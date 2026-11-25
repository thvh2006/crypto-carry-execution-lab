"""Frozen retrospective partitions, matched forecasts and net-economics study."""
import hashlib
import json
import random
import statistics
from collections import defaultdict
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from .engine import Config, replay
from .run import ROOT, load_rows, forecast_comparison, summarize, write_csv

PARTITIONS={'development':('2025-01-01','2025-07-01'), 'validation':('2025-07-01','2025-10-01'), 'holdout':('2025-10-01','2026-01-01')}


def paired_interval(a,b):
    daily=defaultdict(float)
    olda=oldb=0.0
    for x,y in zip(a,b):
        assert x['timestamp']==y['timestamp']
        daily[x['timestamp'][:10]]+=(x['net_pnl']-olda)-(y['net_pnl']-oldb)
        olda,oldb=x['net_pnl'],y['net_pnl']
    values=list(daily.values()); n=len(values); rng=random.Random(20261124)
    simulations=[]
    for _ in range(2000):
        resampled=[]
        while len(resampled)<n:
            start=rng.randrange(max(1,n-6))
            resampled.extend(values[start:start+7])
        simulations.append(sum(resampled[:n]))
    simulations.sort()
    return dict(paired_pnl_difference=sum(values),block_bootstrap_low=simulations[49],block_bootstrap_high=simulations[1949],days=n,block_days=7,replications=2000,seed=20261124)


def chart(ledgers, path):
    colors=['#526779','#137c66','#d97a37','#6d57a6','#a64368','#1d88a8']
    policy=list(ledgers); vals=[r['net_pnl'] for rows in ledgers.values() for r in rows]+[0]
    lo,hi=min(vals),max(vals);span=hi-lo or 1
    lines=[]
    for k,color in zip(policy,colors):
        rows=ledgers[k]
        pts=' '.join(f'{65+i*790/max(1,len(rows)-1):.1f},{350-(r["net_pnl"]-lo)*270/span:.1f}' for i,r in enumerate(rows))
        lines.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/><text x="{65+policy.index(k)%3*270}" y="{405+policy.index(k)//3*22}" fill="{color}">{k}</text>')
    path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="920" height="465" viewBox="0 0 920 465"><rect width="920" height="465" fill="#faf8f4"/><g font-family="Arial" font-size="13" fill="#243c45"><text x="50" y="30" font-size="20">{path.stem} — net P&amp;L / 100,000 USDT sleeve</text><text x="5" y="85">{hi:,.0f}</text><text x="5" y="350">{lo:,.0f}</text><path d="M65 70 V350 H860" fill="none" stroke="#b6c6c8"/>{"".join(lines)}<text x="65" y="375">{next(iter(ledgers.values()))[0]["timestamp"][:10]}</text><text x="775" y="375">{next(iter(ledgers.values()))[-1]["timestamp"][:10]}</text></g></svg>')


