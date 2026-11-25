.PHONY: sample validate notebooks reproduce review dashboard workbook report release
sample:
	python3 -m carry.run demo
validate:
	python3 -m unittest discover -s tests -v
notebooks:
	python3 scripts/build_notebooks.py
reproduce:
	python3 -m carry.reproduce
review:
	python3 -m scripts.prepare_review
dashboard:
	python3 -c "from pathlib import Path; from carry.web import build_dashboard; build_dashboard(Path('artifacts/market'))"
workbook:
	node scripts/build_workbook.mjs
report:
	python3 scripts/build_report.py
release:
	python3 scripts/export_public.py
