import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'deliverables/excel');
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const review=wb.worksheets.add('Review');
const scenario=wb.worksheets.add('Scenario');
const sensitivity=wb.worksheets.add('Cost Review');
const trend=wb.worksheets.add('Selected Trend');
const start=wb.worksheets.add('Start Here');
const model=wb.worksheets.add('Mechanics');
const settlements=wb.worksheets.add('Settlements');
const snapshot=wb.worksheets.add('Replay Snapshot');
const audit=wb.worksheets.add('Audit');
const history=wb.worksheets.add('History');
const costSource=wb.worksheets.add('Cost Source');
for(const sheet of [start,model,settlements,snapshot,audit]){
  sheet.showGridLines=false;
  sheet.getRange('A1:J40').format.font={name:'Arial',size:11,color:'#172E29'};
  sheet.getRange('A1:J40').format.rowHeight=23;
  sheet.getRange('A1:A40').format.columnWidth=3;
  sheet.getRange('B1:B40').format.columnWidth=43;
  sheet.getRange('C1:J40').format.columnWidth=18;
  sheet.freezePanes.freezeRows(5);
}
function title(sheet,text){sheet.getRange('B2').values=[[text]];sheet.getRange('B2').format.font={name:'Arial',size:20,bold:true};}
function band(sheet,address){sheet.getRange(address).format={fill:'#213F38',font:{name:'Arial',bold:true,color:'#FFFFFF'},rowHeight:27};}
title(start,'Crypto carry review');
start.getRange('B5:D11').values=[
 ['Worksheet','Use','Status'],
 ['Mechanics','Edit blue inputs','Independent scenario'],
 ['Settlements','Inspect funding cash flows','Three synthetic settlements'],
 ['Replay Snapshot','Compare engine outputs','Imported 2025 holdout snapshot'],
 ['Audit','Compare with Python golden case','Default input reconciliation'],
 ['Market replay','2025 BTC/ETH audit complete','Retrospective, hypothetical fills'],
 ['Currency','USDT base currency','USD peg assumed in this workbook']
];
start.getRange('C5:C15').format.columnWidth=40;start.getRange('D5:D15').format.columnWidth=42;
band(start,'B5:D5');start.getRange('B14').values=[['Blue inputs are editable. Black formulas calculate the scenario. Green formulas link sheets.']];
start.getRange('B16').values=[['Start with Mechanics. Change spot fill, closing prices or maintenance rate to inspect hedge and margin.']];
start.getRange('B18').values=[['Funding and fee inputs are assumptions. Venue-exact liquidation and forward performance remain unverified.']];
title(model,'Two-leg mechanics');
model.getRange('B5:C5').values=[['Scenario input','Value']];band(model,'B5:C5');
const inputs=[['Initial capital',100000],['Spot wallet fraction',0.65],['Desired base quantity',550],['Spot fill fraction',0.5],['Spot entry price',100],['Perp short entry price',100],['Spot closing price',100],['Perp closing price',105],['Spot fee each side (bps)',10],['Perp fee each side (bps)',5],['Maintenance rate',0.05],['Closing reserve (bps)',10]];
model.getRange('B6:C17').values=inputs;
model.getRange('C6:C17').format.font.color='#0000FF';
model.getRange('C7').setNumberFormat('0.0%');model.getRange('C9').setNumberFormat('0.0%');model.getRange('C16').setNumberFormat('0.0%');
model.getRange('C9').dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};
model.getRange('E5:F5').values=[['Calculated result','USDT unless stated']];band(model,'E5:F5');model.getRange('E1:E40').format.columnWidth=40;
const labels=['Spot quantity (units)','Short perp quantity (units)','Residual delta (units)','Spot P&L','Perp P&L','Funding cash','Spot fees','Perp fees','Net P&L','Closing equity','Return on total capital','Initial perp collateral','Margin buffer before closing'];
model.getRange('E6:E18').values=labels.map(x=>[x]);
const formulas=['=C8*C9','=-C8','=SUM(F6:F7)','=F6*(C12-C10)','=F7*(C13-C11)',"='Settlements'!H9",'=F6*(C10+C12)*C14/10000','=ABS(F7)*(C11+C13)*C15/10000','=SUM(F9:F11)-SUM(F12:F13)','=C6+F14','=F14/C6','=C6*(1-C7)','=F17-ABS(F7)*C11*C15/10000+F10+F11-ABS(F7)*C13*(C16+C17/10000)'];
model.getRange('F6:F18').formulas=formulas.map(x=>[x]);
model.getRange('F6:F18').setNumberFormat('#,##0.00;(#,##0.00);0.00');model.getRange('F16').setNumberFormat('0.00%');model.getRange('F11').format.font.color='#008000';
model.getRange('E21').values=[['Default case includes partial spot fill, negative funding, a basis gap and 5% maintenance.']];
model.getRange('B24').values=[['Source conventions']];
model.getRange('B25').values=[['Synthetic educational inputs. Fees and margin rates are scenario assumptions.']];
model.getRange('B27').values=[['Funding convention verified against Binance funding documentation, accessed 24 Nov 2026.']];
model.getRange('B28').values=[['https://www.binance.com/en/support/faq/detail/360033525031']];
title(settlements,'Funding settlements');
settlements.getRange('B5:H5').values=[['Settlement UTC','Mark price','Funding rate','Perp quantity','Funding cash','Cumulative funding','Margin buffer']];band(settlements,'B5:H5');
settlements.getRange('B6:D8').values=[[new Date('2025-01-01T08:00:00Z'),100,0.001],[new Date('2025-01-01T16:00:00Z'),102,-0.002],[new Date('2025-01-02T00:00:00Z'),105,0.001]];
settlements.getRange('B6:B8').setNumberFormat('dd-mmm hh:mm');settlements.getRange('D6:D8').setNumberFormat('0.000%');
settlements.getRange('C6:D8').format.font.color='#0000FF';
for(let r=6;r<=8;r++){
  settlements.getRange(`E${r}:H${r}`).formulas=[[
   "='Mechanics'!F7",`=-E${r}*C${r}*D${r}`,`=SUM($F$6:F${r})`,
   `='Mechanics'!F17-ABS(E${r})*'Mechanics'!C11*'Mechanics'!C15/10000+E${r}*(C${r}-'Mechanics'!C11)+G${r}-ABS(E${r})*C${r}*('Mechanics'!C16+'Mechanics'!C17/10000)`]];
}
settlements.getRange('G9').values=[['Total funding']];settlements.getRange('H9').formulas=[['=SUM(F6:F8)']];
settlements.getRange('E6:E8').format.font.color='#008000';settlements.getRange('H6:H8').format.font.color='#008000';
settlements.getRange('E6:H9').setNumberFormat('#,##0.00;(#,##0.00);0.00');
settlements.getRange('B12').values=[['Existing short positions receive positive rates. Settlement mark determines notional.']];
title(snapshot,'2025 holdout replay comparison');
const data=JSON.parse(await fs.readFile(path.join(root,'artifacts/market/dashboard_data.json'),'utf8'));
snapshot.getRange('B5:H5').values=[['Asset','Policy','Net P&L','Funding','Fees','Return on capital','Max drawdown']];band(snapshot,'B5:H5');
snapshot.getRange('B6:H11').values=data.summary.filter(s=>s.partition==='holdout'&&['spot','continuous','threshold'].includes(s.policy)).map(s=>[s.symbol,s.policy,s.net_pnl,s.funding,s.fees,s.return_on_total_capital,s.max_drawdown]);
snapshot.getRange('D6:F11').setNumberFormat('#,##0.00;(#,##0.00);0.00');snapshot.getRange('G6:H11').setNumberFormat('0.00%');
snapshot.getRange('B14').values=[['Imported engine snapshot. Editing Mechanics recalculates its independent scenario.']];
snapshot.getRange('B16').values=[['As of '+data.receipt.as_of+' UTC. Every policy uses a separate 100,000 USDT sleeve.']];
title(audit,'Independent reconciliation');
const golden=JSON.parse(await fs.readFile(path.join(root,'artifacts/demo/golden.json'),'utf8'));
audit.getRange('B5:E5').values=[['Default case output','Workbook','Python golden','Difference']];band(audit,'B5:E5');
audit.getRange('B6:B9').values=[['Net P&L'],['Closing equity'],['Funding'],['Residual delta units']];
audit.getRange('C6:C9').formulas=[["='Mechanics'!F14"],["='Mechanics'!F15"],["='Mechanics'!F11"],["='Mechanics'!F8"]];
audit.getRange('D6:D9').values=[[golden.pnl],[golden.equity],[golden.funding],[golden.delta]];
audit.getRange('E6').formulas=[['=C6-D6']];audit.getRange('E6:E9').fillDown();audit.getRange('C6:E9').setNumberFormat('0.00');
audit.getRange('B12').values=[['Golden values apply to default inputs. Changes to Mechanics create a new scenario.']];
audit.getRange('B14').values=[['Python checks use Account trades and three funding settlements independently of Excel formulas.']];
for(const sheet of [model,settlements,audit])sheet.getRange('B5:J40').format.rowHeight=25;

