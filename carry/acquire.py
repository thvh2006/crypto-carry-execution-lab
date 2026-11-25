"""Optional public API acquisition. HTTP 451 stops; no keys or region bypass."""
import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from .market import START, END, STEP, normalize
from .run import ROOT


def request(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 451:
                raise RuntimeError('Provider access restriction (HTTP 451). Stop; use a permitted environment or preserved snapshot.') from exc
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        time.sleep(attempt + 1)
    raise RuntimeError('Acquisition did not complete')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'data/acquired')
    parser.add_argument('--install-equivalent', action='store_true', help='Install only normalized CSVs matching the original frozen hashes')
    args = parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        parser.error('Use a new empty acquisition directory; do not replace an earlier snapshot')
    args.out.mkdir(parents=True, exist_ok=True)
    receipts = []
    for symbol in ('BTCUSDT', 'ETHUSDT'):
        for kind in ('spot', 'perp', 'mark', 'funding'):
            limit = 1000 if kind in ('spot', 'funding') else 1500
            base = 'https://data-api.binance.vision/api/v3/klines' if kind == 'spot' else 'https://fapi.binance.com/fapi/v1/' + {'perp':'klines','mark':'markPriceKlines','funding':'fundingRate'}[kind]
            cursor, page = START, 1
            while cursor < END:
                params = dict(symbol=symbol, startTime=cursor, endTime=END-1, limit=limit)
                if kind != 'funding':
                    params['interval'] = '8h'
                url = base + '?' + urllib.parse.urlencode(params)
                raw = request(url)
                records = json.loads(raw)
                if not isinstance(records, list) or not records:
                    raise ValueError('Missing market page: ' + symbol + ' ' + kind)
                path = args.out / f'P3_{symbol}_{kind}_2025_part{page}.json'
                path.write_bytes(raw)
                receipts.append(dict(file=path.name, url=url, retrieved_at=datetime.now(timezone.utc).isoformat(), sha256=hashlib.sha256(raw).hexdigest(), records=len(records)))
                last = records[-1]['fundingTime'] if kind == 'funding' else records[-1][0]
                next_cursor = last + (1 if kind == 'funding' else STEP)
                if next_cursor <= cursor:
                    raise ValueError('Pagination failed to advance')
                cursor, page = next_cursor, page+1
                if len(records) < limit:
                    break
    (args.out / 'acquisition_receipt.json').write_text(json.dumps(receipts, indent=2))
    candidate = args.out / 'normalized'
    normalize(args.out, candidate)
    freeze = json.loads((ROOT/'artifacts/market/freeze.json').read_text())
    matched = all(hashlib.sha256((candidate/(s+'.csv')).read_bytes()).hexdigest() == freeze['sha256']['data/market/'+s+'.csv'] for s in ('BTCUSDT','ETHUSDT'))
    if args.install_equivalent:
        if not matched:
            raise ValueError('Provider data differ from the frozen snapshot. Preserve candidate for a separately versioned study.')
        target = ROOT / 'data/market'
        target.mkdir(parents=True, exist_ok=True)
        for s in ('BTCUSDT','ETHUSDT'):
            shutil.copyfile(candidate/(s+'.csv'), target/(s+'.csv'))
        # This is the original normalized-data provenance, not a new acquisition claim.
        # New raw byte receipts remain separately under --out.
        shutil.copyfile(ROOT/'artifacts/market/data_audit.json', target/'manifest.json')
    print(json.dumps(dict(normalized_csvs_match_original=matched, installed=args.install_equivalent, receipts=len(receipts)), indent=2))


if __name__ == '__main__':
    main()
