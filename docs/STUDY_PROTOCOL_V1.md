# P3 market study protocol v1

Recorded on 24 November 2026 before inspecting market strategy returns. A January 2025 BTC funding archive was inspected for schema and timestamp jitter only.

Candidate venue and instruments are Binance BTCUSDT and ETHUSDT spot and USD-M linear perpetuals. Candidate sample is the complete calendar year 2025, subject to an explicit coverage audit. Acquisition amendment, recorded before any market strategy replay: public monthly download links were blocked in Chrome and shell DNS is unavailable. Use official public API snapshots saved through the browser. Use 8-hour spot/perpetual OHLC bars and actual funding events with their settlement marks. The coarser grid bounds the study to settlement-level economics; it cannot establish intraperiod liquidation safety or executable fills. Preserve all timestamp offsets and disclose the sampling approximation.

Development is January–June 2025. Validation is July–September 2025. The final historical holdout is October–December 2025. These are retrospective research partitions. No forward performance claim is made. Freeze the validated adapter, engine, config and data hashes before opening final-holdout strategy results.

Keep the existing capital and cost assumptions for the initial study. Compare spot, continuous carry and last-settled-funding threshold policies. Forecast last rate, trailing mean and regularized AR(1) use past funding only. Report MAE and paired net strategy economics. One fixed model per family, with no hyperparameter optimization, is the initial trial budget. Record every subsequent change and reason. A model revision after holdout inspection invalidates its untouched status.

Primary outcome is net P&L divided by total sleeve capital, with funding, both leg P&Ls, costs, drawdown, residual delta and minimum isolated margin buffer reported. Compare policies on identical timestamps and starting capital. Cost ×1/×2/×3 and execution delays are predefined sensitivities. Block uncertainty uses paired daily P&L differences with seven-day moving blocks and a fixed random seed. Its interval describes this observed sample and does not establish a persistent edge.

All executable prices are bar-based approximations. Settlement marks are kept separate from traded prices. No funding is credited to a position opened after that settlement. Funding availability includes actual archive event time. New decisions execute on a later observation. Instrument filters, fee tiers and maintenance schedules must be sourced or explicitly labeled historical assumptions. A fixed maintenance approximation cannot be promoted to an exact venue liquidation result.

Coverage failures must be recorded before a sample change. Do not silently fill missing funding with zero. Do not choose the sample or threshold to improve returns. Report negative results and all operational failures.
