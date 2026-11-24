
# Funding carry after the friction bill


**Retrospective market evidence / 24 November 2026.** Does long spot and short a linear perpetual produce useful net economics once funding reversals, both legs, turnover and separate collateral are counted? The answer in this fixed 2025 sample depends strongly on how often the position is switched.

Continuous carry made a small positive net result in the October-December holdout. The last-rate threshold repeatedly paid to enter and exit and lost money. Smoother forecasts reduced the loss relative to that threshold, but neither forecast strategy beat continuous carry in this holdout. This is a useful negative result, not a deployable return claim.

|Holdout sleeve|Continuous carry|Last-rate threshold|

|---|---|---|

|BTCUSDT|374.27|-8,137.40|

|ETHUSDT|311.46|-10,252.43|

Each asset/policy starts with a separate 100,000 USDT sleeve. Results are hypothetical bar-based executions after fees and slippage. They exclude live fills, custody/venue default, tax, tier-exact liquidation and a forward paper track record. Do not interpret the two sleeves as a combined 100,000 USDT portfolio.

The package contains the audited data contract, frozen study receipt, all three research partitions, six policy variants, forecast errors, cost/delay sensitivities, paired uncertainty, independent Excel mechanics and 18 automated tests. Run identifier: eed008040d6c6d18.


# 01 / Contract mechanics and capital


Universe: Binance BTCUSDT and ETHUSDT spot plus USDT-margined linear perpetuals. Perpetual quantity is signed base units, with short quantities negative. Positive funding pays a short position. Funding cash at an event is -q_perp × settlement mark × settled rate. New positions entered after settlement receive no cash for that event.

The 100,000 USDT capital denominator includes 65,000 spot-wallet cash and 35,000 isolated derivatives collateral. Desired matched spot exposure is 55% of initial capital. Quantity is fixed while active and recalculated on re-entry. The market study uses a conservative common 0.001 base-unit quantity step. Current exchangeInfo corroborates the linear USDT instruments and perpetual step; it is not historical filter evidence.

|Accounting identity|Treatment|

|---|---|

|Equity|Spot cash + spot market value + perp collateral + unrealized perp P&L|

|Net P&L|Spot P&L + perp P&L + funding - commissions - financing|

|Slippage|Embedded once in each leg’s P&L; shown separately as a diagnostic|

|Collateral transfers|Internal allocation, never profit|

|Financing|0% base assumption for a fully cash-funded sleeve; opportunity cost excluded|

The independent workbook case uses 275 filled spot units against 550 short perp units, spot price 100 and perp close 105, with three positive/negative settlements. The default result is -2,860.825 USDT, funding +0.55 and residual delta -275 units. Four commissions are included. Workbook formulas reconcile to the Python Account case; changing the spot-fill input changes the result.


# 02 / Source provenance and coverage


Official public API responses were read in Chrome and saved as plain UTF-8 JSON after shell DNS and several archive downloads failed. Raw records are preserved in the private package with SHA-256 receipts. No account endpoint, API key or order endpoint was used. An independently downloaded January BTC funding archive was also available.

|Coverage 2025|BTCUSDT|ETHUSDT|

|---|---|---|

|Funding events|1,095|1,095|

|Spot / perp / mark 8h bars|1,095 each|1,095 each|

|Missing or duplicate nominal events|0|0|

|Negative funding events|141|177|

|Maximum event offset / quote age|16 ms|16 ms|

All 93 January BTC funding timestamps and rates match the same-provider public archive exactly. This checks schema and ingestion, not independent exchange truth. Funding timestamps are actual event milliseconds. Price references are the nominal 8-hour bar OPEN; close, high and low are never used as executable prices or signal features. A reference can precede funding availability by up to 16 ms, so it remains an execution approximation.

The bar-high mark series is used only as an ex-post isolated-margin diagnostic. It is never a tradable quote or predictor. The archive microsecond convention for 2025 spot files is not applied to API kline milliseconds. No missing funding is filled with zero. A changed cadence, duplicate or incomplete coverage stops normalization.

Access is public, but no unrestricted market-data redistribution license is asserted. Raw and normalized snapshots stay out of the public source export. The private delivery preserves them for reproducibility. Historical maintenance tiers, fee tier, minimum order filters and depth are unavailable and explicitly remain assumptions.


# 03 / Frozen temporal design


|Partition|Dates UTC|Purpose / events per asset|

|---|---|---|

|Development|Jan-Jun 2025|Pipeline development / 543|

|Validation|Jul-Sep 2025|Fixed specification check / 276|

|Historical holdout|Oct-Dec 2025|Final retrospective comparison / 276|

