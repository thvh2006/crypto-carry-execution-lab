# Reproduction and operations runbook

## Public review without network access

Use Python 3.9+ from the repository root. Engine/tests/notebook generation have no third-party Python dependencies. Interactive notebook viewing requires Jupyter/IPython.

```sh
python3 -m unittest discover -s tests -v
python3 -m carry.run demo
python3 scripts/build_notebooks.py
```

The notebooks execute calculations and deterministic cases, render actual tables/SVGs, and explain published market evidence. Public aggregate evidence is sufficient for this review path; it is not a full market replay.

## Exact original study reproduction

With the preserved private snapshot placed under `data/market/`:

```sh
python3 -m carry.reproduce --verify-only
python3 -m carry.reproduce --out artifacts/reproduction
```

The exact byte baseline used Python 3.9.6. Newer Python versions can change floating-point summation in forecast error summaries. An explicit separate `--allow-numeric-equivalence` run checks fixed absolute 1e-9 / relative 1e-12 tolerances and labels any differences; it never claims byte identity.

The second command runs immutable source in a temporary isolated tree, checks all seven output CSV hashes, and writes `reproduction_receipt.json`. The original freeze, CSVs and published receipt are never replaced. `python3 -m carry.study` delegates to this reproduction path in release 0.3. Do not delete a freeze to make a changed study pass.

If raw snapshots are available, `python3 -m carry.market` deterministically restores normalized files. The acquisition time is preserved when raw hashes match. To reacquire publicly where the provider permits access, use `python3 -m carry.acquire --install-equivalent`. A changed provider snapshot is preserved as a candidate and is not silently accepted as the original.

## Rebuild descriptive analysis and deliverables

```sh
python3 -m scripts.prepare_review
python3 scripts/design_notebooks.py
python3 scripts/build_notebooks.py
python3 scripts/build_report.py
node scripts/build_workbook.mjs
python3 scripts/export_public.py
```

`prepare_review` requires the private original ledger, fills and normalized prices. It derives post-study diagnostics without choosing a new strategy. Report authoring additionally needs ReportLab and installed Times New Roman fonts (`P3_TIMES_FONT_DIR` can identify their directory). Workbook authoring needs the provided artifact runtime; the delivered XLSX has native formulas/charts and opens independently. See `environment.json` for the authoring environment.

## Paper loop: blocked on the hosted runner

`python3 -m carry.paper` uses public quote, mark and settled-funding endpoints only. No private keys or order endpoints are accepted. Its first observation starts flat, creates an epoch and records a target for a later observation. Subsequent steps settle new funding, execute previous hypothetical intent, reconcile equity, and retain intent/fill details.

Non-finite inputs, future/duplicate funding, stale quotes, funding gaps, changed cadence, incomplete pagination and duplicate observations stop updates. Preserve `paper/state/` and its epoch. Cache loss must be treated as a new paper run, never a continuation of the old track record. A state lock prevents concurrent local runs; investigate a stale lock before removing it after a crash.

The retained GitHub-hosted run failed with HTTP 451 at futures bookTicker. Its cron schedule is omitted, leaving a manual workflow for a permitted environment check. No successful forward paper state or performance is claimed. Do not bypass provider restrictions or substitute assumed data. Archive incidents and preserve the last-known-good state.

## Release and recovery

1. Run tests, public notebook smoke build, exact reproduction where private data are available, and workbook input/recalculation checks.
2. Confirm report/workbook/dashboard reference the same original run and separate historical/scenario/paper labels.
3. Export only reviewed public derived fields; verify local relative links and artifact hashes.
4. Publish source and static dashboard. Check deployed selectors, tables, calculator and CSV downloads.
5. Retain the previous GitHub commit and private evidence version. Restore a known commit if a publication fails; never label a failed collection current.
