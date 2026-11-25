# Data contract and provenance

## Preserved market snapshot

Private normalized files: `data/market/BTCUSDT.csv`, `ETHUSDT.csv`, `manifest.json`. The original raw snapshot contains funding, spot, perpetual and mark-price API responses plus a January BTC funding archive. All four streams contain 1,095 nominal observations per asset for 2025. No missing or duplicate nominal event was accepted. Archive/API comparison matches 93/93 January BTC funding timestamps and rates; both sources share the same provider.

| Field | Unit / meaning |
|---|---|
| timestamp | Actual funding availability/event time, timezone-aware UTC |
| symbol | BTCUSDT or ETHUSDT |
| spot / perp | Nominal 8-hour bar open, USDT per base unit |
| mark | Actual funding settlement mark |
| funding | Decimal rate per settlement, not annualized |
| elapsed_hours | Actual difference from the previous funding timestamp |
| spot_fill / perp_fill | Explicit hypothetical fractions, 0-1 |
| funding_time_ms / bar_open_ms | API milliseconds, retained separately |
| quote_age_ms | Funding time minus bar open time; maximum 16 ms |
| mark_high / mark_low | Ex-post stress inputs only, never signals or fills |

Validate positive finite prices, finite rates, strict UTC ordering, single-symbol sleeves, unique nominal grid and actual elapsed intervals. Do not fill missing funding with zero. A changed cadence or missing event stops the historical adapter; study changes require a separate version.

Spot API klines use milliseconds in this snapshot. The 2025 microsecond convention of spot archive files must not be applied to API responses. Opening a candle at the same nominal funding time does not establish an executable quote after funding availability.

## Stable identity and reruns

Raw SHA-256s, exact request parameters and original retrieval time are in the preserved manifest and public `artifacts/market/data_audit.json`. Re-normalizing the same raw bytes preserves the original retrieval timestamp, so the normalized manifest is deterministic. New acquisition receipts are separate and are never backdated.

`python3 -m carry.reproduce` verifies every original frozen source/input hash in an isolated temporary checkout and compares all seven CSV hashes. It writes a new reproduction directory rather than replacing the original study.

## Optional public reacquisition

`python3 -m carry.acquire --install-equivalent` collects official public API pages into a new private `data/acquired/` directory, audits complete coverage and installs normalized CSVs only if they match the original frozen CSV hashes. It retains new raw-byte receipts separately and the original normalized-data provenance unchanged. Provider revisions that change normalized data require a new study. HTTP 451 is a hard stop, not a reason to change regions or bypass restrictions.

Endpoint availability and successful reacquisition depend on the execution environment. The hosted paper runner returned HTTP 451; optional reacquisition has not been demonstrated from that blocked environment.

## Public export boundaries

Raw/normalized snapshots and price-level ledgers are private; no unrestricted redistribution license is asserted. Public artifacts contain aggregate statistics and derived account trajectories, without raw price/settled-rate columns. The workbook History tab contains derived account values. A code license would not license provider data.

The legacy manifest flags describe the recorded research audit and its stated private-use scope. They do not certify historical fee tiers, maintenance rules, executable fills or legal permission for unrestricted exports.
