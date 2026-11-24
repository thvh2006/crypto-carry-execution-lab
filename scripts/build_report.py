"""Create the evidence report and a Vietnamese decision memo from run artifacts."""
import csv
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'reports/results';OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'artifacts/market'
def read(name):return list(csv.DictReader((DATA/(name+'.csv')).open()))
summary=read('summary');errors=read('forecast_errors');cost=read('cost_sensitivity');delay=read('delay_sensitivity');intervals=read('paired_uncertainty');ledger=read('ledger')
receipt=json.loads((DATA/'receipt.json').read_text()); manifest=json.loads((ROOT/'data/market/manifest.json').read_text())
font='/System/Library/Fonts/Supplemental/Arial.ttf';bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
pdfmetrics.registerFont(TTFont('Arial',font));pdfmetrics.registerFont(TTFont('ArialBold',bold))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body',fontName='Arial',fontSize=10,leading=15,spaceAfter=10))
styles.add(ParagraphStyle(name='Title2',fontName='ArialBold',fontSize=24,leading=29,spaceAfter=16,textColor=colors.HexColor('#173e38')))
styles.add(ParagraphStyle(name='Small2',fontName='Arial',fontSize=8,leading=11))
styles.add(ParagraphStyle(name='Sub2',fontName='ArialBold',fontSize=13,leading=17,spaceAfter=10))
story=[];markdown=[]
def p(text):story.append(Paragraph(text,styles['Body']));markdown.append(text.replace('<b>','**').replace('</b>','**'))
def page(title):
    if story:story.append(PageBreak())
    story.extend([Paragraph('P3 / CRYPTO CARRY &amp; EXECUTION LAB',styles['Small2']),Spacer(1,12),Paragraph(title,styles['Title2'])]);markdown.append('\n# '+title+'\n')
def table(headers,rows,widths=None):
    values=[[Paragraph(str(x),styles['Small2']) for x in r] for r in [headers]+rows]
    t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173e38')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#ccd6d2'))]))
    # Paragraph colors are explicit for header text.
    for cell in values[0]:cell.style=ParagraphStyle(name='Header',parent=styles['Small2'],textColor=colors.white,fontName='ArialBold')
    story.extend([t,Spacer(1,12)]);markdown.extend(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])
def num(x):return f'{float(x):,.2f}'
def pct(x):return f'{100*float(x):.2f}%'
def find(symbol,policy,part='holdout'):return next(r for r in summary if r['symbol']==symbol and r['policy']==policy and r['partition']==part)
class Lines(Flowable):
    def __init__(self,symbol,part='holdout'):Flowable.__init__(self);self.width=480;self.height=150;self.symbol=symbol;self.part=part
    def draw(self):
        c=self.canv; names=['spot','continuous','threshold'];cols=['#526779','#137c66','#d97a37']
        data=[[r for r in ledger if r['symbol']==self.symbol and r['partition']==self.part and r['policy']==name] for name in names]
        vals=[float(r['net_pnl']) for rows in data for r in rows];lo=min(vals+[0]);hi=max(vals+[0]);span=hi-lo or 1
        c.setFont('Arial',8);c.setFillColor(colors.HexColor('#173e38'));c.drawString(0,142,self.symbol+' | Net P&L, USDT');c.drawString(0,125,num(hi));c.drawString(0,20,num(lo))
        for name,color,rows in zip(names,cols,data):
            line=c.beginPath()
            for i,r in enumerate(rows):
                x=60+i*410/(len(rows)-1);y=22+(float(r['net_pnl'])-lo)*100/span
                if i:line.lineTo(x,y)
                else:line.moveTo(x,y)
            c.setStrokeColor(colors.HexColor(color));c.drawPath(line);c.setFillColor(colors.HexColor(color));c.drawString(60+names.index(name)*135,4,name)

page('Funding carry after the friction bill')
p('<b>Retrospective market evidence / 24 November 2026.</b> Does long spot and short a linear perpetual produce useful net economics once funding reversals, both legs, turnover and separate collateral are counted? The answer in this fixed 2025 sample depends strongly on how often the position is switched.')
p('Continuous carry made a small positive net result in the October-December holdout. The last-rate threshold repeatedly paid to enter and exit and lost money. Smoother forecasts reduced the loss relative to that threshold, but neither forecast strategy beat continuous carry in this holdout. This is a useful negative result, not a deployable return claim.')
table(['Holdout sleeve','Continuous carry','Last-rate threshold'],[[s,num(find(s,'continuous')['net_pnl']),num(find(s,'threshold')['net_pnl'])] for s in ('BTCUSDT','ETHUSDT')],[150,165,165])
p('Each asset/policy starts with a separate 100,000 USDT sleeve. Results are hypothetical bar-based executions after fees and slippage. They exclude live fills, custody/venue default, tax, tier-exact liquidation and a forward paper track record. Do not interpret the two sleeves as a combined 100,000 USDT portfolio.')
p('The package contains the audited data contract, frozen study receipt, all three research partitions, six policy variants, forecast errors, cost/delay sensitivities, paired uncertainty, independent Excel mechanics and 18 automated tests. Run identifier: '+receipt['run_id']+'.')

