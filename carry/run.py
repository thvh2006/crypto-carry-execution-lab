import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
import subprocess
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .engine import Account, Config, replay, stress_case, validate_rows

ROOT = Path(__file__).resolve().parents[1]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def sample(symbol):
    rng = random.Random(3 if symbol == "BTCUSDT" else 4)
    spot = 60000 if symbol == "BTCUSDT" else 3000
    rows = []
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    for i in range(270):
        spot *= math.exp(rng.gauss(0, 0.012))
        basis = 0.0015 + 0.002 * math.sin(i / 11)
        perp = spot * (1 + basis)
        rows.append({"timestamp": (start + timedelta(hours=8 * i)).isoformat().replace("+00:00", "Z"),
                     "symbol": symbol, "spot": spot, "perp": perp, "mark": perp * (1 + rng.gauss(0, 0.0001)),
                     "funding": 0.0001 + 0.0002 * math.sin(i / 18), "elapsed_hours": 8.0,
                     "spot_fill": 0.6 if 80 <= i < 84 else 1.0,
                     "perp_fill": 0.0 if i == 80 else 1.0})
    return rows


def forecast_comparison(rows):
    predictions = []
    history = []
    variance = 0.0
    for i, row in enumerate(rows):
        if len(history) >= 24:
            training = history[-90:]
            xs, ys = training[:-1], training[1:]
            mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
            scale = statistics.pstdev(xs) or 1.0
            standardized = [(x - mean_x) / scale for x in xs]
            beta = sum(x * (y - mean_y) for x, y in zip(standardized, ys)) / (sum(x * x for x in standardized) + len(xs))
            predicted = {"last_rate": history[-1], "rolling_mean": statistics.mean(training[-9:]),
                         "ridge_ar1": mean_y + beta * (history[-1] - mean_x) / scale}
            for model, value in predicted.items():
                predictions.append({"timestamp": row["timestamp"], "model": model, "prediction": value,
                                    "actual": row["funding"], "absolute_error": abs(value - row["funding"]),
                                    "squared_error": (value - row["funding"]) ** 2,
                                    "training_end": rows[i - 1]["timestamp"],
                                    "ewma_vol_per_observation": math.sqrt(variance)})
        if i:
            log_return = math.log(row["spot"] / rows[i - 1]["spot"])
            variance = 0.94 * variance + 0.06 * log_return ** 2
        history.append(row["funding"])
    return predictions


def summarize(ledger, initial_capital=100000.0):
    first_equity = initial_capital
    peak = first_equity
    maximum_drawdown = 0.0
    for row in ledger:
        peak = max(peak, row["equity"])
        maximum_drawdown = min(maximum_drawdown, row["equity"] / peak - 1)
    last = ledger[-1]
    return {"symbol": last["symbol"], "policy": last["policy"], "net_pnl": last["net_pnl"],
            "return_on_total_capital": last["net_pnl"] / first_equity,
            "funding": last["funding_total"], "spot_pnl": last["spot_pnl"], "perp_pnl": last["perp_pnl"],
            "fees": last["fees_total"], "slippage_embedded_in_leg_pnl": last["slippage_total"],
            "max_drawdown": maximum_drawdown, "max_abs_delta_usdt": max(abs(r["residual_delta_usdt"]) for r in ledger),
            "halted": any(r["halted"] for r in ledger),
            "max_reconciliation_error": max(abs(r["reconciliation_error"]) for r in ledger)}


def load_rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    numeric = ("spot", "perp", "mark", "funding", "spot_fill", "perp_fill", "elapsed_hours")
    return [dict(row, **{name: float(row[name]) for name in numeric}) for row in rows]


