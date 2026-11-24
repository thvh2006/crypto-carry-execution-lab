import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(root,'deliverables/excel');
await fs.mkdir(out,{recursive:true});
const wb=Workbook.create();
const start=wb.worksheets.add('Start Here');
const model=wb.worksheets.add('Mechanics');
const settlements=wb.worksheets.add('Settlements');
const snapshot=wb.worksheets.add('Replay Snapshot');
const audit=wb.worksheets.add('Audit');
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
snapshot.getRange('B6:H11').values=data.summary.map(s=>[s.symbol,s.policy,s.net_pnl,s.funding,s.fees,s.return_on_total_capital,s.max_drawdown]);
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
wb.recalculate();
const base=model.getRange('F14').values[0][0];
if(Math.abs(base-golden.pnl)>1e-6)throw new Error('Golden mismatch '+base+' vs '+golden.pnl);
model.getRange('C9').values=[[1]];wb.recalculate();const changed=model.getRange('F14').values[0][0];
if(Math.abs(changed-base)<1)throw new Error('Input did not recalculate');
model.getRange('C9').values=[[0.5]];wb.recalculate();
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:20},summary:'Formula errors'})).ndjson);
for(const sheet of [start,model,settlements,snapshot,audit]){
 const blob=await wb.render({sheetName:sheet.name,range:sheet===model?'B2:H21':'B2:H18',scale:1,format:'png'});
 await fs.writeFile(path.join(out,sheet.name.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'P3_Carry_Review.xlsx'));
console.log(JSON.stringify({goldenPnl:base,changedFillPnl:changed,workbook:'P3_Carry_Review.xlsx'}));