page('01 / Contract mechanics and capital')
p('Universe: Binance BTCUSDT and ETHUSDT spot plus USDT-margined linear perpetuals. Perpetual quantity is signed base units, with short quantities negative. Positive funding pays a short position. Funding cash at an event is -q_perp × settlement mark × settled rate. New positions entered after settlement receive no cash for that event.')
p('The 100,000 USDT capital denominator includes 65,000 spot-wallet cash and 35,000 isolated derivatives collateral. Desired matched spot exposure is 55% of initial capital. Quantity is fixed while active and recalculated on re-entry. The market study uses a conservative common 0.001 base-unit quantity step. Current exchangeInfo corroborates the linear USDT instruments and perpetual step; it is not historical filter evidence.')
table(['Accounting identity','Treatment'],[['Equity','Spot cash + spot market value + perp collateral + unrealized perp P&L'],['Net P&L','Spot P&L + perp P&L + funding - commissions - financing'],['Slippage','Embedded once in each leg’s P&L; shown separately as a diagnostic'],['Collateral transfers','Internal allocation, never profit'],['Financing','0% base assumption for a fully cash-funded sleeve; opportunity cost excluded']],[145,335])
p('The independent workbook case uses 275 filled spot units against 550 short perp units, spot price 100 and perp close 105, with three positive/negative settlements. The default result is -2,860.825 USDT, funding +0.55 and residual delta -275 units. Four commissions are included. Workbook formulas reconcile to the Python Account case; changing the spot-fill input changes the result.')

page('02 / Source provenance and coverage')
p('Official public API responses were read in Chrome and saved as plain UTF-8 JSON after shell DNS and several archive downloads failed. Raw records are preserved in the private package with SHA-256 receipts. No account endpoint, API key or order endpoint was used. An independently downloaded January BTC funding archive was also available.')
table(['Coverage 2025','BTCUSDT','ETHUSDT'],[['Funding events','1,095','1,095'],['Spot / perp / mark 8h bars','1,095 each','1,095 each'],['Missing or duplicate nominal events','0','0'],['Negative funding events','141','177'],['Maximum event offset / quote age','16 ms','16 ms']],[240,120,120])
p('All 93 January BTC funding timestamps and rates match the same-provider public archive exactly. This checks schema and ingestion, not independent exchange truth. Funding timestamps are actual event milliseconds. Price references are the nominal 8-hour bar OPEN; close, high and low are never used as executable prices or signal features. A reference can precede funding availability by up to 16 ms, so it remains an execution approximation.')
p('The bar-high mark series is used only as an ex-post isolated-margin diagnostic. It is never a tradable quote or predictor. The archive microsecond convention for 2025 spot files is not applied to API kline milliseconds. No missing funding is filled with zero. A changed cadence, duplicate or incomplete coverage stops normalization.')
p('Access is public, but no unrestricted market-data redistribution license is asserted. Raw and normalized snapshots stay out of the public source export. The private delivery preserves them for reproducibility. Historical maintenance tiers, fee tier, minimum order filters and depth are unavailable and explicitly remain assumptions.')

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

page('06 / Forecast skill versus strategy value')
table(['Asset / model','Holdout MAE, bps','Matched net P&L'],[[s+' / '+m,num(float(next(r['mae'] for r in errors if r['symbol']==s and r['partition']=='holdout' and r['model']==m))*10000),num(find(s,'forecast_'+m)['net_pnl'])] for s in ('BTCUSDT','ETHUSDT') for m in ('last_rate','rolling_mean','ridge_ar1')],[240,120,120])
p('Forecasts predict the next settled rate using data through the current settlement. Their recorded training cutoff precedes the target event. All three are inserted into the same threshold rule. During initial model warm-up the matched forecast family holds cash; the full-history last-rate trading baseline is also reported separately. In validation/holdout all models already have a past training history.')
p('Smoothing reduces the number of switches around a threshold. Its improved net result relative to the last-rate rule is therefore not evidence that forecasting funding creates investable alpha. Lower forecast error and lower trading loss are separate questions. Ridge has a lower ETH holdout MAE than the mean but a worse net trading result.')
p('The matched forecasts remain negative after assumed costs in both holdout sleeves, while continuous carry is positive. The incremental-benefit gate fails against that operationally simpler benchmark. A subsequent hysteresis, cost-aware entry rule or different model must be a separately logged study; this holdout is now consumed.')

