import unittest
from dataclasses import replace

from carry.engine import Account, Config, replay, stress_case, validate_rows
from carry.run import sample, forecast_comparison


def flat_rows(rate=0.001):
    return [{"timestamp": f"2025-01-01T{hour:02d}:00:00Z", "symbol": "BTCUSDT",
             "spot": 100.0, "perp": 100.0, "mark": 100.0, "funding": rate,
             "elapsed_hours": 8.0, "spot_fill": 1.0, "perp_fill": 1.0} for hour in (0, 8, 16)]


class EconomicTests(unittest.TestCase):
    def setUp(self):
        self.config = Config(spot_fee_bps=0, perp_fee_bps=0, slippage_bps=0)

    def test_hand_worked_funding_and_timing(self):
        ledger, _ = replay(flat_rows(), self.config, "continuous")
        # Decide at 00, fill at 08 after settlement, receive one payment at 16.
        self.assertEqual(ledger[0]["funding_total"], 0)
        self.assertEqual(ledger[1]["funding_total"], 0)
        self.assertAlmostEqual(ledger[-1]["net_pnl"], 55)
        self.assertAlmostEqual(ledger[-1]["equity"], 100055)

    def test_negative_funding_short_pays(self):
        ledger, _ = replay(flat_rows(-0.001), self.config, "continuous")
        self.assertAlmostEqual(ledger[-1]["net_pnl"], -55)

    def test_all_four_commissions(self):
        config = replace(self.config, spot_fee_bps=10, perp_fee_bps=5)
        ledger, trades = replay(flat_rows(0), config, "continuous")
        self.assertEqual(len(trades), 4)
        self.assertAlmostEqual(ledger[-1]["fees_total"], 165)
        self.assertAlmostEqual(ledger[-1]["net_pnl"], -165)

    def test_partial_execution_leaves_delta(self):
        rows = flat_rows(0)
        rows[1]["perp_fill"] = 0.5
        ledger, _ = replay(rows, self.config, "continuous")
        self.assertAlmostEqual(ledger[1]["residual_delta_units"], 275)

    def test_basis_loss_with_constant_spot(self):
        rows = flat_rows(0)
        rows[-1].update(perp=105, mark=105)
        ledger, _ = replay(rows, self.config, "continuous")
        self.assertAlmostEqual(ledger[-1]["net_pnl"], -2750)

    def test_collateral_transfer_is_not_profit(self):
        account = Account(self.config)
        before = account.equity(100, 100)
        account.spot_cash -= 1000
        account.collateral += 1000
        self.assertEqual(account.equity(100, 100), before)

    def test_margin_failure_stops_entries(self):
        rows = flat_rows(0)
        rows[-1].update(spot=200, perp=200, mark=200)
        ledger, _ = replay(rows, self.config, "continuous")
        self.assertTrue(ledger[-1]["halted"])
        self.assertEqual(ledger[-1]["perp_qty"], 0)
        self.assertLess(ledger[-1]["collateral"], 0)

    def test_future_changes_preserve_prior_orders(self):
        rows = sample("BTCUSDT")
        cutoff = 100
        altered = [dict(row) for row in rows]
        for row in altered[cutoff:]:
            row.update(funding=-0.01, spot=row["spot"] * 1.5)
        first, _ = replay(rows, self.config)
        second, _ = replay(altered, self.config)
        self.assertEqual(first[:cutoff], second[:cutoff])

    def test_current_rate_never_changes_same_event_fill(self):
        rows = flat_rows(0.001)
        changed = [dict(row) for row in rows]
        changed[1]["funding"] = -0.01
        a, _ = replay(rows, self.config, close_at_end=False)
        b, _ = replay(changed, self.config, close_at_end=False)
        self.assertEqual(a[1]["spot_qty"], b[1]["spot_qty"])
        self.assertEqual(a[1]["perp_qty"], b[1]["perp_qty"])

    def test_forecasts_use_only_previous_settlements(self):
        rows = sample("ETHUSDT")
        first = forecast_comparison(rows)
        changed = [dict(row) for row in rows]
        changed[30]["funding"] = 0.5
        second = forecast_comparison(changed)
        self.assertEqual([r["prediction"] for r in first if r["timestamp"] == rows[30]["timestamp"]],
                         [r["prediction"] for r in second if r["timestamp"] == rows[30]["timestamp"]])

    def test_reconciliation_and_nonnegative_fee(self):
        for policy in ("spot", "continuous", "threshold"):
            ledger, trades = replay(sample("BTCUSDT"), Config(), policy)
            self.assertLess(max(abs(row["reconciliation_error"]) for row in ledger), 1e-6)
            self.assertTrue(all(row["fee"] >= 0 for row in trades))

    def test_missing_or_duplicate_event_rejected(self):
        rows = flat_rows()
        rows[1]["timestamp"] = rows[0]["timestamp"]
        with self.assertRaises(ValueError):
            validate_rows(rows)
        rows = flat_rows()
        rows[-1]["elapsed_hours"] = 4
        with self.assertRaises(ValueError):
            validate_rows(rows)

    def test_margin_can_fail_while_combined_capital_survives(self):
        result = stress_case(spot_shock=0.8, perp_shock=0.8)
        self.assertGreater(result["equity_usdt"], 99000)
        self.assertLess(result["margin_buffer_after_haircut"], 0)


if __name__ == "__main__":
    unittest.main()