The written protocol preceded the first strategy-return inspection. Acquisition was amended from hourly monthly archives to official 8-hour API bars because of access failures, before running the market study. Engine, adapter, study code, forecasting code, protocol, normalized inputs and configuration were hashed before the initial run. The freeze file rejects a rerun if any of those contents change.

Each partition starts flat with fresh capital and closes fully at its final sampled observation. Therefore partition results are separate experiments, not a continuously compounded full-year portfolio. Forecast histories can use earlier chronological partitions; no future funding enters a training window. All policy variants share timestamps, capital and execution assumptions.

Event order is: settle existing positions, check sampled isolated margin, execute the earlier target, record/reconcile equity, then decide the next target. The base delay is one observation, roughly eight hours. Sensitivities delay by two or three observations. No strategy can earn the just-observed settlement by opening at that same row.

The fixed trial budget is one last-rate model, one trailing-nine mean and one ridge AR(1), with no hyperparameter optimization. Ridge uses at most 90 previous observations, at least 24, train-only standardization and fixed shrinkage. EWMA with decay 0.94 is a causal diagnostic rather than a trading rule. No threshold or sample was tuned to improve the holdout.


# 04 / Baselines before the holdout


Unhedged spot measures directional exposure at the same 55% allocation. Continuous carry holds equal spot and short-perpetual base quantities. Threshold carry is active when the last settled funding rate is at least 0.00005 (0.005% per settlement), and acts only at the later observation. There is no hysteresis or minimum holding period in this deliberately simple baseline.

|Asset / partition|Spot net|Carry net|Threshold net|

|---|---|---|---|

|BTCUSDT / development|8,015.39|1,034.95|-18,933.65|

|ETHUSDT / development|-14,489.54|854.31|-14,682.37|

|BTCUSDT / validation|2,905.03|832.97|-7,996.11|

|ETHUSDT / validation|36,443.68|332.71|-7,495.15|

These partitions are reported alongside the holdout so an attractive single window cannot stand in for the whole experiment. A holdout comparison remains retrospective: the data were collected after 2025 and implementation choices reflect this research context. The freeze prevents hidden edits within this run, not prior knowledge of the market history.

Cash constraints, quantity rounding and initial-margin rejection can leave a residual delta when both legs do not match. Synthetic partial fills and outages exercise the same accounting path; historical base fills are 100% assumptions with adverse price slippage. No historical fill probability, capacity or maker priority is inferred from OHLC bars.


# 05 / Net holdout attribution


|Sleeve / policy|Net P&L|Funding|Fees|Max DD|

|---|---|---|---|---|

|BTCUSDT / spot|-12,931.12|0.00|97.60|-19.32%|

|BTCUSDT / continuous|374.27|566.06|146.38|-0.11%|

|BTCUSDT / threshold|-8,137.40|409.59|6,729.98|-8.14%|

|ETHUSDT / spot|-15,504.96|0.00|94.62|-24.52%|

|ETHUSDT / continuous|311.46|495.99|141.91|-0.12%|

|ETHUSDT / threshold|-10,252.43|309.68|7,752.96|-10.25%|

Values are USDT except drawdown. Slippage is already inside leg P&L. Full spot/perp attribution, residual exposure, fills and sampled margin are in summary.csv and ledger.csv. A positive carry result is small relative to the 100,000 denominator; gross funding alone exaggerates its economics.


# 06 / Forecast skill versus strategy value


|Asset / model|Holdout MAE, bps|Matched net P&L|

|---|---|---|

|BTCUSDT / last_rate|0.30|-8,137.40|

|BTCUSDT / rolling_mean|0.29|-1,255.39|

|BTCUSDT / ridge_ar1|0.31|-4,334.24|

|ETHUSDT / last_rate|0.34|-10,252.43|

|ETHUSDT / rolling_mean|0.31|-1,147.12|

|ETHUSDT / ridge_ar1|0.29|-3,858.67|

Forecasts predict the next settled rate using data through the current settlement. Their recorded training cutoff precedes the target event. All three are inserted into the same threshold rule. During initial model warm-up the matched forecast family holds cash; the full-history last-rate trading baseline is also reported separately. In validation/holdout all models already have a past training history.

Smoothing reduces the number of switches around a threshold. Its improved net result relative to the last-rate rule is therefore not evidence that forecasting funding creates investable alpha. Lower forecast error and lower trading loss are separate questions. Ridge has a lower ETH holdout MAE than the mean but a worse net trading result.

The matched forecasts remain negative after assumed costs in both holdout sleeves, while continuous carry is positive. The incremental-benefit gate fails against that operationally simpler benchmark. A subsequent hysteresis, cost-aware entry rule or different model must be a separately logged study; this holdout is now consumed.


# 07 / Friction and uncertainty


|Asset / policy|Cost ×1|Cost ×2|Cost ×3|Delay 3 events|

|---|---|---|---|---|

