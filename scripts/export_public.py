"""Curated public export; raw/normalized markets and price-level ledger omitted."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'p3-public'
OUT.mkdir(exist_ok=True)
for name in ('carry','tests','scripts','notebooks','docs','reports','deliverables'):
 for p in (ROOT/name).rglob('*'):
  if not p.is_file() or any(x in ('__pycache__','node_modules') for x in p.parts) or p.suffix in ('.png','.ndjson','.pyc') or p.name.startswith('~$'):continue
  dest=OUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
for name in ('README.md','pyproject.toml','Makefile','.gitignore'):
 shutil.copyfile(ROOT/name,OUT/name)
for category in ('demo','market'):
 for p in (ROOT/'artifacts'/category).glob('*'):
  if not p.is_file():continue
  if category=='market' and p.name in ('ledger.csv','trades.csv','dashboard_data.json','dashboard.html'):continue
  if category=='demo' and p.name=='dashboard.html':continue
  dest=OUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
# Public dashboard exports derived P&L fields without normalized price/rate stream.
payload=json.loads((ROOT/'artifacts/market/dashboard_data.json').read_text())
for row in payload['ledger']:
 for key in ('spot','perp','mark','settled_funding_rate'):row.pop(key,None)
html=(ROOT/'artifacts/market/dashboard.html').read_text()
a=html.index('const data=')+len('const data=');b=html.index(';const $=',a)
html=html[:a]+json.dumps(payload,separators=(',',':'))+html[b:]
(OUT/'index.html').write_text(html)
(OUT/'.nojekyll').write_text('')
files=[p for p in OUT.rglob('*') if p.is_file()]
(OUT/'public_manifest.json').write_text(json.dumps({'version':'0.2.0','excluded':'raw and normalized market snapshots; price-level ledgers; private paper state','sha256':{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}},indent=2))
print(json.dumps({'path':str(OUT),'files':len(files)+1}))
