"""Auditable official Binance snapshots -> settlement-level research inputs.

No keys, account endpoints or trading operations. Raw snapshots stay private.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .run import ROOT, write_csv
from .engine import validate_rows

START, END, STEP = 1735689600000, 1767225600000, 28800000


def source_urls(symbol):
    common = f'symbol={symbol}&interval=8h&startTime={START}&endTime={END-1}'
    return [f'https://data-api.binance.vision/api/v3/klines?{common}&limit=1000',
            f'https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=8h&startTime={START+1000*STEP}&endTime={END-1}&limit=1000',
            f'https://fapi.binance.com/fapi/v1/klines?{common}&limit=1500',
            f'https://fapi.binance.com/fapi/v1/markPriceKlines?{common}&limit=1500',
            f'https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&startTime={START}&endTime={END-1}&limit=1000',
            f'https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&startTime=1764460800004&endTime={END-1}&limit=1000']


def normalize(raw_dir, out):
    out.mkdir(parents=True, exist_ok=True)
    audit, hashes = [], {}
    expected = list(range(START, END, STEP))
    for symbol in ('BTCUSDT', 'ETHUSDT'):
        def load(kind):
            files = sorted(raw_dir.glob(f'P3_{symbol}_{kind}_2025*.json'))
            if not files:
                raise ValueError('Missing raw stream '+symbol+' '+kind)
            records = []
            for f in files:
                hashes[f.name] = hashlib.sha256(f.read_bytes()).hexdigest()
                records.extend(json.loads(f.read_text()))
            return records
        streams = {k: load(k) for k in ('spot','perp','mark','funding')}
        maps = {}
        for kind, records in streams.items():
            times = [r['fundingTime'] if kind == 'funding' else r[0] for r in records]
            nominal = [round(t/STEP)*STEP if kind == 'funding' else t for t in times]
            if len(nominal) != len(set(nominal)) or sorted(nominal) != expected:
                raise ValueError('Missing, duplicate or out-of-range observations '+symbol+' '+kind)
            maps[kind] = dict(zip(nominal, records))
        rows = []
        for t in expected:
            fund = maps['funding'][t]
            actual = fund['fundingTime']
            if not 0 <= actual-t <= 60000:
                raise ValueError('Unexpected funding timestamp offset')
            previous = rows[-1]['funding_time_ms'] if rows else actual-STEP
            spot, perp, mark = [maps[k][t] for k in ('spot','perp','mark')]
            for bar in (spot, perp, mark):
                if not float(bar[3]) <= float(bar[1]) <= float(bar[2]):
                    raise ValueError('Invalid OHLC bar')
            rows.append(dict(timestamp=datetime.fromtimestamp(actual/1000,timezone.utc).isoformat().replace('+00:00','Z'),
                symbol=symbol,spot=float(spot[1]),perp=float(perp[1]),mark=float(fund['markPrice']),
                funding=float(fund['fundingRate']),elapsed_hours=(actual-previous)/3600000,
                spot_fill=1.0,perp_fill=1.0,funding_time_ms=actual,bar_open_ms=t,
                mark_high=float(mark[2]),mark_low=float(mark[3]),quote_age_ms=actual-t))
        validate_rows(rows)
        write_csv(out/(symbol+'.csv'),rows)
        audit.append(dict(symbol=symbol,events=len(rows),first=rows[0]['timestamp'],last=rows[-1]['timestamp'],
            missing=0,duplicates=0,max_quote_age_ms=max(r['quote_age_ms'] for r in rows),
            negative_funding=sum(r['funding']<0 for r in rows),zero_funding=sum(r['funding']==0 for r in rows)))
    manifest = dict(kind='market',source_urls=sum([source_urls(s) for s in ('BTCUSDT','ETHUSDT')],[]),
        funding_coverage_verified=True,timestamp_alignment_verified=True,rights_reviewed=True,
        contract_specs_reviewed=True,rights_scope='Private research copy; raw and normalized data excluded from public source release. No redistribution license asserted.',
        contract_scope='Linear USDT perpetual, current exchangeInfo corroboration only. Historical fees, margin, minimum order and fills are assumptions; not venue certification.',
        timestamp_method='Actual funding milliseconds; matched nominal 8h bar OPEN, not close. Bar open is up to milliseconds stale; fills are hypothetical with slippage. Signal executes at least one later settlement.',
        assumptions='Flat 1% maintenance plus 10bps close reserve, 10% initial margin, 10/5bps spot/perp fees, 2bps each fill; 0.001 base-unit common quantity step.',
        source_sha256=hashes,coverage=audit,retrieved_at=datetime.now(timezone.utc).isoformat())
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    return manifest


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,default=ROOT/'data/raw');p.add_argument('--out',type=Path,default=ROOT/'data/market')
    args=p.parse_args();print(json.dumps(normalize(args.raw,args.out)['coverage'],indent=2))
