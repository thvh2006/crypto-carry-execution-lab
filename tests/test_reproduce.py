import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from carry import market
from carry.reproduce import reproduce, ROOT


class ReproductionTests(unittest.TestCase):
    def test_same_raw_snapshot_keeps_manifest_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw, out = Path(tmp)/'raw', Path(tmp)/'normalized'
            raw.mkdir()
            times = [market.START+i*market.STEP for i in range(3)]
            for symbol in ('BTCUSDT','ETHUSDT'):
                for kind in ('spot','perp','mark','funding'):
                    rows = [dict(fundingTime=t,markPrice='100',fundingRate='.0001') if kind=='funding' else [t,'100','101','99'] for t in times]
                    (raw/f'P3_{symbol}_{kind}_2025.json').write_text(json.dumps(rows))
            with patch.object(market,'END',market.START+3*market.STEP):
                market.normalize(raw,out)
                path=out/'manifest.json';before=path.read_bytes()
                market.normalize(raw,out)
                self.assertEqual(before,path.read_bytes())

    def test_cannot_replace_original_study(self):
        with patch('carry.reproduce.verify',return_value={}):
            with self.assertRaisesRegex(ValueError,'must not replace'):
                reproduce(ROOT/'artifacts/market')
