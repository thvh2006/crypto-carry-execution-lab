"""Read-only daily paper loop. Hypothetical fills; never submits an order."""
import argparse
import json
import os
import time
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .engine import Account, Config


def get(url):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=20) as response:return json.load(response)
        except Exception:
            if attempt==2:raise
            time.sleep(.5*(attempt+1))


def fetch(symbol, since):
    start=time.time()
    spot=get(f'https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol={symbol}')
    perp=get(f'https://fapi.binance.com/fapi/v1/ticker/bookTicker?symbol={symbol}')
    clock=get('https://data-api.binance.vision/api/v3/time')['serverTime']
    query=f'&startTime={since+1}' if since else ''
    funds=get(f'https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol}&limit={1000 if since else 1}{query}')
    premium=get(f'https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}')
    if len(funds)==1000:raise ValueError('Funding pagination required; stop rather than truncate')
    elapsed=time.time()-start
    if elapsed>15 or max(abs(clock-perp['time']),abs(clock-premium['time']))>60000:raise ValueError('Stale or unsynchronized quotes')
    prices=[]
    for quote in (spot,perp):
        bid,ask=float(quote['bidPrice']),float(quote['askPrice'])
        if bid<=0 or ask<bid or (ask/bid-1)>.01:raise ValueError('Invalid or wide quote')
        prices.append((bid+ask)/2)
    if not funds:raise ValueError('No settled funding available')
    return dict(timestamp=datetime.fromtimestamp(clock/1000,timezone.utc).isoformat().replace('+00:00','Z'),
        symbol=symbol,spot=prices[0],perp=prices[1],mark=float(premium['markPrice']),funding=float(funds[-1]['fundingRate']),
        observed_ms=clock,quote_window_seconds=elapsed),funds


def step(state,row,funds):
    cfg=Config(quantity_step=.001)
    account=Account(cfg)
    if state:
        if state['config']!=asdict(cfg):raise ValueError('Configuration changed: start a separately labeled paper run')
        if row['observed_ms']-state['observed_ms']<300000:raise ValueError('Duplicate or too-frequent observation')
        for key,value in state['account'].items():setattr(account,key,value)
    last=state['last_funding_ms'] if state else funds[-1]['fundingTime']
    halted=state['halted'] if state else False
    new=[f for f in funds if last<f['fundingTime']<=row['observed_ms']]
    times=[last]+[f['fundingTime'] for f in new]
    if any(abs((b-a)-28800000)>60000 for a,b in zip(times,times[1:])):
        raise ValueError('Funding gap or changed cadence: manual research review required')
    for event in new:
        eventrow=dict(row,mark=float(event['markPrice']),funding=float(event['fundingRate']))
        account.settle(eventrow,0)
        if account.perp_qty and account.margin_buffer(eventrow['mark'])<=0:halted=True
    if halted:
        account.trade_perp(-account.perp_qty,row);account.trade_spot(-account.spot_qty,row)
    elif state:
        account.trade_spot(state['next_target']-account.spot_qty,row)
        account.trade_perp(-state['next_target']-account.perp_qty,row)
    target=0.0
    if not halted and row['funding']>=cfg.funding_threshold:
        target=state['next_target'] if state and state['next_target'] else round(int(cfg.capital*cfg.allocation_fraction/row['spot']/cfg.quantity_step)*cfg.quantity_step,9)
    equity=account.equity(row['spot'],row['mark'])
    bridge=account.realized_spot+account.spot_qty*(row['spot']-account.spot_cost)+account.realized_perp+account.perp_unrealized(row['mark'])+account.funding-account.fees-account.financing
    if abs(equity-cfg.capital-bridge)>1e-6:raise ArithmeticError('Paper reconciliation failed')
    return dict(kind='HYPOTHETICAL PAPER ONLY - no live orders',config=asdict(cfg),symbol=row['symbol'],observed_ms=row['observed_ms'],
        last_funding_ms=max([last]+[f['fundingTime'] for f in new]),next_target=target,halted=halted,
        account={k:v for k,v in vars(account).items() if k not in ('config','fills')},
        receipt=dict(timestamp=row['timestamp'],equity=equity,net_pnl=equity-cfg.capital,funding_total=account.funding,fees=account.fees,
            residual_delta_units=account.spot_qty+account.perp_qty,margin_buffer=account.margin_buffer(row['mark']),new_funding_events=len(new),
            quote_window_seconds=row.get('quote_window_seconds',0),modeled_fills=len(account.fills),reconciliation_error=equity-cfg.capital-bridge))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--state-dir',type=Path,default=Path('paper/state'))
    args=parser.parse_args();args.state_dir.mkdir(parents=True,exist_ok=True)
    lock=args.state_dir/'.lock'
    descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        updates=[]
        for symbol in ('BTCUSDT','ETHUSDT'):
            path=args.state_dir/(symbol+'.json');state=json.loads(path.read_text()) if path.exists() else None
            row,funds=fetch(symbol,state['last_funding_ms'] if state else 0)
            updates.append((path,step(state,row,funds)))
        # All quotes and calculations must pass before either sleeve is replaced.
        for path,value in updates:
            tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2));tmp.replace(path)
            print(json.dumps(dict(symbol=value['symbol'],**value['receipt'])))
        with (args.state_dir/'history.jsonl').open('a') as stream:
            for _,value in updates:stream.write(json.dumps(dict(symbol=value['symbol'],**value['receipt']))+'\n')
    finally:
        os.close(descriptor);lock.unlink()


if __name__=='__main__':main()
