"""Event replay with separate spot cash and isolated derivatives collateral.

At each timestamp, mark and settle funding on old holdings, check margin,
execute the previous decision, then make the next decision. No live orders.
"""
import math
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Config:
    capital: float = 100000.0
    spot_wallet_fraction: float = 0.65
    allocation_fraction: float = 0.55
    spot_fee_bps: float = 10.0
    perp_fee_bps: float = 5.0
    slippage_bps: float = 2.0
    maintenance_rate: float = 0.01
    close_reserve_bps: float = 10.0
    funding_threshold: float = 0.00005
    quantity_step: float = 0.0001
    initial_margin_rate: float = 0.1
    financing_apr: float = 0.0

    def validate(self):
        if not all(math.isfinite(value) for value in vars(self).values()):
            raise ValueError("Configuration contains a non-finite value")
        if self.capital <= 0 or self.quantity_step <= 0:
            raise ValueError("Capital and quantity step must be positive")
        if not 0 < self.allocation_fraction < self.spot_wallet_fraction < 1:
            raise ValueError("Allocation must leave capital for costs and collateral")
        if not 0 < self.maintenance_rate < self.initial_margin_rate <= 1:
            raise ValueError("Invalid initial or maintenance margin rates")
        for name in ("spot_fee_bps", "perp_fee_bps", "slippage_bps", "close_reserve_bps", "financing_apr"):
            if getattr(self, name) < 0:
                raise ValueError("Negative cost assumption " + name)
        if self.slippage_bps >= 10000:
            raise ValueError("Slippage must be less than 100%")


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("All timestamps must have UTC offsets")
    return parsed


def validate_rows(rows):
    if len(rows) < 3:
        raise ValueError("At least three observations required")
    previous = None
    symbols = set()
    for row in rows:
        current = timestamp(row["timestamp"])
        if previous is not None and current <= previous:
            raise ValueError("Timestamps must be strictly increasing within each symbol")
        previous = current
        symbols.add(row["symbol"])
        for name in ("spot", "perp", "mark", "funding", "spot_fill", "perp_fill", "elapsed_hours"):
            if not math.isfinite(row[name]):
                raise ValueError("Non-finite input " + name)
        if min(row["spot"], row["perp"], row["mark"], row["elapsed_hours"]) <= 0:
            raise ValueError("Prices and funding interval must be positive")
        if any(not 0 <= row[name] <= 1 for name in ("spot_fill", "perp_fill")):
            raise ValueError("Fill fractions must be between zero and one")
        if abs(row["funding"]) > 1:
            raise ValueError("Funding must be expressed as a decimal per settlement")
    if len(symbols) != 1:
        raise ValueError("Replay one symbol per capital sleeve")
    for old, new in zip(rows, rows[1:]):
        hours = (timestamp(new["timestamp"]) - timestamp(old["timestamp"])).total_seconds() / 3600
        if abs(hours - new["elapsed_hours"]) > 1e-8:
            raise ValueError("Missing event or incorrect elapsed_hours")