// POLISHED_REVIEW
const source=JSON.parse(await fs.readFile(path.join(root,'artifacts/review/workbook_inputs.json'),'utf8'));
const money='#,##0.00;(#,##0.00);"-"';
function setup(s,range='B2:K42'){
 s.showGridLines=false;s.getRange(range).format.font={name:'Arial',size:11,color:'#172E29'};
 s.getRange(range).format.rowHeight=24;s.getRange('A1:A42').format.columnWidth=3;
 s.getRange('B1:B42').format.columnWidth=33;s.getRange('C1:K42').format.columnWidth=17;
}
function chart(s,type,ranges,caption,first,last){
 const c=s.charts.add(type,ranges);c.title=caption;c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=14;
 c.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:11}};
 c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
 c.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
 c.setPosition(first,last);return c;
}
for(const s of [review,scenario,sensitivity,trend])setup(s);
review.tabColor='#213F38';scenario.tabColor='#658778';
title(review,'Historical carry review');review.getRange('B3:J3').merge();
review.getRange('B3').values=[['2025 frozen study. Each asset-policy-partition is a separate 100,000 USDT sleeve.']];
review.getRange('B5:C7').values=[['Asset','BTCUSDT'],['Partition','holdout'],['Policy','continuous']];
review.getRange('C5:C7').format.font.color='#0000FF';
for(const [cell,values] of [['C5',['BTCUSDT','ETHUSDT']],['C6',['development','validation','holdout']],['C7',['spot','continuous','threshold','forecast_last_rate','forecast_rolling_mean','forecast_ridge_ar1']]])review.getRange(cell).dataValidation={rule:{type:'list',values}};
review.getRange('C42').formulas=[['=C5&"|"&C6&"|"&C7']];
review.getRange('C43').formulas=[["=MATCH(C42,'Replay Snapshot'!$A$6:$A$41,0)"]];
review.getRange('B42:C43').format.font.color='#69766D';
const rs=(col)=>`INDEX('Replay Snapshot'!$${col}$6:$${col}$41,$C$43)`;
review.getRange('E5:F12').values=[['Selected historical result','USDT unless stated'],['Net P&L',null],['Return on total capital',null],['Funding received',null],['Fees',null],['Max drawdown',null],['Trade fills',null],['Minimum sampled margin buffer',null]];
band(review,'E5:F5');review.getRange('E1:E42').format.columnWidth=37;
for(const [r,c] of [[6,'E'],[7,'J'],[8,'F'],[9,'I'],[10,'K'],[11,'L'],[12,'O']])review.getRange('F'+r).formulas=[['='+rs(c)]];
review.getRange('F6:F12').setNumberFormat(money);review.getRange('F7').setNumberFormat('0.00%');review.getRange('F10').setNumberFormat('0.00%');review.getRange('F11').setNumberFormat('0');
review.getRange('B10:C16').values=[['P&L attribution','USDT'],['Spot P&L',null],['Perp P&L',null],['Funding',null],['Fees (deduction)',null],['Net P&L',null],['Accounting difference',null]];band(review,'B10:C10');
for(const [r,c] of [[11,'G'],[12,'H'],[13,'F']])review.getRange('C'+r).formulas=[['='+rs(c)]];
review.getRange('C14').formulas=[['=-F9']];review.getRange('C15').formulas=[['=SUM(C11:C14)']];review.getRange('C16').formulas=[['=C15-F6']];review.getRange('C11:C16').setNumberFormat(money);
review.getRange('B19:J19').merge();review.getRange('B19').values=[['Full-period drawdown comes from all events; trend chart samples 100 evenly spaced events.']];

