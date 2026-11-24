# Mechanics and implementation

## Contract and units

The engine models a USDT-settled linear perpetual. Quantity is base-asset exposure after applying the contract multiplier. One unit of BTCUSDT exposure means one BTC. Inverse contracts require a different engine. All prices are USDT per base unit. Funding is a decimal at the settlement timestamp. USDT equals USD in the base replay. A depeg scenario separately translates total equity into USD.

Long spot quantity is positive. Short perpetual quantity is negative. Positive funding produces cash `-perp_quantity × settlement_mark × rate`. Perpetual unrealized P&L is `quantity × (mark − average_entry)`. Closing part of a short realizes `closed_quantity × (average_entry − execution_price)`. Increasing a short updates its weighted average entry. The algorithm supports a short held or closed toward zero.

Equity equals spot cash plus spot market value plus derivative collateral plus perpetual unrealized P&L. The profit bridge equals realized and unrealized spot P&L plus perpetual P&L plus funding less commissions and financing. Execution slippage is already embedded in leg P&L. Its separate diagnostic must never be deducted again.

## Information and event order

1. Read the observation timestamp and prices.
2. Settle funding for the position held before this observation. Funding settlement cash cannot fund a position retroactively.
3. Check isolated collateral against sampled mark maintenance plus closing reserve.
4. On breach, perform a full modeled unwind, preserve any collateral deficit and halt entries.
5. Execute intended quantities from the prior observation with separate spot/perpetual fill fractions.
6. Mark equity and reconcile the P&L bridge.
7. Decide intended quantities for the next observation using only information available now.

On the final sample observation, positions are closed with modeled taker costs. The default one-observation decision delay is conservative and explicit. It is eight hours in the fixture. A new position at a settlement is modeled as opened after that settlement. Real exchanges can have settlement timing deviations, which need additional event data.

## Allocation and execution

Initial capital is 100,000 USDT per sleeve. Spot wallet is 65%, isolated derivative collateral is 35%, and desired spot notional at entry is 55% of capital. The short has equal desired base quantity. Partial executions can leave residual delta. Pending differences are retried at subsequent observations and can be cancelled by a newer exit signal. Quantity step is an assumption. Entry margin checks may reject a short increase. Spot purchases are limited by spendable spot cash.

Base commission assumptions are spot 10 bps each side, perpetual 5 bps each side and adverse execution slippage 2 bps. They are educational inputs, with cost ×1/×2/×3 sensitivity. Historical fee tiers and instrument filters require an audited dated specification. Market prices are observations and execution references, with slippage applied in the adverse direction. Fill fractions express hypothetical execution availability.

Unhedged spot, continuously held carry and threshold carry all have the same starting capital and spot allocation budget. Spot has different directional risk. Threshold uses last settled funding >= 0.5 bps per settlement. No annualized yield claim is inferred from this threshold. No train/test performance is claimed. Model thresholds have not been optimized on market data.

## Margin and stresses

The approximation subtracts `abs(perp_quantity) × mark × (maintenance_rate + close_reserve)` from isolated derivative equity. It does not automatically mobilize spot appreciation as collateral. A joint spot/perpetual rally can leave the combined sleeve approximately hedged while the short collateral fails. Full forced unwind at the next sampled price is an illustrative operational policy. It does not reproduce an exchange liquidation engine or prove survival between observations.

Stresses cover funding reversal, basis widening, partial spot fills, maintenance increase, collateral haircut and stablecoin depeg. A haircut reduces collateral eligibility in the stress diagnostic. A depeg changes USD translation. These scenario effects are reported separately.

## Forecasts

At observation t, predictions use funding settlements strictly before t. Last rate and trailing nine-observation mean are baselines. Ridge AR(1) uses at most 90 previous funding observations, train-only standardization and a fixed penalty of one times the training sample count on the standardized regressor. It begins after 24 observations. Squared and absolute forecast errors are exported. Volatility uses EWMA lambda 0.94 on prior log spot returns, in units per observation. It is a diagnostic and does not drive positions in this release.

Full temporal model selection, boosting, forecast-driven strategy comparison, block uncertainty and locked evaluation remain pending.
