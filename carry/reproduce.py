"""Reproduce the consumed v1 study without replacing its original evidence."""
import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from .run import ROOT


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    freeze = json.loads((root / 'artifacts/market/freeze.json').read_text())
    for relative, expected in freeze['sha256'].items():
        path = root / relative
        if relative.startswith('carry/'):
            path = root / 'artifacts/market/frozen_source' / relative
        if not path.is_file():
            raise ValueError('Private snapshot or frozen source missing: ' + relative)
        if digest(path) != expected:
            raise ValueError('Frozen input changed: ' + relative)
    return freeze


def compare_numeric(reference, candidate):
    with reference.open() as left, candidate.open() as right:
        a, b = list(csv.reader(left)), list(csv.reader(right))
    if len(a) != len(b) or a[0] != b[0]:
        raise ArithmeticError('CSV schema or row count differs')
    maximum = 0.0
    for ra, rb in zip(a[1:], b[1:]):
        if len(ra) != len(rb):
            raise ArithmeticError('CSV row shape differs')
        for x, y in zip(ra, rb):
            if x == y:
                continue
            try:
                u, v = float(x), float(y)
            except ValueError:
                raise ArithmeticError('Non-numeric CSV value differs')
            if not math.isfinite(u) or not math.isfinite(v) or not math.isclose(u, v, abs_tol=1e-9, rel_tol=1e-12):
                raise ArithmeticError('Numeric CSV difference exceeds fixed tolerance')
            maximum = max(maximum, abs(u-v))
    return maximum


def reproduce(out, verify_only=False, allow_numeric_equivalence=False):
    freeze = verify()
    if verify_only:
        return {'status': 'verified', 'frozen_files': len(freeze['sha256'])}
    out = out.resolve()
    baseline = (ROOT / 'artifacts/market').resolve()
    if out == baseline or baseline in out.parents:
        raise ValueError('Reproduction output must not replace baseline artifacts')
    expected = json.loads((baseline / 'baseline_outputs.json').read_text())
    with tempfile.TemporaryDirectory(prefix='p3-frozen-replay-') as tmp:
        stage = Path(tmp)
        shutil.copytree(baseline / 'frozen_source/carry', stage / 'carry')
        shutil.copytree(ROOT / 'data/market', stage / 'data/market')
        (stage / 'docs').mkdir()
        shutil.copyfile(ROOT / 'docs/STUDY_PROTOCOL_V1.md', stage / 'docs/STUDY_PROTOCOL_V1.md')
        for kind in ('demo', 'market'):
            (stage / 'artifacts' / kind).mkdir(parents=True)
        shutil.copyfile(baseline / 'freeze.json', stage / 'artifacts/market/freeze.json')
        shutil.copyfile(ROOT / 'artifacts/demo/dashboard_data.json', stage / 'artifacts/demo/dashboard_data.json')
        subprocess.run([sys.executable, '-m', 'carry.study'], cwd=stage, check=True, capture_output=True, text=True)
        comparisons = {}
        actual_hashes = {}
        for name, sha in expected.items():
            actual_hashes[name] = digest(stage / 'artifacts/market' / name)
            if digest(stage / 'artifacts/market' / name) != sha:
                if not allow_numeric_equivalence:
                    raise ArithmeticError('Reproduced CSV bytes differ: ' + name + '. Exact baseline used Python 3.9.6; inspect a separate --allow-numeric-equivalence run for newer Python floating-point differences.')
                comparisons[name] = dict(method='numeric equivalence', max_absolute_difference=compare_numeric(baseline/name, stage/'artifacts/market'/name))
            else:
                comparisons[name] = dict(method='byte exact', max_absolute_difference=0.0)
        out.mkdir(parents=True, exist_ok=True)
        for path in (stage / 'artifacts/market').iterdir():
            if path.is_file():
                shutil.copyfile(path, out / path.name)
    receipt = {
        'status': 'numeric-equivalent CSV reproduction' if any(v['method']=='numeric equivalence' for v in comparisons.values()) else 'exact CSV reproduction', 'original_run_id': 'eed008040d6c6d18',
        'original_freeze_sha256': digest(baseline / 'freeze.json'),
        'original_output_sha256': expected, 'reproduced_output_sha256': actual_hashes, 'python': sys.version.split()[0],
        'reproduced_at': datetime.now(timezone.utc).isoformat(),
        'source_scope': 'Original immutable source; no model tuning or new holdout claim',
        'comparisons': comparisons, 'numeric_tolerance': {'absolute':1e-9,'relative':1e-12} if allow_numeric_equivalence else None,
    }
    (out / 'reproduction_receipt.json').write_text(json.dumps(receipt, indent=2))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'artifacts/reproduction')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--allow-numeric-equivalence', action='store_true', help='Separate explicit tolerance check across Python floating-point implementations; never relabeled byte-exact')
    args = parser.parse_args()
    print(json.dumps(reproduce(args.out, args.verify_only, args.allow_numeric_equivalence), indent=2))


if __name__ == '__main__':
    main()