review.getRange('B42:B43').values=[['Lookup key'],['Summary row']];
review.getRange('B39:J39').merge();review.getRange('B39').values=[['Scenario inputs do not alter frozen historical results. Open Scenario to test hypothetical economics.']];

// Expand the original imported snapshot to all 36 historical sleeve comparisons.
snapshot.getRange('B2:J18').clear({applyTo:'contents'});title(snapshot,'All historical policy comparisons');
snapshot.getRange('A5:O5').values=[['Key','Asset','Partition','Policy','Net P&L','Funding','Spot P&L','Perp P&L','Fees','Return','Max DD','Fills','History offset','Events','Min margin']];band(snapshot,'A5:O5');
snapshot.getRange('A6:O41').values=source.summary;snapshot.getRange('A1:A41').format.columnWidth=65;snapshot.getRange('D1:D41').format.columnWidth=30;
snapshot.getRange('E6:I41').setNumberFormat(money);snapshot.getRange('J6:K41').setNumberFormat('0.00%');snapshot.getRange('O6:O41').setNumberFormat(money);
snapshot.tables.add('A5:O41',true,'HistoricalPolicies');
snapshot.getRange('B44:K44').merge();snapshot.getRange('B44').values=[['Source: artifacts/market/summary.csv; immutable run eed008040d6c6d18. Imported results, not live backtest formulas.']];

