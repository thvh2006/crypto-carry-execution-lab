"""Create the evidence report and an English decision memo from run artifacts."""
import csv
import html
import json
import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports/results';OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'artifacts/market'
def read(name):return list(csv.DictReader((DATA/(name+'.csv')).open()))
summary=read('summary');errors=read('forecast_errors');cost=read('cost_sensitivity');delay=read('delay_sensitivity');intervals=read('paired_uncertainty');ledger=read('ledger')
receipt=json.loads((DATA/'receipt.json').read_text()); manifest=json.loads((ROOT/'data/market/manifest.json').read_text())
font_dir=Path(os.environ.get('P3_TIMES_FONT_DIR','/System/Library/Fonts/Supplemental'))
font=str(font_dir/'Times New Roman.ttf')
bold=str(font_dir/'Times New Roman Bold.ttf')
pdfmetrics.registerFont(TTFont('TimesNR',font));pdfmetrics.registerFont(TTFont('TimesNRBold',bold))
for name,file in [('TimesNRItalic','Times New Roman Italic.ttf'),('TimesNRBoldItalic','Times New Roman Bold Italic.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
pdfmetrics.registerFontFamily('TimesNR',normal='TimesNR',bold='TimesNRBold',italic='TimesNRItalic',boldItalic='TimesNRBoldItalic')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='TimesNR',fontSize=12,leading=18,spaceAfter=7,alignment=TA_JUSTIFY,textColor=colors.black))
styles.add(ParagraphStyle(name='Title2',fontName='TimesNRBold',fontSize=12,leading=18,spaceBefore=14,spaceAfter=7,keepWithNext=True,textColor=colors.black))
styles.add(ParagraphStyle(name='PaperTitle',parent=styles['Title2'],alignment=TA_CENTER,spaceBefore=0,spaceAfter=12))
styles.add(ParagraphStyle(name='Small2',fontName='TimesNR',fontSize=12,leading=15,textColor=colors.black))
styles.add(ParagraphStyle(name='Caption',fontName='TimesNR',fontSize=12,leading=15,spaceBefore=6,spaceAfter=6,keepWithNext=True))
story=[];markdown=[];table_number=0;base_caption_index=0;figure_number=0
TABLE_CAPTIONS=['Net P&L by holdout sleeve and policy.','Accounting identities and treatment of cash flows.','Coverage audit of the 2025 market sample.','Temporal research partitions.','Development and validation net P&L (USDT).','Historical holdout attribution (USDT).','Forecast error and matched strategy economics.','Cost and execution-delay sensitivity (USDT).','Paired P&L differences and block-bootstrap intervals (USDT).','Isolated-margin diagnostics (USDT).','Reproduction commands and evidence artifacts.']
def p(text):story.append(Paragraph(text.replace('&','&amp;'),styles['Body']));markdown.append(text.replace('<b>','**').replace('</b>','**'))
def page(title):
    if not story:
        story.append(Paragraph(title,styles['PaperTitle']))
        story.append(Paragraph('Crypto Carry and Execution Lab | Original study 24 November 2026 | Revised 25 November 2026',ParagraphStyle(name='Meta',parent=styles['Body'],alignment=TA_CENTER)))
        story.append(Paragraph('Abstract',styles['Title2']))
    else:
        import re
        title=re.sub(r'^0([1-9]) / ',r'\1. ',title)
        story.append(Paragraph(title,styles['Title2']))
    markdown.append('\n# '+title+'\n')
def table(headers,rows,widths=None,caption=None):
    global table_number,base_caption_index
    table_number+=1
    if caption is None:
        caption=TABLE_CAPTIONS[base_caption_index];base_caption_index+=1
    caption=f'Table {table_number}. '+caption
    story.append(Paragraph(html.escape(caption),styles['Caption']));markdown.append(caption)
    values=[[Paragraph(('<b>'+html.escape(str(x))+'</b>') if i==0 else html.escape(str(x)),styles['Small2']) for x in r] for i,r in enumerate([headers]+rows)]
    if widths:widths=[w*451/480 for w in widths]
    t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.7,colors.black)]))
    story.extend([t,Spacer(1,6)]);markdown.extend(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])