page('07 / Friction and uncertainty')
table(['Asset / policy','Cost ×1','Cost ×2','Cost ×3','Delay 3 events'],[[s+' / '+name]+[num(next(r['net_pnl'] for r in cost if r['symbol']==s and r['partition']=='holdout' and r['policy']==name and int(r['cost_multiple'])==m)) for m in (1,2,3)]+[num(next(r['net_pnl'] for r in delay if r['symbol']==s and r['partition']=='holdout' and r['policy']==name and r['delay_events']=='3'))] for s in ('BTCUSDT','ETHUSDT') for name in ('continuous','threshold')],[180,75,75,75,75])
p('Cost multiples apply to both leg commissions and adverse slippage. Delay sensitivity is separate, at base costs, and changes the first eligible execution observation. The small continuous-carry profit has limited room for larger friction or opportunity cost. Base fees are assumptions, not a promise of the user’s exchange tier.')
table(['Threshold minus continuous','Observed difference','95% block interval'],[[s,num(next(r['paired_pnl_difference'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold')),num(next(r['block_bootstrap_low'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold'))+' to '+num(next(r['block_bootstrap_high'] for r in intervals if r['symbol']==s and r['partition']=='holdout' and r['policy']=='threshold'))] for s in ('BTCUSDT','ETHUSDT')],[180,125,175])
p('Uncertainty uses paired daily P&L differences, seven-day moving blocks, 2,000 replications and seed 20261124. It resamples the observed 92-day regime and does not model new regimes, venue failure, model selection or execution misspecification. Intervals are descriptive and are not multiple-testing-adjusted. Forecast-versus-last-rate intervals are in paired_uncertainty.csv.')

page('08 / Margin is a separate survival problem')
table(['Holdout policy','Minimum sampled buffer','Minimum 8h-high proxy'],[[s+' / '+name,num(find(s,name)['minimum_sampled_margin_buffer']),num(find(s,name)['minimum_bar_high_margin_proxy'])] for s in ('BTCUSDT','ETHUSDT') for name in ('continuous','threshold')],[220,130,130])
p('The margin account does not automatically access gains in the spot wallet. The seven scenario cases cover negative funding, a basis widening, a joint 80% rally, half-filled spot, higher maintenance, a collateral haircut and a stablecoin depeg. In the joint rally the combined sleeve can retain most economic capital while isolated collateral fails.')
p('The bar-high proxy revalues the post-trade short at the maximum mark inside the following 8-hour bar, holding that row’s collateral fixed. It is an ex-post stress diagnostic. Its positive buffer does not certify absence of liquidation: the path of cash transfers, funding, tier changes and liquidation mechanics is not reconstructed. No intrabar event ordering is invented from OHLC.')
p('A sampled margin breach triggers a modeled unwind at sampled traded prices and stops new entries. This preserves a deficit instead of erasing it. Full fills on a forced close are an approximation; the stress case is not an exact exchange liquidation engine. Historical liquidation fees, insurance fund behavior, ADL, custody loss and venue default require separate evidence.')
p('USDT equals USD in the base replay. The depeg scenario translates economic equity into USD; collateral eligibility haircuts are modeled separately. Treating a collateral haircut as an immediate mark-to-market loss would mix two different mechanisms.')

page('09 / Operations, reproduction and decision')
p('The paper module is strictly read-only: public prices/funding in, hypothetical targets and receipts out. It contains no authenticated or order API. The first snapshot starts flat and cannot claim earlier funding. Later runs settle new funding on existing paper holdings before executing the prior target. A state lock, duplicate-time guard, funding-gap check, quote sanity check and event-level reconciliation fail closed.')
p('Operational check: GitHub CI passed. The hosted paper run returned HTTP 451 from Binance futures bookTicker; its schedule was removed and no successful paper state is claimed. The public dashboard and CSV export were checked in Chrome.')
p('Paper polling is coarser than live trading. Quotes are midpoint references with modeled slippage; funding is actually observed but fills are hypothetical. A changed cadence, stale quote, incomplete page or failed network request stops the update. Scheduled execution depends on endpoint access from the chosen runner. A successful workflow is operational evidence, never proof of a future return.')
table(['Reproduction','Command / artifact'],[['Verify engine','python3 -m unittest discover -s tests -v'],['Synthetic replay','python3 -m carry.run demo'],['Normalize preserved snapshots','python3 -m carry.market'],['Frozen market study','python3 -m carry.study'],['Read-only paper observation','python3 -m carry.paper'],['Receipts','artifacts/market/freeze.json and receipt.json']],[160,320])
p('<b>Decision:</b> retain continuous carry as the research benchmark and reject this naive threshold as an execution policy at the assumed fee schedule. Do not deploy from these results. The next study should price switching decisions against expected holding duration and friction, acquire execution-level observations and historical margin tiers, and accumulate a genuine forward paper record without recycling the consumed holdout.')
p('Primary sources: Binance public-data repository (github.com/binance/binance-public-data); Binance funding FAQ (binance.com/en/support/faq/detail/360033525031); official data-api.binance.vision/api/v3/klines; fapi.binance.com/fapi/v1/fundingRate, /klines, /markPriceKlines and /exchangeInfo. Snapshot URL parameters and individual hashes are in the private manifest. Report generated from run '+receipt['run_id']+'.')

def footer(c,doc):
    c.setStrokeColor(colors.HexColor('#ccd6d2'));c.line(48,45,547,45);c.setFont('Arial',8);c.setFillColor(colors.HexColor('#5c716b'));c.drawString(48,31,'Retrospective research | Hypothetical execution | 24 Nov 2026');c.drawRightString(547,31,str(doc.page))
doc=SimpleDocTemplate(str(OUT/'P3_Crypto_Carry_Research_Report.pdf'),pagesize=(595,842),rightMargin=55,leftMargin=55,topMargin=48,bottomMargin=60)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
(OUT/'P3_Crypto_Carry_Research_Report.md').write_text('\n\n'.join(markdown))
memo=f'''# P3 - Memo kết quả và quyết định

Ngày lập: 24/11/2026. Run `{receipt['run_id']}`. Đây là nghiên cứu hồi cứu năm 2025, không phải lợi nhuận giao dịch thật.

## Kết quả cần nhớ

Mỗi tài sản/chính sách có sleeve riêng 100.000 USDT. Holdout là 01/10-31/12/2025, reset vốn đầu kỳ và đóng vị thế cuối kỳ.

| Chính sách | BTC net P&L | ETH net P&L |
|---|---:|---:|
| Giữ carry liên tục | {num(find('BTCUSDT','continuous')['net_pnl'])} | {num(find('ETHUSDT','continuous')['net_pnl'])} |
| Bật/tắt theo funding gần nhất | {num(find('BTCUSDT','threshold')['net_pnl'])} | {num(find('ETHUSDT','threshold')['net_pnl'])} |
| Dự báo bằng mean 9 kỳ | {num(find('BTCUSDT','forecast_rolling_mean')['net_pnl'])} | {num(find('ETHUSDT','forecast_rolling_mean')['net_pnl'])} |
| Ridge AR(1) | {num(find('BTCUSDT','forecast_ridge_ar1')['net_pnl'])} | {num(find('ETHUSDT','forecast_ridge_ar1')['net_pnl'])} |

Threshold đổi vị thế quá nhiều nên phí lớn hơn funding thu được. Dự báo mượt hơn giảm đổi vị thế, nhưng vẫn lỗ và chưa vượt carry liên tục. Sai số dự báo thấp hơn không tự động tạo lợi nhuận tốt hơn. Không chỉnh threshold sau khi nhìn holdout; nếu thử hysteresis/cost-aware entry thì phải lập study mới.

## Bằng chứng đã có

- BTC/ETH: đủ 1.095 funding events và 1.095 bars cho từng stream spot/perp/mark trong 2025; không thiếu/trùng kỳ.
- 93 funding events BTC tháng 1 khớp archive/API về cả timestamp và rate.
- 18 tests; 13.140 dòng ledger cho 6 policy variants × 3 partitions × 2 assets. Sai số đối soát tối đa dưới 1e-9 USDT.
- Freeze hash trước khi xem kết quả; ba partition; paired block bootstrap; cost ×1/×2/×3 và delay 1/2/3 events.
- Workbook có công thức và golden case độc lập; dashboard giữ các kết quả âm.

## Giới hạn và bước tiếp

Giá tham chiếu là open bar 8 giờ, funding có timestamp thực; độ lệch tối đa 16 ms. Fill, fee tier và flat maintenance là giả định. Bar-high margin chỉ là proxy, không chứng minh không bị thanh lý. Đơn vị P&L là USDT, không phải USD bảo đảm. Chưa có bằng chứng depth/capacity, tier margin lịch sử hay forward track record.

Paper collector chỉ đọc dữ liệu công khai, ghi vị thế giả lập, không gửi lệnh và không cần API key. Không thể tạo trước một chuỗi kết quả tương lai. Trạng thái triển khai/runner thực tế được ghi riêng trong `docs/STATUS_VI.md`.

Kết luận: giữ carry liên tục làm benchmark; bác bỏ threshold đơn giản ở bộ giả định chi phí hiện tại. Giá trị portfolio của P3 là một quy trình nghiên cứu kiểm chứng được, bao gồm kết quả âm và giới hạn thực thi.
'''
(OUT/'P3_Decision_Memo_VI.md').write_text(memo)
print('Report and memo written')