// The private price-level ledger is reduced to derived account fields for this public workbook.
history.showGridLines=false;history.getRange('A5:K5').values=[['Sleeve key','Event UTC','Net P&L','Spot P&L','Perp P&L','Funding','Fees','Financing','Residual delta USDT','Margin buffer','Drawdown']];band(history,'A5:K5');
history.getRange('A6:K'+(source.history.length+5)).values=source.history;
history.getRange('A1:A8').format.columnWidth=64;history.getRange('B1:B8').format.columnWidth=25;history.getRange('C6:J'+(source.history.length+5)).setNumberFormat(money);history.getRange('K6:K'+(source.history.length+5)).setNumberFormat('0.00%');history.freezePanes.freezeRows(5);
history.getRange('B2:K2').merge();history.getRange('B2').values=[['Derived account history from frozen ledger. Raw prices and settled-rate stream are excluded.']];
history.tables.add('A5:K'+(source.history.length+5),true,'AccountHistory');
title(trend,'Selected historical trend');trend.getRange('B3:J3').merge();trend.getRange('B3').values=[['100 evenly spaced event observations, including the first and last event. Controls are on Review.']];
trend.getRange('L2').formulas=[['='+rs('M').replace('$C$43','Review!$C$43')]];trend.getRange('L3').formulas=[['='+rs('N').replace('$C$43','Review!$C$43')]];
trend.getRange('B5:I5').values=[['Event UTC','Net P&L','Funding','Fees','Residual delta USDT','Margin buffer','Drawdown','Source index']];band(trend,'B5:I5');
const tr=[];const hr=source.history.length+5;
for(let i=0;i<100;i++){
 const r=i+6;const index=`$L$2+1+ROUNDDOWN(($L$3-1)*${i}/99,0)`;
 tr.push([`=INDEX(History!$B$6:$B$${hr},${index})`,...['C','F','G','I','J','K'].map(c=>`=INDEX(History!$${c}$6:$${c}$${hr},${index})`),`=${index}`]);
}
trend.getRange('B6:I105').formulas=tr;trend.getRange('B1:B105').format.columnWidth=25;trend.getRange('C6:G105').setNumberFormat(money);trend.getRange('H6:H105').setNumberFormat('0.00%');trend.getRange('J5:K5').values=[['Event UTC','Net P&L']];
for(let i=0;i<100;i++){const r=i+6;trend.getRange('J'+r+':K'+r).formulas=[[(i%20===0||i===99)?'=LEFT(B'+r+',10)':'=""','=C'+r]];}
trend.freezePanes.freezeRows(5);
const reviewChart=chart(review,'line',trend.getRange('B5:C105'),'Net P&L (USDT)','B21','J37');reviewChart.hasLegend=false;reviewChart.xAxis={tickLabelInterval:20,tickLabelPosition:'low',majorGridlines:null,minorGridlines:null};reviewChart.series.items[0].line={fill:'#173e38',style:'solid',width:2};