|BTCUSDT / continuous|374.27|188.85|3.44|367.78|

|BTCUSDT / threshold|-8,137.40|-16,649.51|-24,750.93|-8,082.12|

|ETHUSDT / continuous|311.46|131.71|-48.05|301.16|

|ETHUSDT / threshold|-10,252.43|-19,682.60|-28,477.27|-9,716.20|

Cost multiples apply to both leg commissions and adverse slippage. Delay sensitivity is separate, at base costs, and changes the first eligible execution observation. The small continuous-carry profit has limited room for larger friction or opportunity cost. Base fees are assumptions, not a promise of the user’s exchange tier.

|Threshold minus continuous|Observed difference|95% block interval|

|---|---|---|

|BTCUSDT|-8,511.67|-10,603.40 to -6,433.40|

|ETHUSDT|-10,563.90|-12,721.41 to -8,961.71|

Uncertainty uses paired daily P&L differences, seven-day moving blocks, 2,000 replications and seed 20261124. It resamples the observed 92-day regime and does not model new regimes, venue failure, model selection or execution misspecification. Intervals are descriptive and are not multiple-testing-adjusted. Forecast-versus-last-rate intervals are in paired_uncertainty.csv.


# 08 / Margin is a separate survival problem


|Holdout policy|Minimum sampled buffer|Minimum 8h-high proxy|

|---|---|---|

|BTCUSDT / continuous|29,340.62|28,739.34|

|BTCUSDT / threshold|30,646.21|30,235.97|

|ETHUSDT / continuous|27,192.46|26,241.98|

|ETHUSDT / threshold|31,056.00|30,338.42|

The margin account does not automatically access gains in the spot wallet. The seven scenario cases cover negative funding, a basis widening, a joint 80% rally, half-filled spot, higher maintenance, a collateral haircut and a stablecoin depeg. In the joint rally the combined sleeve can retain most economic capital while isolated collateral fails.

The bar-high proxy revalues the post-trade short at the maximum mark inside the following 8-hour bar, holding that row’s collateral fixed. It is an ex-post stress diagnostic. Its positive buffer does not certify absence of liquidation: the path of cash transfers, funding, tier changes and liquidation mechanics is not reconstructed. No intrabar event ordering is invented from OHLC.

A sampled margin breach triggers a modeled unwind at sampled traded prices and stops new entries. This preserves a deficit instead of erasing it. Full fills on a forced close are an approximation; the stress case is not an exact exchange liquidation engine. Historical liquidation fees, insurance fund behavior, ADL, custody loss and venue default require separate evidence.

USDT equals USD in the base replay. The depeg scenario translates economic equity into USD; collateral eligibility haircuts are modeled separately. Treating a collateral haircut as an immediate mark-to-market loss would mix two different mechanisms.


# 09 / Operations, reproduction and decision


The paper module is strictly read-only: public prices/funding in, hypothetical targets and receipts out. It contains no authenticated or order API. The first snapshot starts flat and cannot claim earlier funding. Later runs settle new funding on existing paper holdings before executing the prior target. A state lock, duplicate-time guard, funding-gap check, quote sanity check and event-level reconciliation fail closed.

Operational check: GitHub CI passed. The hosted paper run returned HTTP 451 from Binance futures bookTicker; its schedule was removed and no successful paper state is claimed. The public dashboard and CSV export were checked in Chrome.

Paper polling is coarser than live trading. Quotes are midpoint references with modeled slippage; funding is actually observed but fills are hypothetical. A changed cadence, stale quote, incomplete page or failed network request stops the update. Scheduled execution depends on endpoint access from the chosen runner. A successful workflow is operational evidence, never proof of a future return.

|Reproduction|Command / artifact|

|---|---|

|Verify engine|python3 -m unittest discover -s tests -v|

|Synthetic replay|python3 -m carry.run demo|

|Normalize preserved snapshots|python3 -m carry.market|

|Frozen market study|python3 -m carry.study|

|Read-only paper observation|python3 -m carry.paper|

|Receipts|artifacts/market/freeze.json and receipt.json|

**Decision:** retain continuous carry as the research benchmark and reject this naive threshold as an execution policy at the assumed fee schedule. Do not deploy from these results. The next study should price switching decisions against expected holding duration and friction, acquire execution-level observations and historical margin tiers, and accumulate a genuine forward paper record without recycling the consumed holdout.

Primary sources: Binance public-data repository (github.com/binance/binance-public-data); Binance funding FAQ (binance.com/en/support/faq/detail/360033525031); official data-api.binance.vision/api/v3/klines; fapi.binance.com/fapi/v1/fundingRate, /klines, /markPriceKlines and /exchangeInfo. Snapshot URL parameters and individual hashes are in the private manifest. Report generated from run eed008040d6c6d18.