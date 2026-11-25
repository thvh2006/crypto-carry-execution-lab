# Research method

## Scope and frozen evidence

BTCUSDT and ETHUSDT spot plus USDT-margined linear perpetuals, Binance, calendar 2025. Each asset/policy/partition uses a separate 100,000 USDT sleeve. Development is January-June, validation July-September and historical holdout October-December. Partitions start flat and close at the final observation. They are separate experiments, not a compounded full-year portfolio.

The original run is `eed008040d6c6d18`. Its freeze, protocol and CSV results remain unchanged. Release 0.3 adds explanatory diagnostics and fixes reproduction infrastructure after holdout consumption. Those additions are not a new out-of-sample test. Original engine/adapter/study/forecast source is preserved under `artifacts/market/frozen_source/carry/` and verified against the original freeze before reproduction.

## Units and accounting

Quantity is base-asset exposure; a perp short is negative. Prices are USDT per base unit. Funding is decimal per actual settlement. Short funding cash is `-perp_quantity * settlement_mark * funding_rate`. Perp unrealized P&L is `quantity * (mark - average_entry)`.

Equity = spot cash + spot market value + derivatives collateral + perp unrealized P&L. Net P&L = spot P&L + perp P&L + funding - commissions - financing. Slippage is embedded once in leg P&L and must not be deducted again. Internal collateral allocations are not profit. USDT equals USD in the base study; depeg translation is separate.

## Event order and information

1. Settle funding on the position held before the event.
2. Check isolated collateral using the sampled settlement mark.
3. On breach, model an unwind and halt entries, preserving deficits.
4. Execute an earlier target with separate leg fill assumptions.
5. Mark equity and reconcile all cash/P&L components.
6. Form the next target using currently available information.

Base execution delay is one observation, approximately eight hours. Sensitivities use two and three observations. Actual funding timestamps are matched to nominal 8-hour bar opens, up to 16 ms earlier. The reference is a hypothetical sampled execution, not a synchronized bid/ask or a demonstrated fill. High/low/close prices do not enter signals or executable references.

## Allocation and frictions

Initial spot-wallet cash is 65% of capital, isolated perp collateral 35%, desired matched spot notional 55%. Base quantity stays fixed while active and is recalculated on entry. Original quantity step is 0.001 base unit for both assets. Base assumptions: spot 10 bps per side, perp 5 bps per side, adverse slippage 2 bps per fill, 10% initial margin, 1% maintenance plus 10 bps closing reserve. Financing is zero for the cash-funded base case; opportunity cost is excluded. These are historical research assumptions, not certification of a venue fee tier or liquidation schedule.

Matched spot/perp quantities hedge directional base exposure but do not eliminate basis, funding, collateral, stablecoin or venue risk. Spot purchases can be cash-limited and perp increases rejected by initial-margin checks. Partial-fill/outage scenarios expose residual delta. Full forced-close fills are illustrative.

## Policies and forecasting

Baselines: unhedged spot, continuous matched carry, and carry active above last-settled funding of 0.00005 (0.5 bps per event). Spot has different directional risk and is not an equal-risk benchmark.

Matched forecast families: last rate, trailing-nine mean, and ridge AR(1), using 24-90 previous observations. Standardization is fitted inside each past training window. Fixed ridge shrinkage equals the training sample count on the standardized regressor. A forecast made after event i predicts event i+1 and is first executable then, after that event's settlement. EWMA decay 0.94 is a causal volatility diagnostic, not a position rule.

Forecast errors and net trading economics are both reported. Smoothing can improve threshold economics through lower turnover without establishing alpha. No model or threshold was selected after inspecting the holdout.

## Risk, uncertainty and descriptive review

Margin uses isolated derivative equity less absolute short notional times maintenance plus close reserve. The bar-high proxy revalues the post-trade short at the following bar's maximum mark with collateral held fixed. It is an ex-post diagnostic, not an intrabar liquidation reconstruction.

Seven scenarios cover negative funding, basis widening, joint rally, partial spot fills, maintenance increases, collateral haircut and USDT depeg. Paired uncertainty uses daily P&L differences, seven-day moving blocks, 2,000 replications, seed 20261124. Intervals describe the observed regime and do not include model-selection or execution-model uncertainty.

Release 0.3 descriptive funding/basis distributions, monthly regimes, persistence and turnover diagnostics explain the consumed study. They are not used to revise signals. Native Excel scenarios are separate from imported historical outcomes.
