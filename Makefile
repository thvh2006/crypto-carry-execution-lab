.PHONY: sample validate notebooks
sample:
	python3 -m carry.run demo
validate:
	python3 -m unittest discover -s tests -v
notebooks:
	python3 scripts/build_notebooks.py