title(scenario,'Two-leg scenario and capital stress');scenario.getRange('B3:J3').merge();scenario.getRange('B3').values=[['Hypothetical entry, three funding settlements and exit. Blue inputs recalculate this model only.']];
scenario.getRange('B5:C5').values=[['Editable driver','Input']];band(scenario,'B5:C5');
scenario.getRange('B6:C21').values=[['Total sleeve capital',100000],['Matched notional / capital',.55],['Spot wallet / capital',.65],['Spot entry reference',100],['Perp entry reference',100],['Spot exit reference',100],['Perp exit reference',105],['Spot fill fraction',.5],['Fee multiplier',1],['Adverse slippage (bps)',0],['Maintenance fraction',.05],['Close reserve (bps)',10],['Initial margin fraction',.1],['Financing APR',0],['Holding hours',24],['Flat-price funding per event',.0001]];
scenario.getRange('C6:C21').format.font.color='#0000FF';scenario.getRange('C6:C21').setNumberFormat('0.00');
for(const r of [7,8,13,16,18,19,21])scenario.getRange('C'+r).setNumberFormat('0.00%');
scenario.getRange('C13').dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};
scenario.getRange('E5:F5').values=[['Calculated build','USDT unless stated']];band(scenario,'E5:F5');scenario.getRange('E1:E45').format.columnWidth=40;
const slabel=['Desired base quantity','Filled spot units','Short perp units','Residual base units','Spot entry execution','Spot exit execution','Perp entry execution','Perp exit execution','Spot P&L','Perp P&L','Funding cash','Spot commissions','Perp commissions','Financing cost','Net P&L','Slippage embedded in leg P&L','Closing spot cash','Closing perp collateral','Closing equity','Return on total capital','Pre-close margin buffer','Extra eligible collateral needed','Total friction cost','Flat-price break-even events','Initial margin headroom'];
scenario.getRange('E6:E30').values=slabel.map(x=>[x]);
const sf=['=ROUNDDOWN(C6*C7/C9/0.001,0)*0.001','=F6*C13','=-F6','=SUM(F7:F8)','=C9*(1+C15/10000)','=C11*(1-C15/10000)','=C10*(1-C15/10000)','=C12*(1+C15/10000)','=F7*(F11-F10)','=F8*(F13-F12)',"=-F8*SUMPRODUCT('Settlements'!C6:C8,'Settlements'!D6:D8)",'=F7*(F10+F11)*10*C14/10000','=ABS(F8)*(F12+F13)*5*C14/10000','=F7*F10*C19*C20/8760','=SUM(F14:F16)-SUM(F17:F19)','=F7*(F10-C9+C11-F11)+ABS(F8)*(C10-F12+F13-C12)','=C6*C8+F14-F17-F19','=C6*(1-C8)+F15+F16-F18','=SUM(F22:F23)','=(F24-C6)/C6','=C6*(1-C8)-ABS(F8)*F12*5*C14/10000+F8*(C12-F12)+F16-ABS(F8)*C12*(C16+C17/10000)','=MAX(0,-F26)','=SUM(F17:F19)+F21','=IF(C21>0,ROUNDUP(F28/(ABS(F8)*C10*C21),0),NA())','=C6*(1-C8)-ABS(F8)*C10*C18-ABS(F8)*F12*5*C14/10000'];
scenario.getRange('F6:F30').formulas=sf.map(x=>[x]);scenario.getRange('F6:F30').setNumberFormat(money);scenario.getRange('F25').setNumberFormat('0.00%');
scenario.getRange('B24:C26').values=[['Quantity step assumption',.001],['Spot / perp fee per side (bps)','10 / 5'],['Funding marks / rates','Settlements!C6:D8']];
scenario.getRange('B44:J46').merge();scenario.getRange('B44').values=[['The model diagnoses funding, costs, cash and collateral. Cash or margin infeasibility must be resolved before treating a target as executable. Break-even assumes flat prices and a constant positive funding rate.']];scenario.getRange('B44:J46').format.wrapText=true;
scenario.getRange('B31:F31').merge();scenario.getRange('B31').values=[['Net P&L sensitivity: columns = fee multiplier; rows = adverse slippage bps']];
scenario.getRange('B33').formulas=[['=F20']];scenario.getRange('C33:F33').values=[[.5,1,2,3]];scenario.getRange('B34:B37').values=[[0],[2],[5],[10]];
scenario.dataTables.add('B33:F37',{rowInput:'C14',columnInput:'C15'});scenario.getRange('C34:F37').setNumberFormat(money);scenario.getRange('C34:F37').conditionalFormats.add('colorScale',{colors:['#F2D5D5','#FFFFFF','#BBD6C8']});
scenario.getRange('H6:I7').values=[['Execution feasibility','USDT'],['Opening cash headroom',null]];scenario.getRange('I7').formulas=[['=C6*C8-F7*F10*(1+10*C14/10000)']];scenario.getRange('I7').setNumberFormat(money);scenario.getRange('H1:H7').format.columnWidth=31;
scenario.getRange('B40:J41').merge();scenario.getRange('B40').values=[['Sources: independent mechanics; default 275 spot / -550 perp golden case. Fee and margin assumptions are not historical venue rules. Native Excel two-variable Data Table, not a copied sensitivity grid.']];scenario.getRange('B40:J41').format.wrapText=true;