def num(x):return f'{float(x):,.2f}'
def pct(x):return f'{100*float(x):.2f}%'
def find(symbol,policy,part='holdout'):return next(r for r in summary if r['symbol']==symbol and r['policy']==policy and r['partition']==part)
class Lines(Flowable):
    def __init__(self,symbol,part='holdout'):Flowable.__init__(self);self.width=451;self.height=150;self.symbol=symbol;self.part=part
    def draw(self):
        global figure_number
        figure_number+=1
        c=self.canv; c.scale(451/480,451/480); names=['spot','continuous','threshold'];cols=['#666666','#000000','#333333']
        data=[[r for r in ledger if r['symbol']==self.symbol and r['partition']==self.part and r['policy']==name] for name in names]
        vals=[float(r['net_pnl']) for rows in data for r in rows];lo=min(vals+[0]);hi=max(vals+[0]);span=hi-lo or 1
        c.setFont('TimesNR',12);c.setFillColor(colors.black);c.drawString(0,142,f'Figure {figure_number}. '+self.symbol+' net P&L (USDT).');c.drawString(0,125,num(hi));c.drawString(0,20,num(lo))
        for name,color,rows in zip(names,cols,data):
            line=c.beginPath()
            for i,r in enumerate(rows):
                x=60+i*410/(len(rows)-1);y=22+(float(r['net_pnl'])-lo)*100/span
                if i:line.lineTo(x,y)
                else:line.moveTo(x,y)
            c.setStrokeColor(colors.HexColor(color));c.setDash([[],[5,2],[1,2]][names.index(name)]);c.drawPath(line);c.setDash([]);c.setFillColor(colors.HexColor(color));c.drawString(60+names.index(name)*135,4,name)

def review_csv(name):
    return list(csv.DictReader((ROOT/'artifacts/review'/(name+'.csv')).open()))
