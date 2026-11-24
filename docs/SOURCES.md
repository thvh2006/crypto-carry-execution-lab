# Source register

Reviewed 24 Nov 2026. Documentation informs implementation conventions. Historical market data and dated instrument rules remain unaudited.

| Source | Claim supported | Application and limit |
| --- | --- | --- |
| Binance funding FAQ | Funding transfers depend on position notional and rate, use mark price, and settlement cadence can change | Engine signs and event order. Actual funding times must come from event data. |
| Binance public data README | Archives have stream-specific schemas, spot timestamps change to microseconds from January 2025, and downloads have checksums | Candidate acquisition source. Download failed due DNS and terms require review. |
| Bybit isolated liquidation documentation | Isolated collateral risk is assessed on mark price and includes tier-related behavior | Supports the distinction between hedge P&L and collateral survival. Bybit formulas are not used as Binance rules. |

https://www.binance.com/en/support/faq/detail/360033525031

https://github.com/binance/binance-public-data

https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md

https://www.bybit.com/en/help-center/article/UTA-Trading-Rules-Liquidation-Process

## Actual market acquisition - 24 November 2026

Official public API responses were saved from Chrome into UTF-8 JSON; raw byte hashes and exact request parameters are in data/market/manifest.json and artifacts/market/data_audit.json. Streams cover 2025, eight-hour OHLC for spot/perpetual/mark, actual funding settlement times and marks. Each stream has 1,095 records per asset. The independent January BTC archive cross-check matches 93/93 event times and rates. Current exchangeInfo corroborates linear USDT contracts and 0.001 perpetual quantity steps only; historical filters and fee/margin tiers remain assumptions.

Endpoints: https://data-api.binance.vision/api/v3/klines ; https://fapi.binance.com/fapi/v1/fundingRate ; https://fapi.binance.com/fapi/v1/klines ; https://fapi.binance.com/fapi/v1/markPriceKlines ; https://fapi.binance.com/fapi/v1/exchangeInfo . Public-data access does not establish an unrestricted redistribution license. Raw and normalized data are excluded from the public source export.