title(sensitivity,'Historical transaction-cost review');sensitivity.getRange('B3:J3').merge();sensitivity.getRange('B3').values=[['Fixed policy replay at cost multiples 1, 2 and 3; fees and slippage scale together.']];
costSource.getRange('A5:F5').values=[['Key','Asset','Partition','Policy','Cost multiple','Net P&L']];band(costSource,'A5:F5');
costSource.getRange('A6:F'+(source.cost.length+5)).values=source.cost.map(r=>[[r.symbol,r.partition,r.policy,r.cost_multiple].join('|'),r.symbol,r.partition,r.policy,+r.cost_multiple,+r.net_pnl]);
costSource.getRange('A1:A7').format.columnWidth=70;costSource.getRange('D1:D7').format.columnWidth=30;costSource.getRange('F6:F'+(source.cost.length+5)).setNumberFormat(money);costSource.tables.add('A5:F'+(source.cost.length+5),true,'HistoricalCostRuns');
sensitivity.getRange('B5:E5').values=[['Current Review selection','Cost x1','Cost x2','Cost x3']];band(sensitivity,'B5:E5');
sensitivity.getRange('B6').formulas=[['=Review!C5&" / "&Review!C6&" / "&Review!C7']];
for(let m=1;m<=3;m++)sensitivity.getCell(5,m+1).formulas=[['=INDEX(\'Cost Source\'!$F$6:$F$113,MATCH(Review!$C$42&"|'+m+'",\'Cost Source\'!$A$6:$A$113,0))']];
sensitivity.getRange('C6:E6').setNumberFormat(money);
sensitivity.getRange('B10:D10').values=[['Cost multiple','BTC continuous','ETH continuous']];band(sensitivity,'B10:D10');
for(let i=0;i<3;i++){
 const r=11+i;sensitivity.getRange('B'+r).values=[[i+1]];
 for(const [c,symbol] of [['C','BTCUSDT'],['D','ETHUSDT']])sensitivity.getRange(c+r).formulas=[['=INDEX(\'Cost Source\'!$F$6:$F$113,MATCH("'+symbol+'|holdout|continuous|"&B'+r+',\'Cost Source\'!$A$6:$A$113,0))']];
}sensitivity.getRange('C11:D13').setNumberFormat(money);
chart(sensitivity,'line',sensitivity.getRange('B10:D13'),'Holdout continuous carry after costs (USDT)','B16','J31');
sensitivity.getRange('B34:J35').merge();sensitivity.getRange('B34').values=[['Cost x3 leaves BTC near break-even and ETH negative. This comparison is an imported historical rerun, separate from the native Scenario sensitivity.']];sensitivity.getRange('B34:J35').format.wrapText=true;

