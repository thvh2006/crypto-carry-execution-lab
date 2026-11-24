# Crypto Carry & Execution Lab

**A funding filter can lose more to switching costs than it earns in funding.** This project measures that trade-off with separate spot/perpetual accounts, causal forecasts and auditable capital accounting.

[Interactive dashboard](https://thvh2006.github.io/crypto-carry-execution-lab/) · [10-page research report](reports/results/P3_Crypto_Carry_Research_Report.pdf) · [Decision memo (VI)](reports/results/P3_Decision_Memo_VI.md) · [Excel model](deliverables/excel/P3_Carry_Review.xlsx)

## Result

Fixed October–December 2025 historical holdout. Each asset/policy is a separate **100,000 USDT** sleeve, with 55% desired matched spot exposure. Executions are hypothetical 8-hour bar-open references with fees and adverse slippage.

| Policy | BTC net P&L, USDT | ETH net P&L, USDT |
|---|---:|---:|
| Continuous carry | 374.27 | 311.46 |
| Last-settled-rate threshold | -8,137.40 | -10,252.43 |
| Nine-period mean forecast + threshold | -1,255.39 | -1,147.12 |
| Ridge AR(1) forecast + threshold | -4,334.24 | -3,858.67 |

Smoothing reduces turnover and losses relative to the naive filter. Neither forecast strategy beats continuous carry in this holdout. This does not establish a deployable edge. Negative results are retained.

![BTC historical holdout](artifacts/market/BTCUSDT_holdout.svg)

## Evidence

- Official Binance public snapshots: **1,095 funding events and 1,095 spot/perp/mark bars per asset**, calendar 2025. No missing or duplicate nominal event. January BTC funding archive/API cross-check: 93/93 timestamps and rates match.
- Development Jan–Jun, validation Jul–Sep, historical holdout Oct–Dec. Written protocol and source/config/input hashes frozen before the first strategy-return inspection. Retrospective research, not forward performance.
- Three trading baselines, three matched causal forecast families, cost ×1/×2/×3, execution delays, seven-day paired block bootstrap, margin and operational stresses.
- **18 tests**, four executed notebooks and **13,140 event ledger rows**, with maximum accounting residual below 1e-9 USDT.
- Independent formula-driven Excel case reconciles funding, four commissions, partial fill and a basis gap to Python. Imported market snapshot is separate from editable mechanics.

## Reproduce

Engine, study and tests use Python 3.9+ standard library. No API key or trading account required.

```sh
python3 -m unittest discover -s tests -v
python3 -m carry.run demo
python3 scripts/build_notebooks.py
```

The public source export includes aggregate study evidence and synthetic fixtures. Raw/normalized market snapshots and price-level ledgers are excluded from the public export; no unrestricted data redistribution license is asserted. The private delivery retains those snapshots and exact hashes.

```sh
# With the preserved private snapshots:
python3 -m carry.market
python3 -m carry.study
# Separate, read-only forward observation:
python3 -m carry.paper
```

The frozen study rejects changed inputs or source. Changes after holdout inspection require a new protocol/version. Report generation additionally uses ReportLab; workbook authoring uses the artifact runtime, while the delivered XLSX opens independently.

## Mechanics and limits

Funding settles on **old holdings**, before executing an earlier decision. Spot cash and isolated perp collateral are distinct. P&L includes both legs, funding, commissions, financing and slippage exactly once. The denominator includes idle collateral. A matched directional hedge can still fail isolated margin.

Actual funding timestamps are matched to nominal 8-hour bar OPEN references, up to 16 ms earlier. Fills, fee tiers and flat margin rates are assumptions. The bar-high stress proxy does not certify intrabar liquidation safety. Historical filters, tier-exact margin, depth, capacity, venue default and tax are not reconstructed. USDT/USD depeg is a separate scenario.

The paper collector has no authenticated or order endpoint. It starts flat, guards stale/duplicate observations, checks funding gaps and writes hypothetical receipts. No future paper track record can be claimed at release. Operational status is in [STATUS_VI](docs/STATUS_VI.md).
