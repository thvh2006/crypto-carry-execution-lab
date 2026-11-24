# P3 - Decision Memo

**Date:** 24 November 2026  
**Study run:** `eed008040d6c6d18`  
**Scope:** Retrospective 2025 research with hypothetical execution.

## Decision

Retain continuous carry as the research benchmark. Reject the naive last-settled-funding threshold at the assumed transaction-cost schedule. Neither tested forecast strategy improves on continuous carry in the historical holdout. These findings do not establish a deployable trading edge.

## Historical holdout results

The holdout covers 1 October-31 December 2025. Each asset-policy combination starts flat with a separate **100,000 USDT** sleeve and closes at the final sampled observation. Results are net of modeled commissions and slippage; the two assets do not share a single capital denominator.

| Policy | BTC net P&L (USDT) | ETH net P&L (USDT) |
|---|---:|---:|
| Continuous carry | 374.27 | 311.46 |
| Last-settled-rate threshold | -8,137.40 | -10,252.43 |
| Nine-period mean forecast + threshold | -1,255.39 | -1,147.12 |
| Ridge AR(1) forecast + threshold | -4,334.24 | -3,858.67 |

Frequent switching makes the threshold policy's commissions exceed its funding receipts. Smoother forecasts reduce turnover and losses relative to the last-rate rule, but both forecast strategies remain negative in both sleeves. Lower forecast error does not automatically translate into better net economics. The continuous-carry gain is small relative to total capital and offers limited room for additional friction or opportunity cost.

## Evidence supporting the decision

- **Coverage:** 1,095 funding events and 1,095 bars for each spot, perpetual and mark stream per asset in 2025, with no missing or duplicate nominal events.
- **Ingestion cross-check:** All 93 January BTC funding timestamps and rates match between the public archive and API. Both are from the same provider, so this is not independent confirmation of exchange truth.
- **Accounting:** 18 tests and 13,140 event-ledger rows across six policy variants, three temporal partitions and two assets. Maximum reconciliation residual is below 1e-9 USDT.
- **Research controls:** Written protocol and frozen source/input/configuration hashes before the first strategy-return inspection; chronological development, validation and historical holdout partitions; paired seven-day block-bootstrap intervals; cost multiples of 1, 2 and 3; execution delays of 1, 2 and 3 observations.
- **Independent review:** Formula-driven workbook with a Python golden-case reconciliation, executed notebooks and a public dashboard retaining negative results.

## Limits and operational status

Executable references are eight-hour bar opens matched to actual funding timestamps, with an offset of up to 16 ms. Fills, fee tiers and flat maintenance rates are assumptions. The bar-high margin proxy does not certify intraperiod liquidation safety. P&L is denominated in USDT, not guaranteed USD value. Historical margin tiers, order-book depth, execution capacity and a forward track record remain unverified.

The paper collector reads public data and records hypothetical positions without API keys or order endpoints. Its hosted GitHub run returned **HTTP 451** from Binance futures. Automatic scheduling was removed; no successful forward paper state or performance is claimed. The failure is retained as operational evidence rather than replaced with assumed data.

## Next research gate

Any hysteresis, cost-aware entry rule or model change requires a separately recorded study. The current holdout has been consumed and must not be relabeled untouched. Before considering deployment, obtain execution-level observations and historical margin specifications, verify a permitted data-access environment, and accumulate a genuine forward paper record.

The portfolio contribution is a reproducible research process that explains a negative result and its execution limits, rather than a claim of guaranteed carry income.
