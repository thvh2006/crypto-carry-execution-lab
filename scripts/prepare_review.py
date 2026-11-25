"""Derived research diagnostics. No strategy tuning or changes to frozen returns."""
import csv,json,math,statistics,hashlib
from collections import defaultdict
from pathlib import Path
from carry.run import ROOT,load_rows,write_csv

OUT=ROOT/'artifacts/review';OUT.mkdir(exist_ok=True)
def read(name):
 with (ROOT/'artifacts/market'/(name+'.csv')).open() as f:return list(csv.DictReader(f))
def quantile(values,p):
 x=sorted(values);z=(len(x)-1)*p;i=int(z);return x[i]+(x[min(i+1,len(x)-1)]-x[i])*(z-i)
def correlation(x,y):
 ax,ay=statistics.mean(x),statistics.mean(y);a=[v-ax for v in x];b=[v-ay for v in y]
 den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b));return sum(u*v for u,v in zip(a,b))/den if den else 0

def main():
 summary=read('summary');cost=read('cost_sensitivity');delay=read('delay_sensitivity');ledger=read('ledger');trades=read('trades')
 groups=defaultdict(list);history=[];offsets={};turnover=[]
 for r in ledger:groups[(r['symbol'],r['partition'],r['policy'])].append(r)
 for key,rows in groups.items():
  offsets['|'.join(key)]=len(history);peak=100000
  for r in rows:
   peak=max(peak,float(r['equity']));history.append(['|'.join(key),r['timestamp'][:19].replace('T',' '),*[float(r[k]) for k in ('net_pnl','spot_pnl','perp_pnl','funding_total','fees_total','financing_total','residual_delta_usdt','margin_buffer')],float(r['equity'])/peak-1])
 for r in summary:
  key=(r['symbol'],r['partition'],r['policy']);fills=[x for x in trades if tuple(x[k] for k in ('symbol','partition','policy'))==key]
  notional=sum(abs(float(x['quantity'])*float(x['fill_price'])) for x in fills)
  rows=groups[key];active=sum(abs(float(x['perp_qty']))>0 for x in rows)
  turnover.append(dict(symbol=key[0],partition=key[1],policy=key[2],fills=len(fills),two_leg_traded_notional=notional,turnover_over_capital=notional/100000,active_perp_events=active,events=len(rows),funding=float(r['funding']),fees=float(r['fees'])))
 distributions=[];regimes=[];histograms=[]
 for symbol in ('BTCUSDT','ETHUSDT'):
  rows=load_rows(ROOT/'data/market'/(symbol+'.csv'));rates=[r['funding']*10000 for r in rows];basis=[(r['perp']/r['spot']-1)*10000 for r in rows]
  run=longest=0
  for v in rates:run=run+1 if v<0 else 0;longest=max(longest,run)
  distributions.append(dict(symbol=symbol,n=len(rows),funding_mean_bps=statistics.mean(rates),funding_p05_bps=quantile(rates,.05),funding_median_bps=statistics.median(rates),funding_p95_bps=quantile(rates,.95),negative_fraction=sum(v<0 for v in rates)/len(rates),longest_negative_run=longest,funding_lag1_correlation=correlation(rates[:-1],rates[1:]),basis_median_bps=statistics.median(basis),basis_p05_bps=quantile(basis,.05),basis_p95_bps=quantile(basis,.95),funding_basis_correlation=correlation(rates,basis)))
  for month in sorted({r['timestamp'][:7] for r in rows}):
   rs=[r for r in rows if r['timestamp'].startswith(month)];regimes.append(dict(symbol=symbol,month=month,n=len(rs),mean_funding_bps=statistics.mean(r['funding']*10000 for r in rs),negative_fraction=sum(r['funding']<0 for r in rs)/len(rs),mean_basis_bps=statistics.mean((r['perp']/r['spot']-1)*10000 for r in rs)))
  for a,b in [(-100,-1),(-1,0),(0,.5),(.5,1),(1,100)]:histograms.append(dict(symbol=symbol,bin=f'{a:g} to {b:g}',count=sum(a<=v<b for v in rates)))
 for name,data in [('turnover',turnover),('funding_diagnostics',distributions),('monthly_regimes',regimes),('funding_histogram',histograms)]:write_csv(OUT/(name+'.csv'),data)
 # Explicit workbook source fields. All market records here are derived results.
 source=[]
 for r in summary:
  key='|'.join(r[k] for k in ('symbol','partition','policy'))
  source.append([key,r['symbol'],r['partition'],r['policy'],*[float(r[k]) for k in ('net_pnl','funding','spot_pnl','perp_pnl','fees','return_on_total_capital','max_drawdown','trade_fills')],offsets[key],int(r['events']),float(r['minimum_sampled_margin_buffer'])])
 payload=dict(summary=source,history=history,cost=cost,delay=delay,turnover=turnover,diagnostics=distributions,regimes=regimes,histogram=histograms,run_id='eed008040d6c6d18')
 (OUT/'workbook_inputs.json').write_text(json.dumps(payload,separators=(',',':')))
 # Derived public curves: omit all raw price and settled-rate columns.
 curves=[{k:r[k] for k in ('symbol','partition','policy','timestamp','net_pnl','funding_total','fees_total','residual_delta_usdt','margin_buffer','basis_bps')} for r in ledger]
 write_csv(OUT/'curves.csv',curves)
 (OUT/'receipt.json').write_text(json.dumps(dict(kind='Post-study descriptive review; not a new holdout',source_run='eed008040d6c6d18',source_sha256={n+'.csv':hashlib.sha256((ROOT/'artifacts/market'/(n+'.csv')).read_bytes()).hexdigest() for n in ('summary','ledger','trades','cost_sensitivity')},definitions='Rates/basis in bps per observed settlement; turnover sums absolute notional on both legs / 100000 sleeve; active events count post-trade perp holdings.'),indent=2))
 print('Prepared review diagnostics and workbook sources')
if __name__=='__main__':main()
