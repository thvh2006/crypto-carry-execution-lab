"""Check published file identities, relative links and frozen source availability."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT);args=parser.parse_args();root=args.root.resolve()
 manifest=json.loads((root/'public_manifest.json').read_text());errors=[]
 for relative,expected in manifest['sha256'].items():
  p=root/relative
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Published hash mismatch: '+relative)
 for p in root.rglob('*.md'):
  if 'node_modules' in p.parts or '.git' in p.parts:continue
  for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if not dest.startswith(('http:','https:','mailto:','#','sandbox:')) and not (p.parent/dest.split('#')[0]).exists():errors.append('Broken link: '+str(p.relative_to(root))+' -> '+dest)
 freeze=json.loads((root/'artifacts/market/freeze.json').read_text())
 for relative,expected in freeze['sha256'].items():
  if relative.startswith('carry/'):p=root/'artifacts/market/frozen_source'/relative
  elif relative.startswith('docs/'):p=root/relative
  else:continue
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Frozen source/protocol mismatch: '+relative)
 source=json.loads((root/'artifacts/review/receipt.json').read_text())
 for relative,expected in source['source_sha256'].items():
  p=root/'artifacts/market'/relative
  if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Review source changed: '+relative)
 for name in ('ledger.csv','trades.csv','dashboard_data.json'):
  if (root/'artifacts/market'/name).exists():errors.append('Private market artifact in public export: '+name)
 if (root/'data/market').exists() or (root/'data/raw').exists():errors.append('Private provider data present in public export')
 if errors:raise SystemExit('\n'.join(errors))
 print(json.dumps({'status':'verified','published_files':len(manifest['sha256']),'relative_links':'valid','frozen_source_and_protocol':'valid','raw_market_data':'excluded'}))
if __name__=='__main__':main()
