import unittest
from carry.paper import step


class PaperTests(unittest.TestCase):
    def test_first_snapshot_cannot_claim_old_funding(self):
        row=dict(timestamp='2026-11-24T00:00:00Z',symbol='BTCUSDT',spot=100,perp=100,mark=100,funding=.001,observed_ms=1000000)
        funds=[dict(fundingTime=900000,fundingRate='.001',markPrice='100')]
        first=step(None,row,funds)
        self.assertEqual(first['receipt']['net_pnl'],0)
        self.assertEqual(first['receipt']['modeled_fills'],0)
        second=step(first,dict(row,observed_ms=1400000),funds)
        self.assertGreater(second['receipt']['modeled_fills'],0)
        self.assertEqual(second['receipt']['funding_total'],0)
        funds.append(dict(fundingTime=29700000,fundingRate='-.001',markPrice='100'))
        third=step(second,dict(row,observed_ms=30000000),funds)
        self.assertLess(third['receipt']['funding_total'],0)

    def test_duplicate_observation_rejected(self):
        row=dict(timestamp='2026-11-24T00:00:00Z',symbol='BTCUSDT',spot=100,perp=100,mark=100,funding=.001,observed_ms=1000000)
        funds=[dict(fundingTime=900000,fundingRate='.001',markPrice='100')]
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            step(step(None,row,funds),row,funds)