class Account:
    def __init__(self, config):
        config.validate()
        self.config = config
        self.spot_cash = config.capital * config.spot_wallet_fraction
        self.collateral = config.capital - self.spot_cash
        self.spot_qty = 0.0
        self.perp_qty = 0.0
        self.entry = 0.0
        self.funding = 0.0
        self.fees = 0.0
        self.slippage = 0.0
        self.financing = 0.0
        self.realized_perp = 0.0
        self.spot_cost = 0.0
        self.realized_spot = 0.0
        self.fills = []

    def perp_unrealized(self, mark):
        return self.perp_qty * (mark - self.entry)

    def equity(self, spot, mark):
        return self.spot_cash + self.spot_qty * spot + self.collateral + self.perp_unrealized(mark)

    def margin_buffer(self, mark):
        notional = abs(self.perp_qty) * mark
        requirement = notional * (self.config.maintenance_rate + self.config.close_reserve_bps / 10000)
        return self.collateral + self.perp_unrealized(mark) - requirement

    def settle(self, row, hours):
        payment = -self.perp_qty * row["mark"] * row["funding"]
        self.collateral += payment
        self.funding += payment
        financing = self.spot_qty * row["spot"] * self.config.financing_apr * hours / (365 * 24)
        self.spot_cash -= financing
        self.financing += financing
        return payment

    def trade_spot(self, delta, row, fraction=1.0):
        config = self.config
        delta *= fraction
        fill_price = row["spot"] * (1 + math.copysign(config.slippage_bps / 10000, delta))
        if delta > 0:
            delta = min(delta, max(0, self.spot_cash) / (fill_price * (1 + config.spot_fee_bps / 10000)))
        delta = math.copysign(math.floor((abs(delta) + 1e-10) / config.quantity_step) * config.quantity_step, delta)
        if abs(delta) < config.quantity_step / 2:
            return
        old_qty = self.spot_qty
        fee = abs(delta * fill_price) * config.spot_fee_bps / 10000
        if delta > 0:
            self.spot_cost = (old_qty * self.spot_cost + delta * fill_price) / (old_qty + delta)
        else:
            self.realized_spot += -delta * (fill_price - self.spot_cost)
        self.spot_qty += delta
        self.spot_cash -= delta * fill_price + fee
        self.record("spot", delta, fill_price, fee, row)

    def trade_perp(self, delta, row, fraction=1.0):
        config = self.config
        delta *= fraction
        delta = math.copysign(math.floor((abs(delta) + 1e-10) / config.quantity_step) * config.quantity_step, delta)
        if abs(delta) < config.quantity_step / 2:
            return
        fill_price = row["perp"] * (1 + math.copysign(config.slippage_bps / 10000, delta))
        old_qty = self.perp_qty
        new_qty = old_qty + delta
        # Strategies only carry a short perp and close it toward zero.
        if new_qty > 1e-8:
            raise ValueError("A carry short cannot cross into a long")
        if delta < 0:
            incremental = abs(delta) * row["mark"] * config.initial_margin_rate
            available = self.collateral + self.perp_unrealized(row["mark"]) - abs(old_qty) * row["mark"] * config.initial_margin_rate
            if incremental > available:
                return
            self.entry = (abs(old_qty) * self.entry + abs(delta) * fill_price) / abs(new_qty)
        else:
            realized = delta * (self.entry - fill_price)
            self.collateral += realized
            self.realized_perp += realized
        self.perp_qty = new_qty
        if abs(new_qty) < 1e-8:
            self.perp_qty = 0.0
            self.entry = 0.0
        fee = abs(delta * fill_price) * config.perp_fee_bps / 10000
        self.collateral -= fee
        self.record("perp", delta, fill_price, fee, row)

    def record(self, leg, delta, price, fee, row):
        reference = row[leg]
        slip = delta * (price - reference)
        self.slippage += slip
        self.fees += fee
        self.fills.append({"timestamp": row["timestamp"], "symbol": row["symbol"], "leg": leg,
                           "quantity": delta, "reference": reference, "fill_price": price,
                           "fee": fee, "slippage_cost": slip})