// Terminal checks observe builds; no output depends on Audit.
audit.getRange('B17:E17').values=[['Additional independent check','Workbook','Reference','Difference']];band(audit,'B17:E17');
audit.getRange('B18:B21').values=[['Scenario default net P&L'],['Scenario equity bridge'],['Selected historical bridge'],['Scenario default residual units']];
audit.getRange('C18:C21').formulas=[["=Scenario!F20"],["=Scenario!F24-Scenario!C6"],["=Review!C15"],["=Scenario!F9"]];
audit.getRange('D18:D21').values=[[golden.pnl],[null],[null],[golden.delta]];
audit.getRange('D19:D20').formulas=[["=Scenario!F20"],["=Review!F6"]];
for(let r=18;r<=21;r++)audit.getRange('E'+r).formulas=[[`=C${r}-D${r}`]];
audit.getRange('C18:E21').setNumberFormat('0.000000');
audit.getRange('E18:E21').conditionalFormats.add('cellIs',{operator:'notBetween',formula:[-.000001,.000001],format:{fill:'#FCE4D6',font:{color:'#A40000',bold:true}}});
start.getRange('B5:D11').values=[['Read in this order','Use','Status'],['Review','Select asset, partition and policy','Frozen historical outcomes'],['Scenario','Change blue model drivers','Independent formula model'],['Cost Review','Review historical cost fragility','Imported reruns + linked chart'],['Mechanics / Settlements','Inspect original golden case','Default independent reconciliation'],['Replay Snapshot / History','Trace all 36 sleeves and events','Imported derived account data'],['Audit','Review bridges and golden differences','Terminal checks']];
start.getRange('B14:J14').merge();start.getRange('B14').values=[['Blue inputs; black same-sheet formulas; green cross-sheet calculations. Audit differences apply to default golden inputs.']];
start.getRange('B16:J16').merge();start.getRange('B16').values=[['Scenario is hypothetical. Review and Cost Review are fixed historical results; changing Scenario does not rerun the backtest.']];
start.getRange('B18:J19').merge();start.getRange('B18').values=[['Study run eed008040d6c6d18. Data: 2025. Forward paper remains blocked by HTTP 451 on the hosted runner. No live trading.']];start.getRange('B18:J19').format.wrapText=true;
wb.recalculate();
const base=model.getRange('F14').values[0][0];
if(Math.abs(base-golden.pnl)>1e-6)throw new Error('Golden mismatch '+base+' vs '+golden.pnl);
model.getRange('C9').values=[[1]];wb.recalculate();const changed=model.getRange('F14').values[0][0];
if(Math.abs(changed-base)<1)throw new Error('Input did not recalculate');
model.getRange('C9').values=[[0.5]];wb.recalculate();
const scenarioBase=scenario.getRange('F20').values[0][0];
if(Math.abs(scenarioBase-golden.pnl)>1e-6)throw new Error('Scenario golden mismatch '+scenarioBase);
review.getRange('C5').values=[['ETHUSDT']];wb.recalculate();
if(Math.abs(trend.getRange('C105').values[0][0]-311.46356131575885)>1e-6)throw new Error('Trend selector mismatch');
if(Math.abs(review.getRange('F6').values[0][0]-311.46356131575885)>1e-6)throw new Error('Historical selector mismatch');
review.getRange('C5').values=[['BTCUSDT']];
scenario.getRange('C15').values=[[2]];wb.recalculate();const scenarioSlipped=scenario.getRange('F20').values[0][0];
if(scenarioSlipped>=scenarioBase)throw new Error('Slippage did not reduce scenario P&L');
scenario.getRange('C15').values=[[0]];wb.recalculate();
const nativeBase=scenario.getRange('D34').values[0][0];
if(Math.abs(nativeBase-scenarioBase)>1e-6)throw new Error('Native Data Table base mismatch '+nativeBase);
console.log(JSON.stringify({scenarioBase,scenarioSlipped,nativeBase,selectedHistoricalPnl:review.getRange('F6').values[0][0]}));
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#N/A|#CALC!',options:{useRegex:true,maxResults:20},summary:'Formula errors'})).ndjson);
for(const sheet of [review,scenario,sensitivity,trend,start,model,settlements,snapshot,audit,history,costSource]){
 const region=sheet===review?'B2:J39':sheet===scenario?'B2:J41':sheet===sensitivity?'B2:J35':sheet===history?'A2:K14':sheet===costSource?'A5:F16':sheet===snapshot?'A2:O17':sheet===trend?'B2:J18':sheet===audit?'B2:E23':sheet===model?'B2:H21':'B2:H19';
 const blob=await wb.render({sheetName:sheet.name,range:region,scale:1,format:'png'});
 await fs.writeFile(path.join(out,sheet.name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'P3_Carry_Review.xlsx'));
console.log(JSON.stringify({goldenPnl:base,changedFillPnl:changed,workbook:'P3_Carry_Review.xlsx'}));
