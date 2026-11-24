"""Package source and verified sample outputs, excluding authoring previews."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT.parents[1] / 'outputs'
OUTPUT.mkdir(exist_ok=True)
excluded = {'__pycache__', '.git', 'node_modules', '.venv'}
files = [p for p in sorted(ROOT.rglob('*')) if p.is_file()
         and not any(part in excluded for part in p.relative_to(ROOT).parts)
         and p.suffix not in ('.pyc', '.png', '.ndjson')
         and p.name != 'release_manifest.json']
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest_path = ROOT / 'release_manifest.json'
manifest_path.write_text(json.dumps({'version':'0.1.0','status':'synthetic_validation','sha256':manifest},indent=2))
files.append(manifest_path)
archive = OUTPUT / 'P3_Crypto_Carry_Execution_Validation_2026-11-24.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
    for path in files:
        bundle.write(path, ROOT.name + '/' + str(path.relative_to(ROOT)))
with zipfile.ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert all(part not in bundle.namelist() for part in ('work/transfer.json',))
print(json.dumps({'path':str(archive),'files':len(files),'bytes':archive.stat().st_size,
                  'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
