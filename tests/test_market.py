import json
import tempfile
import unittest
from pathlib import Path
from carry.engine import Config, replay
from carry.run import sample
from carry.market import START, STEP, normalize


class TemporalTests(unittest.TestCase):
    def test_extra_delay_leaves_two_empty_events(self):
        rows=sample('BTCUSDT')[:8]
        ledger,fills=replay(rows,Config(),'continuous',delay_events=2)
        self.assertEqual(ledger[0]['spot_qty'],0)
        self.assertEqual(ledger[1]['spot_qty'],0)
        self.assertEqual(fills[0]['timestamp'],rows[2]['timestamp'])

    def test_forecast_changes_signal_not_settlement_cash(self):
        rows=sample('BTCUSDT')[:8]
        for r in rows:r['signal_funding']=-1
        ledger,fills=replay(rows,Config(),'threshold')
        self.assertEqual(fills,[])
        self.assertEqual(ledger[-1]['funding_total'],0)
        rows[0]['signal_funding']=1
        ledger,fills=replay(rows,Config(),'threshold')
        self.assertEqual(ledger[1]['funding_cash'],0)
        self.assertNotEqual(ledger[2]['funding_cash'],0)

    def test_adapter_rejects_missing_or_duplicate_grid(self):
        for times in ([START],[START,START]):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                for kind in ('spot','perp','mark','funding'):
                    records=[dict(fundingTime=t,fundingRate='.0001',markPrice='100') if kind=='funding' else [t,'100','101','99'] for t in times]
                    (root/f'P3_BTCUSDT_{kind}_2025.json').write_text(json.dumps(records))
                with self.assertRaisesRegex(ValueError,'Missing, duplicate'):
                    normalize(root,root/'out')