def golden_case():
    account = Account(Config(slippage_bps=0))
    row = {"timestamp": "2025-01-01T00:00:00Z", "symbol": "BTCUSDT", "spot": 100, "perp": 100, "mark": 100}
    account.trade_spot(275, row)
    account.trade_perp(-550, row)
    for mark, rate in ((100, 0.001), (102, -0.002), (105, 0.001)):
        account.settle(dict(row, mark=mark, funding=rate), 0)
    delta = account.spot_qty + account.perp_qty
    account.trade_perp(550, dict(row, perp=105))
    account.trade_spot(-275, row)
    equity = account.equity(100, 105)
    return {"pnl": equity - 100000, "equity": equity, "funding": account.funding, "delta": delta}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["demo", "market"])
    parser.add_argument("--data", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/demo")
    args = parser.parse_args()
    config = Config()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.mode == "market":
        if args.data is None:
            parser.error("market requires --data DIRECTORY")
        manifest = json.loads((args.data / "manifest.json").read_text())
        if manifest.get("kind") != "market" or not manifest.get("source_urls"):
            parser.error("Market manifest must identify kind and source_urls")
        required = ("funding_coverage_verified", "timestamp_alignment_verified", "rights_reviewed", "contract_specs_reviewed")
        if any(manifest.get(key) is not True for key in required):
            parser.error("Complete source, funding, timestamp and contract audit first")
        status = "MARKET DEVELOPMENT REPLAY — sampled execution and approximate margin"
    else:
        status = "SYNTHETIC VALIDATION — historical market study pending"
    all_ledgers, all_fills, summary, forecasts, sensitivity = [], [], [], [], []
    input_hashes = {}
    for symbol in ("BTCUSDT", "ETHUSDT"):
        if args.mode == "demo":
            rows = sample(symbol)
            path = args.out / (symbol + "_synthetic.csv")
            write_csv(path, rows)
        else:
            path = args.data / (symbol + ".csv")
            rows = load_rows(path)
        input_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        validate_rows(rows)
        if any(row["symbol"] != symbol for row in rows):
            parser.error("Symbol column disagrees with the instrument filename")
        if len(rows) < 25:
            parser.error("At least 25 events are required for forecast comparison")
        forecasts.extend(dict(row, symbol=symbol) for row in forecast_comparison(rows))
        for policy in ("spot", "continuous", "threshold"):
            ledger, fills = replay(rows, config, policy)
            all_ledgers.extend(ledger)
            all_fills.extend(dict(fill, policy=policy) for fill in fills)
            summary.append(summarize(ledger))
            for multiplier in (1, 2, 3):
                stress_config = replace(config, spot_fee_bps=config.spot_fee_bps * multiplier,
                                        perp_fee_bps=config.perp_fee_bps * multiplier,
                                        slippage_bps=config.slippage_bps * multiplier)
                stressed, _ = replay(rows, stress_config, policy)
                sensitivity.append(dict(summarize(stressed), cost_multiple=multiplier))
    scenarios = {
        "flat_negative_funding": {},
        "basis_widens": {"perp_shock": 0.05},
        "joint_price_rally": {"spot_shock": 0.8, "perp_shock": 0.8},
        "spot_partial_fill": {"spot_fill": 0.5, "spot_shock": -0.2, "perp_shock": -0.2},
        "maintenance_increase": {"maintenance_rate": 0.05, "perp_shock": 0.1},
        "collateral_haircut": {"collateral_haircut": 0.5, "perp_shock": 0.1},
        "stablecoin_depeg": {"stablecoin_usd": 0.9},
    }
    stress = [dict(scenario=name, **stress_case(**kwargs)) for name, kwargs in scenarios.items()]
    write_csv(args.out / "ledger.csv", all_ledgers)
    write_csv(args.out / "trades.csv", all_fills)
    write_csv(args.out / "summary.csv", summary)
    write_csv(args.out / "forecast_comparison.csv", forecasts)
    write_csv(args.out / "cost_sensitivity.csv", sensitivity)
    write_csv(args.out / "stress.csv", stress)
    config_json = json.dumps(asdict(config), sort_keys=True)
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL, text=True).strip()
    except subprocess.CalledProcessError:
        commit = None
    receipt = {"run_id": hashlib.sha256((config_json + json.dumps(input_hashes, sort_keys=True)).encode()).hexdigest()[:16],
               "status": status, "as_of": max(r["timestamp"] for r in all_ledgers),
               "published_at": datetime.now(timezone.utc).isoformat(), "commit_sha": commit,
               "config": asdict(config), "config_sha256": hashlib.sha256(config_json.encode()).hexdigest(),
               "input_sha256": input_hashes, "python": platform.python_version(),
               "model_version": "0.1.0", "validation": "ledger reconciled each event",
               "market_data_access": "DNS failure" if args.mode == "demo" else "user-supplied audited snapshot"}
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    (args.out / "golden.json").write_text(json.dumps(golden_case(), indent=2))
    (args.out / "dashboard_data.json").write_text(json.dumps({"receipt": receipt, "summary": summary, "stress": stress,
                                                           "ledger": all_ledgers}, separators=(",", ":")))
    from .web import build_dashboard
    build_dashboard(args.out)
    print(json.dumps({"status": status, "run_id": receipt["run_id"], "ledger_rows": len(all_ledgers), "trades": len(all_fills)}))


if __name__ == "__main__":
    main()