def main():
    # Preserve the consumed study. Rebuild through its immutable source snapshot.
    if (ROOT/'artifacts/market/frozen_source/carry/study.py').exists():
        from .reproduce import main as reproduce_main
        return reproduce_main()
    out=ROOT/'artifacts/market';out.mkdir(parents=True,exist_ok=True)
    config=Config(quantity_step=.001)
    frozen_files=[ROOT/'carry'/name for name in ('engine.py','market.py','study.py','run.py')]+list((ROOT/'data/market').glob('*'))+[ROOT/'docs/STUDY_PROTOCOL_V1.md']
    freeze=dict(frozen_at=datetime.now(timezone.utc).isoformat(),config=asdict(config),
                scope='Retrospective historical holdout; freeze before first strategy return inspection. No forward claim.',
                sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen_files})
    freeze_path=out/'freeze.json'
    if freeze_path.exists():
        old=json.loads(freeze_path.read_text())
        if old['sha256']!=freeze['sha256'] or old['config']!=freeze['config']:
            raise ValueError('Frozen study changed. Record amendment and new study version before rerun.')
    else:
        freeze_path.write_text(json.dumps(freeze,indent=2))
    summaries=[];costs=[];delays=[];intervals=[];errors=[];all_ledger=[];all_fills=[]
    for symbol in ('BTCUSDT','ETHUSDT'):
        full=load_rows(ROOT/'data/market'/(symbol+'.csv'))
        forecasts=forecast_comparison(full)
        predictions={(r['timestamp'],r['model']):r['prediction'] for r in forecasts}
        for partition,(start,end) in PARTITIONS.items():
            indexes=[i for i,r in enumerate(full) if start<=r['timestamp'][:10]<end]
            rows=[full[i] for i in indexes]; results={}
            cases={name:rows for name in ('spot','continuous','threshold')}
            for model in ('last_rate','rolling_mean','ridge_ar1'):
                # Decision after settlement i predicts settlement i+1 using data through i.
                cases['forecast_'+model]=[dict(full[i],signal_funding=predictions.get((full[i+1]['timestamp'],model),-1) if i+1<len(full) else -1) for i in indexes]
                values=[r for r in forecasts if r['model']==model and start<=r['timestamp'][:10]<end]
                errors.append(dict(symbol=symbol,partition=partition,model=model,n=len(values),mae=statistics.mean(r['absolute_error'] for r in values),rmse=statistics.mean(r['squared_error'] for r in values)**.5))
            for name,inputs in cases.items():
                policy=name if name in ('spot','continuous','threshold') else 'threshold'
                ledger,fills=replay(inputs,config,policy)
                for r in ledger:r['policy']=name
                results[name]=ledger
                # A short's worst mark in each following bar, using its post-trade holdings.
                # Diagnostic only: no claim about the ordering/path of high versus cash flows.
                buffers=[r['collateral']+r['perp_qty']*(float(src['mark_high'])-r['mark'])+r['perp_unrealized']-abs(r['perp_qty'])*float(src['mark_high'])*.011 for r,src in zip(ledger,inputs) if r['perp_qty']]
                summaries.append(dict(partition=partition,**summarize(ledger),events=len(rows),
                    minimum_sampled_margin_buffer=min((r['margin_buffer'] for r in ledger if r['perp_qty']),default=0),
                    minimum_bar_high_margin_proxy=min(buffers,default=0),trade_fills=len(fills)))
                all_ledger.extend(dict(r,partition=partition) for r in ledger)
                all_fills.extend(dict(r,partition=partition,policy=name) for r in fills)
                for multiple in (1,2,3):
                    cfg=replace(config,spot_fee_bps=10*multiple,perp_fee_bps=5*multiple,slippage_bps=2*multiple)
                    stress,_=replay(inputs,cfg,policy)
                    costs.append(dict(symbol=symbol,partition=partition,policy=name,cost_multiple=multiple,net_pnl=stress[-1]['net_pnl']))
                for delay in (1,2,3):
                    stress,_=replay(inputs,config,policy,delay_events=delay)
                    delays.append(dict(symbol=symbol,partition=partition,policy=name,delay_events=delay,net_pnl=stress[-1]['net_pnl']))
            for name,benchmark in [('threshold','continuous'),('forecast_rolling_mean','forecast_last_rate'),('forecast_ridge_ar1','forecast_last_rate')]:
                intervals.append(dict(symbol=symbol,partition=partition,policy=name,benchmark=benchmark,**paired_interval(results[name],results[benchmark])))
            chart(results,out/(symbol+'_'+partition+'.svg'))
    for name,values in [('summary',summaries),('cost_sensitivity',costs),('delay_sensitivity',delays),('paired_uncertainty',intervals),('forecast_errors',errors),('ledger',all_ledger),('trades',all_fills)]:
        write_csv(out/(name+'.csv'),values)
    receipt=dict(run_id=hashlib.sha256(json.dumps(freeze['sha256'],sort_keys=True).encode()).hexdigest()[:16],status='RETROSPECTIVE MARKET STUDY — hypothetical sampled fills',config=asdict(config),as_of=all_ledger[-1]['timestamp'],published_at=datetime.now(timezone.utc).isoformat(),freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),partitions=PARTITIONS,validation='Reconciled every event; no live orders',model_version='0.2.0')
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    # Dashboard's time-series source is the holdout. Partition-level results remain in CSV/report.
    stress=json.loads((ROOT/'artifacts/demo/dashboard_data.json').read_text())['stress']
    payload=dict(receipt=receipt,summary=[r for r in summaries if r['partition']=='holdout' and r['policy'] in ('spot','continuous','threshold')],stress=stress,ledger=[r for r in all_ledger if r['partition']=='holdout' and r['policy'] in ('spot','continuous','threshold')])
    (out/'dashboard_data.json').write_text(json.dumps(payload,separators=(',',':')))
    from .web import build_dashboard
    build_dashboard(out)
    print(json.dumps(dict(run_id=receipt['run_id'],ledger_rows=len(all_ledger),fills=len(all_fills),max_reconciliation_error=max(abs(r['reconciliation_error']) for r in all_ledger))))


if __name__=='__main__':main()