diagnostics=review_csv('funding_diagnostics');regimes=review_csv('monthly_regimes');turnover=review_csv('turnover')
class DiagnosticLines(Flowable):
    def __init__(self,title,labels,series,unit):
        Flowable.__init__(self);self.width=451;self.height=190;self.caption=title;self.labels=labels;self.series=series;self.unit=unit
    def draw(self):
        global figure_number
        figure_number+=1;c=self.canv;c.setFont('TimesNR',12);c.setFillColor(colors.black)
        c.drawString(0,176,f'Figure {figure_number}. '+self.caption)
        allvals=[x for values in self.series.values() for x in values];lo=min(allvals+[0]);hi=max(allvals+[0]);span=hi-lo or 1
        c.setFont('TimesNR',10);c.drawString(0,157,self.unit);c.drawString(0,139,num(hi));c.drawString(0,44,num(lo))
        for j,(name,values) in enumerate(self.series.items()):
            line=c.beginPath()
            for i,value in enumerate(values):
                x=65+i*375/max(1,len(values)-1);y=45+(value-lo)*95/span
                if i:line.lineTo(x,y)
                else:line.moveTo(x,y)
            c.setStrokeColor(colors.black);c.setDash([[],[5,2]][j%2]);c.drawPath(line);c.setDash([]);c.drawString(65+j*180,5,name)
        for i in sorted({0,len(self.labels)//2,len(self.labels)-1}):
            c.drawString(65+i*345/max(1,len(self.labels)-1),25,str(self.labels[i]))

page('Funding Carry after Transaction Costs: A BTC and ETH Study')
p('Does long spot and short a linear perpetual produce useful net economics once funding reversals, both legs, turnover and separate collateral are counted? The answer in this fixed 2025 sample depends strongly on how often the position is switched.')
p('Continuous carry made a small positive net result in the October-December holdout. The last-rate threshold repeatedly paid to enter and exit and lost money. Smoother forecasts reduced the loss relative to that threshold, but neither forecast strategy beat continuous carry in this holdout. This is a useful negative result, not a deployable return claim.')
p('<b>Keywords:</b> cryptocurrency; cash-and-carry; funding rates; transaction costs; isolated margin.')
story.append(Paragraph('Research overview',styles['Title2']))
table(['Holdout sleeve','Continuous carry','Last-rate threshold'],[[s,num(find(s,'continuous')['net_pnl']),num(find(s,'threshold')['net_pnl'])] for s in ('BTCUSDT','ETHUSDT')],[150,165,165])
p('Each asset/policy starts with a separate 100,000 USDT sleeve. Results are hypothetical bar-based executions after fees and slippage. They exclude live fills, custody/venue default, tax, tier-exact liquidation and a forward paper track record. Do not interpret the two sleeves as a combined 100,000 USDT portfolio.')
p('The package contains the audited data contract, frozen study receipt, all three research partitions, six policy variants, forecast errors, cost/delay sensitivities, paired uncertainty, independent Excel mechanics and 22 automated tests. Run identifier: '+receipt['run_id']+'.')

page('Research context and contribution')
p('Schmeling, Schrimpf and Todorov [6] document variation in crypto futures basis and relate carry to demand for leveraged exposure and limited arbitrage capital. Their analysis also emphasizes margin and liquidation risk. Their dated-futures setting should not be treated as a promise of the same return for a perpetual funding strategy.')
p('Ackerer, Hugonnier and Jermann [7] study no-arbitrage pricing of perpetual contracts and the role of periodic funding in anchoring prices. That theoretical connection does not establish that a historical last-rate trading rule survives transaction costs.')
p('This project addresses a narrower empirical question: under a disclosed single-venue, cash-funded, sampled-execution design, how much of observed carry remains after both legs, switching and collateral constraints? It does not replicate either paper, estimate a structural convenience yield, or infer a guaranteed annual carry return. The contribution is an auditable accounting and decision comparison with negative findings retained.')

page('01 / Contract mechanics and capital')
p('Universe: Binance BTCUSDT and ETHUSDT spot plus USDT-margined linear perpetuals. Perpetual quantity is signed base units, with short quantities negative. Positive funding pays a short position [2]. Funding cash at an event is -q_perp × settlement mark × settled rate. New positions entered after settlement receive no cash for that event.')
p('The 100,000 USDT capital denominator includes 65,000 spot-wallet cash and 35,000 isolated derivatives collateral. Desired matched spot exposure is 55% of initial capital. Quantity is fixed while active and recalculated on re-entry. The market study uses a conservative common 0.001 base-unit quantity step. Current exchangeInfo corroborates the linear USDT instruments and perpetual step; it is not historical filter evidence [5].')
table(['Accounting identity','Treatment'],[['Equity','Spot cash + spot market value + perp collateral + unrealized perp P&L'],['Net P&L','Spot P&L + perp P&L + funding - commissions - financing'],['Slippage','Embedded once in each leg’s P&L; shown separately as a diagnostic'],['Collateral transfers','Internal allocation, never profit'],['Financing','0% base assumption for a fully cash-funded sleeve; opportunity cost excluded']],[145,335])
p('The independent workbook case uses 275 filled spot units against 550 short perp units, spot price 100 and perp close 105, with three positive/negative settlements. The default result is -2,860.825 USDT, funding +0.55 and residual delta -275 units. Four commissions are included. Workbook formulas reconcile to the Python Account case; changing the spot-fill input changes the result.')

page('02 / Source provenance and coverage')
p('Official public API responses were read in Chrome and saved as plain UTF-8 JSON after shell DNS and several archive downloads failed. Raw records are preserved in the private package with SHA-256 receipts. No account endpoint, API key or order endpoint was used. An independently downloaded January BTC funding archive was also available [1, 3, 4].')
table(['Coverage 2025','BTCUSDT','ETHUSDT'],[['Funding events','1,095','1,095'],['Spot / perp / mark 8h bars','1,095 each','1,095 each'],['Missing or duplicate nominal events','0','0'],['Negative funding events','141','177'],['Maximum event offset / quote age','16 ms','16 ms']],[240,120,120])
p('All 93 January BTC funding timestamps and rates match the same-provider public archive exactly. This checks schema and ingestion, not independent exchange truth. Funding timestamps are actual event milliseconds. Price references are the nominal 8-hour bar OPEN; close, high and low are never used as executable prices or signal features. A reference can precede funding availability by up to 16 ms, so it remains an execution approximation.')
p('The bar-high mark series is used only as an ex-post isolated-margin diagnostic. It is never a tradable quote or predictor. The archive microsecond convention for 2025 spot files is not applied to API kline milliseconds. No missing funding is filled with zero. A changed cadence, duplicate or incomplete coverage stops normalization.')
p('Access is public, but no unrestricted market-data redistribution license is asserted. Raw and normalized snapshots stay out of the public source export. The private delivery preserves them for reproducibility. Historical maintenance tiers, fee tier, minimum order filters and depth are unavailable and explicitly remain assumptions.')

page('2.1. Post-study funding and basis diagnostics')
p('The following descriptive analysis was added after the historical holdout was consumed. It explains market conditions and switching costs; it does not select a new threshold, model or sample. Rates are basis points per observed settlement. Basis is traded perpetual / spot minus one, separate from the settlement mark.')
table(['Asset','Negative funding','Longest negative run','Lag-1 funding correlation','Median basis (bps)'],[[r['symbol'],pct(r['negative_fraction']),r['longest_negative_run'],f"{float(r['funding_lag1_correlation']):.3f}",num(r['basis_median_bps'])] for r in diagnostics],[100,95,95,95,95],caption='Descriptive funding persistence and traded-price basis, full 2025 sample.')
p('BTC funding is negative at approximately 12.9% of observed settlements and ETH at 16.2%. Positive average funding therefore does not remove payment reversals. Lag-one funding correlation is around 0.55 for BTC and 0.53 for ETH; serial dependence motivates testing smoother forecasts but does not establish an investable edge. Contemporaneous funding/basis correlations are descriptive, not causal predictors.')
monthly={s:[r for r in regimes if r['symbol']==s] for s in ('BTCUSDT','ETHUSDT')}
story.append(DiagnosticLines('Monthly mean funding in the observed year',[r['month'] for r in monthly['BTCUSDT']],{s:[float(r['mean_funding_bps']) for r in rs] for s,rs in monthly.items()},'bps per settlement'))
p('The monthly summaries preserve all events rather than removing difficult regimes. Full quantiles, histogram counts and negative-run diagnostics are retained in artifacts/review and the first executed notebook. Bar sampling and timestamp offsets limit interpretation of the basis measurements.')

page('03 / Frozen temporal design')
table(['Partition','Dates UTC','Purpose / events per asset'],[['Development','Jan-Jun 2025','Pipeline development / 543'],['Validation','Jul-Sep 2025','Fixed specification check / 276'],['Historical holdout','Oct-Dec 2025','Final retrospective comparison / 276']],[110,145,225])
p('The written protocol preceded the first strategy-return inspection. Acquisition was amended from hourly monthly archives to official 8-hour API bars because of access failures, before running the market study. Engine, adapter, study code, forecasting code, protocol, normalized inputs and configuration were hashed before the initial run. The freeze file rejects a rerun if any of those contents change.')
p('Each partition starts flat with fresh capital and closes fully at its final sampled observation. Therefore partition results are separate experiments, not a continuously compounded full-year portfolio. Forecast histories can use earlier chronological partitions; no future funding enters a training window. All policy variants share timestamps, capital and execution assumptions.')
p('Event order is: settle existing positions, check sampled isolated margin, execute the earlier target, record/reconcile equity, then decide the next target. The base delay is one observation, roughly eight hours. Sensitivities delay by two or three observations. No strategy can earn the just-observed settlement by opening at that same row.')
p('The fixed trial budget is one last-rate model, one trailing-nine mean and one ridge AR(1), with no hyperparameter optimization. Ridge uses at most 90 previous observations, at least 24, train-only standardization and fixed shrinkage. EWMA with decay 0.94 is a causal diagnostic rather than a trading rule. No threshold or sample was tuned to improve the holdout.')

page('04 / Baselines before the holdout')
p('Unhedged spot measures directional exposure at the same 55% allocation. Continuous carry holds equal spot and short-perpetual base quantities. Threshold carry is active when the last settled funding rate is at least 0.00005 (0.005% per settlement), and acts only at the later observation. There is no hysteresis or minimum holding period in this deliberately simple baseline.')
table(['Asset / partition','Spot net','Carry net','Threshold net'],[[s+' / '+part,num(find(s,'spot',part)['net_pnl']),num(find(s,'continuous',part)['net_pnl']),num(find(s,'threshold',part)['net_pnl'])] for part in ('development','validation') for s in ('BTCUSDT','ETHUSDT')],[180,100,100,100])
p('These partitions are reported alongside the holdout so an attractive single window cannot stand in for the whole experiment. A holdout comparison remains retrospective: the data were collected after 2025 and implementation choices reflect this research context. The freeze prevents hidden edits within this run, not prior knowledge of the market history.')
p('Cash constraints, quantity rounding and initial-margin rejection can leave a residual delta when both legs do not match. Synthetic partial fills and outages exercise the same accounting path; historical base fills are 100% assumptions with adverse price slippage. No historical fill probability, capacity or maker priority is inferred from OHLC bars.')

page('05 / Net holdout attribution')
table(['Sleeve / policy','Net P&L','Funding','Fees','Max DD'],[[s+' / '+name,num(find(s,name)['net_pnl']),num(find(s,name)['funding']),num(find(s,name)['fees']),pct(find(s,name)['max_drawdown'])] for s in ('BTCUSDT','ETHUSDT') for name in ('spot','continuous','threshold')],[180,75,75,75,75])
story.append(Lines('BTCUSDT'));story.append(Spacer(1,10));story.append(Lines('ETHUSDT'))
p('Values are USDT except drawdown. Slippage is already inside leg P&L. Full spot/perp attribution, residual exposure, fills and sampled margin are in summary.csv and ledger.csv. A positive carry result is small relative to the 100,000 denominator; gross funding alone exaggerates its economics.')

page('5.1. Turnover and the gross-to-net mechanism')
table(['Asset / policy','Fill count','Two-leg turnover / capital','Fees (USDT)'],[[r['symbol']+' / '+r['policy'],r['fills'],num(r['turnover_over_capital']),num(r['fees'])] for r in turnover if r['partition']=='holdout' and r['policy'] in ('continuous','threshold','forecast_rolling_mean')],[230,65,100,85],caption='Holdout execution intensity; absolute traded notional on both legs divided by 100,000 USDT.')
p('ETH continuous carry uses four modeled fills, whereas the naive threshold uses 192. Two-leg turnover rises from about 1.89 times capital to 103.83 times. Funding receipts are lower for the switching policy while its commission bill rises sharply. The mean forecast reduces switching intensity, explaining part of its improvement over the naive rule. This is an execution-cost mechanism, not proof that forecast skill produces alpha.')

page('06 / Forecast skill versus strategy value')
table(['Asset / model','Holdout MAE, bps','Matched net P&L'],[[s+' / '+m,num(float(next(r['mae'] for r in errors if r['symbol']==s and r['partition']=='holdout' and r['model']==m))*10000),num(find(s,'forecast_'+m)['net_pnl'])] for s in ('BTCUSDT','ETHUSDT') for m in ('last_rate','rolling_mean','ridge_ar1')],[240,120,120])
p('Forecasts predict the next settled rate using data through the current settlement. Their recorded training cutoff precedes the target event. All three are inserted into the same threshold rule. During initial model warm-up the matched forecast family holds cash; the full-history last-rate trading baseline is also reported separately. In validation/holdout all models already have a past training history.')
p('Smoothing reduces the number of switches around a threshold. Its improved net result relative to the last-rate rule is therefore not evidence that forecasting funding creates investable alpha. Lower forecast error and lower trading loss are separate questions. Ridge has a lower ETH holdout MAE than the mean but a worse net trading result.')
p('The matched forecasts remain negative after assumed costs in both holdout sleeves, while continuous carry is positive. The incremental-benefit gate fails against that operationally simpler benchmark. A subsequent hysteresis, cost-aware entry rule or different model must be a separately logged study; this holdout is now consumed.')

page('07 / Friction and uncertainty')
table(['Asset / policy','Cost ×1','Cost ×2','Cost ×3','Delay 3 events'],[[s+' / '+name]+[num(next(r['net_pnl'] for r in cost if r['symbol']==s and r['partition']=='holdout' and r['policy']==name and int(r['cost_multiple'])==m)) for m in (1,2,3)]+[num(next(r['net_pnl'] for r in delay if r['symbol']==s and r['partition']=='holdout' and r['policy']==name and r['delay_events']=='3'))] for s in ('BTCUSDT','ETHUSDT') for name in ('continuous','threshold')],[180,75,75,75,75])
p('Cost multiples apply to both leg commissions and adverse slippage. Delay sensitivity is separate, at base costs, and changes the first eligible execution observation. The small continuous-carry profit has limited room for larger friction or opportunity cost. Base fees are assumptions, not a promise of the user’s exchange tier.')
table(['Threshold minus continuous','Observed difference','95% block interval'],[[s,num(next(r['paired_pnl_difference'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold')),num(next(r['block_bootstrap_low'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold'))+' to '+num(next(r['block_bootstrap_high'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold'))] for s in ('BTCUSDT','ETHUSDT')],[180,125,175])
story.append(DiagnosticLines('Continuous carry under higher friction',['1x','2x','3x'],{symbol:[float(next(r['net_pnl'] for r in cost if r['symbol']==symbol and r['partition']=='holdout' and r['policy']=='continuous' and int(r['cost_multiple'])==m)) for m in (1,2,3)] for symbol in ('BTCUSDT','ETHUSDT')},'Net P&L (USDT)'))
p('Uncertainty uses paired daily P&L differences, seven-day moving blocks, 2,000 replications and seed 20261124. It resamples the observed 92-day regime and does not model new regimes, venue failure, model selection or execution misspecification. Intervals are descriptive and are not multiple-testing-adjusted. Forecast-versus-last-rate intervals are in paired_uncertainty.csv.')

page('08 / Margin is a separate survival problem')
table(['Holdout policy','Minimum sampled buffer','Minimum 8h-high proxy'],[[s+' / '+name,num(find(s,name)['minimum_sampled_margin_buffer']),num(find(s,name)['minimum_bar_high_margin_proxy'])] for s in ('BTCUSDT','ETHUSDT') for name in ('continuous','threshold')],[220,130,130])
p('The margin account does not automatically access gains in the spot wallet. The seven scenario cases cover negative funding, a basis widening, a joint 80% rally, half-filled spot, higher maintenance, a collateral haircut and a stablecoin depeg. In the joint rally the combined sleeve can retain most economic capital while isolated collateral fails.')
p('The bar-high proxy revalues the post-trade short at the maximum mark inside the following 8-hour bar, holding that row’s collateral fixed. It is an ex-post stress diagnostic. Its positive buffer does not certify absence of liquidation: the path of cash transfers, funding, tier changes and liquidation mechanics is not reconstructed. No intrabar event ordering is invented from OHLC.')
p('A sampled margin breach triggers a modeled unwind at sampled traded prices and stops new entries. This preserves a deficit instead of erasing it. Full fills on a forced close are an approximation; the stress case is not an exact exchange liquidation engine. Historical liquidation fees, insurance fund behavior, ADL, custody loss and venue default require separate evidence.')
p('USDT equals USD in the base replay. The depeg scenario translates economic equity into USD; collateral eligibility haircuts are modeled separately. Treating a collateral haircut as an immediate mark-to-market loss would mix two different mechanisms.')

page('09 / Operations, reproduction and decision')
p('The paper module is strictly read-only: public prices/funding in, hypothetical targets and receipts out. It contains no authenticated or order API. The first snapshot starts flat and cannot claim earlier funding. Later runs settle new funding on existing paper holdings before executing the prior target. A state lock, duplicate-time guard, funding-gap check, quote sanity check and event-level reconciliation fail closed.')
p('Release 0.3 preserves the original economic source and outcomes. Python 3.9.6 reproduced all seven CSV outputs byte-for-byte. A separate Python 3.12 tolerance check found identical trading outcomes, with only forecast-error summary rounding differing at approximately 6.8e-21. The original freeze is not reset; new receipts record the reproduction mode and environment.')
p('Operational check: GitHub CI passed. The hosted paper run returned HTTP 451 from Binance futures bookTicker; its schedule was removed and no successful paper state is claimed. The public dashboard and CSV export were checked in Chrome.')
p('Paper polling is coarser than live trading. Quotes are midpoint references with modeled slippage; funding is actually observed but fills are hypothetical. A changed cadence, stale quote, incomplete page or failed network request stops the update. Scheduled execution depends on endpoint access from the chosen runner. A successful workflow is operational evidence, never proof of a future return.')
table(['Reproduction','Command / artifact'],[['Verify engine','python3 -m unittest discover -s tests -v'],['Synthetic replay','python3 -m carry.run demo'],['Normalize preserved snapshots','python3 -m carry.market'],['Frozen study reproduction','python3 -m carry.reproduce'],['Read-only paper observation','python3 -m carry.paper'],['Receipts','artifacts/market/freeze.json and receipt.json']],[160,320])
p('<b>Decision:</b> retain continuous carry as the research benchmark and reject this naive threshold as an execution policy at the assumed fee schedule. Do not deploy from these results. The next study should price switching decisions against expected holding duration and friction, acquire execution-level observations and historical margin tiers, and accumulate a genuine forward paper record without recycling the consumed holdout.')
story.append(PageBreak())
story.append(Paragraph('References',styles['Title2']))
markdown.append('\n# References\n')
references=[
 '[1] Binance. (n.d.). Binance Public Data [Data repository]. https://github.com/binance/binance-public-data (accessed 24 November 2026).',
 '[2] Binance. (n.d.). Funding rates for perpetual futures. https://www.binance.com/en/support/faq/detail/360033525031 (accessed 24 November 2026).',
 '[3] Binance. (2026). Spot market-data API: Historical klines. https://data-api.binance.vision/api/v3/klines. BTCUSDT and ETHUSDT, 2025 observations; retrieved 24 November 2026. Exact parameters are retained in the study manifest.',
 '[4] Binance. (2026). USD-M futures market-data API: Funding history, contract klines and mark-price klines. https://fapi.binance.com/fapi/v1/fundingRate ; https://fapi.binance.com/fapi/v1/klines ; https://fapi.binance.com/fapi/v1/markPriceKlines. Retrieved 24 November 2026.',
 '[5] Binance. (2026). USD-M futures exchange information [Contract specification snapshot]. https://fapi.binance.com/fapi/v1/exchangeInfo. Retrieved 24 November 2026. Current specifications do not establish historical fee or maintenance tiers.'
]
references.extend([
 '[6] Schmeling, M., Schrimpf, A., & Todorov, K. (2023). Crypto carry. BIS Working Papers No. 1087, April 2023 version. https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf (accessed 25 November 2026).',
 '[7] Ackerer, D., Hugonnier, J., & Jermann, U. (2024). Perpetual Futures Pricing. arXiv:2310.11771v2, revised 4 September 2024. https://arxiv.org/abs/2310.11771v2 (accessed 25 November 2026).'
])
reference_style=ParagraphStyle(name='Reference',parent=styles['Body'],alignment=TA_LEFT,leftIndent=18,firstLineIndent=-18,spaceAfter=12)
for reference in references:
    story.append(Paragraph(html.escape(reference),reference_style));markdown.append(reference)


def footer(c,doc):
    c.setFont('TimesNR',10);c.setFillColor(colors.black);c.drawCentredString(297.5,40,str(doc.page))
doc=SimpleDocTemplate(str(OUT/'P3_Crypto_Carry_Research_Report.pdf'),pagesize=(595,842),rightMargin=72,leftMargin=72,topMargin=72,bottomMargin=72)
doc.title='Funding Carry after Transaction Costs: A BTC and ETH Study'
doc.author='Crypto Carry and Execution Lab'
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'P3_Crypto_Carry_Research_Report.md').write_text('\n\n'.join(markdown))
memo=f'''# P3 - Decision Memo

**Date:** 24 November 2026  
**Study run:** `{receipt['run_id']}`  
**Scope:** Retrospective 2025 research with hypothetical execution.

## Decision

Retain continuous carry as the research benchmark. Reject the naive last-settled-funding threshold at the assumed transaction-cost schedule. Neither tested forecast strategy improves on continuous carry in the historical holdout. These findings do not establish a deployable trading edge.

## Historical holdout results

The holdout covers 1 October-31 December 2025. Each asset-policy combination starts flat with a separate **100,000 USDT** sleeve and closes at the final sampled observation. Results are net of modeled commissions and slippage; the two assets do not share a single capital denominator.

| Policy | BTC net P&L (USDT) | ETH net P&L (USDT) |
|---|---:|---:|
| Continuous carry | {num(find('BTCUSDT','continuous')['net_pnl'])} | {num(find('ETHUSDT','continuous')['net_pnl'])} |
| Last-settled-rate threshold | {num(find('BTCUSDT','threshold')['net_pnl'])} | {num(find('ETHUSDT','threshold')['net_pnl'])} |
| Nine-period mean forecast + threshold | {num(find('BTCUSDT','forecast_rolling_mean')['net_pnl'])} | {num(find('ETHUSDT','forecast_rolling_mean')['net_pnl'])} |
| Ridge AR(1) forecast + threshold | {num(find('BTCUSDT','forecast_ridge_ar1')['net_pnl'])} | {num(find('ETHUSDT','forecast_ridge_ar1')['net_pnl'])} |

Frequent switching makes the threshold policy's commissions exceed its funding receipts. Smoother forecasts reduce turnover and losses relative to the last-rate rule, but both forecast strategies remain negative in both sleeves. Lower forecast error does not automatically translate into better net economics. The continuous-carry gain is small relative to total capital and offers limited room for additional friction or opportunity cost.

## Evidence supporting the decision

- **Coverage:** 1,095 funding events and 1,095 bars for each spot, perpetual and mark stream per asset in 2025, with no missing or duplicate nominal events.
- **Ingestion cross-check:** All 93 January BTC funding timestamps and rates match between the public archive and API. Both are from the same provider, so this is not independent confirmation of exchange truth.
- **Accounting:** 22 tests and 13,140 event-ledger rows across six policy variants, three temporal partitions and two assets. Maximum reconciliation residual is below 1e-9 USDT.
- **Research controls:** Written protocol and frozen source/input/configuration hashes before the first strategy-return inspection; chronological development, validation and historical holdout partitions; paired seven-day block-bootstrap intervals; cost multiples of 1, 2 and 3; execution delays of 1, 2 and 3 observations.
- **Independent review:** Formula-driven workbook with a Python golden-case reconciliation, executed notebooks and a public dashboard retaining negative results.

## Limits and operational status

Executable references are eight-hour bar opens matched to actual funding timestamps, with an offset of up to 16 ms. Fills, fee tiers and flat maintenance rates are assumptions. The bar-high margin proxy does not certify intraperiod liquidation safety. P&L is denominated in USDT, not guaranteed USD value. Historical margin tiers, order-book depth, execution capacity and a forward track record remain unverified.

The paper collector reads public data and records hypothetical positions without API keys or order endpoints. Its hosted GitHub run returned **HTTP 451** from Binance futures. Automatic scheduling was removed; no successful forward paper state or performance is claimed. The failure is retained as operational evidence rather than replaced with assumed data.

## Release 0.3 review improvements

The original study outcomes are unchanged. Four executed notebooks now include rich diagnostic tables/figures, funding/basis regimes and turnover analysis. Excel adds historical sleeve selectors, a full derived account source, a native two-variable fee/slippage Data Table and a formula-driven cash/collateral scenario. The dashboard compares partitions, all policy variants, forecasts and archived cost runs. Exact reproduction is isolated from the consumed study and separately labeled across Python versions.

## Next research gate

Any hysteresis, cost-aware entry rule or model change requires a separately recorded study. The current holdout has been consumed and must not be relabeled untouched. Before considering deployment, obtain execution-level observations and historical margin specifications, verify a permitted data-access environment, and accumulate a genuine forward paper record.

The portfolio contribution is a reproducible research process that explains a negative result and its execution limits, rather than a claim of guaranteed carry income.
'''
(OUT/'P3_Decision_Memo.md').write_text(memo)
print('Report and memo written')
