# Reproduction and next research gate

Engine, tests and the notebook builder run with stock Python 3.9+. The builder executes each notebook from a clean namespace and serializes its actual stream outputs in nbformat 4 JSON. Interactive notebook use requires a Jupyter-compatible application. Workbook rebuilding needs the OpenAI primary runtime with @oai/artifact-tool. The delivered workbook is self-contained and formula-driven in Excel.

Run tests, then demo CLI. Each demo overwrites its deterministic synthetic inputs and output tables. Input and config hashes identify the computation. `published_at` records the actual build time and `as_of` records fixture event time. A git commit is recorded when a committed checkout exists. Source hashes in the release manifest identify the delivered files.

For market work, preserve raw snapshots separately and normalize a small BTC sample first. Verify funding signs/times and mark/trade distinction, then do ETH. Freeze development/validation/locked periods and the experiment budget before any model search. Market mode runs supplied data as development replay and offers no locked-test certification.

Forward paper work requires a live collector with observation and receipt timestamps, frozen policy, append-only intended orders and simulated fills, actual funding receipts and daily reconciliation. This release contains the protocol and historical engine. It has no fabricated forward trades or scheduled refresh.

Before publishing, confirm market-data redistribution rights, run all tests and notebooks, rebuild workbook/dashboard from the same receipt and validate hosting. Preserve last-known-good artifacts if future refresh fails. Stop new signals on stale or incomplete input and retain the incident record. Scheduled refresh and rollback automation are pending.

## Market evidence and paper loop (release 0.2)

Run `python3 -m carry.market` against preserved JSON, then `python3 -m carry.study`. The study freezes source/config/data before the first result pass and rejects mismatches. To change a consumed study, create an explicitly amended protocol and output version; never delete the freeze to make it pass silently.

Run `python3 -m carry.paper` for public-data-only hypothetical observations. Preserve `paper/state/`; the first snapshot remains flat and cannot earn past funding. Use one process. A stale lock after a crash must be investigated before manual removal. Stale quotes, missing funding, a changed 8-hour cadence, 1,000-row truncation and duplicate observations stop updates. Network failure must not be substituted with zero funding or a successful-paper flag.

A daily/8-hour polling collector has modeled midpoint fills with slippage, not venue execution. No private exchange key is accepted. A scheduled runner must be tested from its own network: some hosting regions cannot reach Binance. Forward outcomes need real future elapsed time. Current collector test coverage proves initialization/timing mechanics only.