def replay(rows, config, policy="threshold", close_at_end=True, delay_events=1):
    validate_rows(rows)
    if policy not in ("spot", "continuous", "threshold"):
        raise ValueError("Unknown policy")
    if delay_events < 1:
        raise ValueError("Execution must follow the observation")
    account = Account(config)
    pending = [(0.0, 0.0)] * delay_events
    target_spot = target_perp = 0.0
    ledger = []
    halted = False
    for i, row in enumerate(rows):
        paid = account.settle(row, 0 if i == 0 else row["elapsed_hours"])
        breach = bool(account.perp_qty and account.margin_buffer(row["mark"]) <= 0)
        if breach:
            # Full unwind at sampled prices is a stress approximation.
            # Preserve any deficit and stop all subsequent entries.
            account.trade_perp(-account.perp_qty, row)
            account.trade_spot(-account.spot_qty, row)
            target_spot = target_perp = 0.0
            halted = True
        execute_spot, execute_perp = pending.pop(0)
        if not halted:
            account.trade_spot(execute_spot - account.spot_qty, row, row["spot_fill"])
            account.trade_perp(execute_perp - account.perp_qty, row, row["perp_fill"])
        if close_at_end and i == len(rows) - 1:
            account.trade_perp(-account.perp_qty, row)
            account.trade_spot(-account.spot_qty, row)
        equity = account.equity(row["spot"], row["mark"])
        spot_pnl = account.realized_spot + account.spot_qty * (row["spot"] - account.spot_cost)
        perp_pnl = account.realized_perp + account.perp_unrealized(row["mark"])
        pnl_bridge = spot_pnl + perp_pnl + account.funding - account.fees - account.financing
        residual = equity - config.capital - pnl_bridge
        if abs(residual) > 1e-6:
            raise ArithmeticError("Two-leg P&L reconciliation failed")
        ledger.append({"timestamp": row["timestamp"], "symbol": row["symbol"], "policy": policy,
                       "spot": row["spot"], "perp": row["perp"], "mark": row["mark"],
                       "basis_bps": (row["perp"] / row["spot"] - 1) * 10000,
                       "settled_funding_rate": row["funding"], "funding_cash": paid,
                       "spot_qty": account.spot_qty, "perp_qty": account.perp_qty,
                       "residual_delta_units": account.spot_qty + account.perp_qty,
                       "residual_delta_usdt": (account.spot_qty + account.perp_qty) * row["spot"],
                       "spot_cash": account.spot_cash, "collateral": account.collateral,
                       "perp_unrealized": account.perp_unrealized(row["mark"]),
                       "spot_pnl": spot_pnl, "perp_pnl": perp_pnl,
                       "funding_total": account.funding, "fees_total": account.fees,
                       "slippage_total": account.slippage, "financing_total": account.financing,
                       "equity": equity, "net_pnl": equity - config.capital,
                       "margin_buffer": account.margin_buffer(row["mark"]),
                       "reconciliation_error": residual, "margin_breach": breach, "halted": halted})
        if not halted:
            # Information at row i is first executable at row i+1.
            active = policy != "threshold" or row.get("signal_funding", row["funding"]) >= config.funding_threshold
            if active and target_spot == 0:
                target_spot = math.floor(config.capital * config.allocation_fraction / row["spot"] / config.quantity_step) * config.quantity_step
            if not active:
                target_spot = 0.0
            target_perp = -target_spot if policy != "spot" else 0.0
        pending.append((target_spot, target_perp))
    return ledger, account.fills


def stress_case(spot_shock=0.0, perp_shock=0.0, funding_rate=-0.001,
                spot_fill=1.0, maintenance_rate=0.01, collateral_haircut=0.0, stablecoin_usd=1.0):
    config = Config(maintenance_rate=maintenance_rate, initial_margin_rate=max(0.1, maintenance_rate + 0.01))
    account = Account(config)
    opening = {"timestamp": "2025-01-01T00:00:00Z", "symbol": "BTCUSDT", "spot": 100.0, "perp": 100.0, "mark": 100.0}
    quantity = config.capital * config.allocation_fraction / opening["spot"]
    account.trade_spot(quantity, opening, spot_fill)
    account.trade_perp(-quantity, opening)
    end = dict(opening, spot=100 * (1 + spot_shock), perp=100 * (1 + perp_shock),
               mark=100 * (1 + perp_shock), funding=funding_rate)
    account.settle(end, 8)
    equity = account.equity(end["spot"], end["mark"])
    haircut = account.collateral * collateral_haircut
    return {"equity_usdt": equity, "economic_pnl_usdt": equity - config.capital,
            "equity_usd_after_depeg": equity * stablecoin_usd,
            "margin_buffer_after_haircut": account.margin_buffer(end["mark"]) - haircut,
            "residual_delta_units": account.spot_qty + account.perp_qty,
            "additional_collateral_required": max(0, haircut - account.margin_buffer(end["mark"]))}
