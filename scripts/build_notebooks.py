"""Execute standard-library review cells and save nbformat 4 notebooks."""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

NOTEBOOKS = json.loads((ROOT/'scripts/market_notebook_cells.json').read_text())

destination = ROOT / 'notebooks'
destination.mkdir(exist_ok=True)
for slug, title, codes in NOTEBOOKS:
    cells = [{"cell_type": "markdown", "metadata": {}, "source": [f"# {title}\n", "Audited retrospective market evidence. Run from the repository root or notebooks directory. Python standard library. Hypothetical fills; no forward return claim.\n"]}]
    namespace = {}
    # Each notebook executes from a clean namespace, using the delivered package.
    setup = "from pathlib import Path\nimport os,sys\nroot=Path.cwd()\nif not (root/'carry').exists():\n    root=root.parent\nos.chdir(root)\nsys.path.insert(0,str(root))"
    for index, code in enumerate([setup] + codes, start=1):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(compile(code, slug, 'exec'), namespace)
        outputs = []
        for name, stream in [('stdout',stdout),('stderr',stderr)]:
            if stream.getvalue():
                outputs.append({"output_type":"stream","name":name,"text":stream.getvalue().splitlines(keepends=True)})
        cells.append({"cell_type":"code","execution_count":index,"metadata":{},"source":code.splitlines(keepends=True),"outputs":outputs})
    notebook = {"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":sys.version.split()[0]}},"nbformat":4,"nbformat_minor":4}
    (destination / (slug+'.ipynb')).write_text(json.dumps(notebook,indent=2))
print('Executed',len(NOTEBOOKS),'notebooks from clean namespaces')
