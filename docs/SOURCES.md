# Sources and assumptions

| Source | Use | Evidence boundary |
|---|---|---|
| https://github.com/binance/binance-public-data | Public archive conventions; January BTC funding cross-check | Same provider as API; not independent exchange truth |
| https://www.binance.com/en/support/faq/detail/360033525031 | Funding sign, settlement notional and timing conventions | Does not establish historical fee tier or execution |
| https://data-api.binance.vision/api/v3/klines | 2025 BTC/ETH spot 8-hour bars | Bar open is a hypothetical reference, not a bid/ask fill |
| https://fapi.binance.com/fapi/v1/klines | Perpetual traded-price bars | Distinct from settlement mark |
| https://fapi.binance.com/fapi/v1/markPriceKlines | Mark high/low stress diagnostics | OHLC cannot reconstruct intrabar event order |
| https://fapi.binance.com/fapi/v1/fundingRate | Actual funding events, rates and settlement marks | Realized rate is available only at its event time |
| https://fapi.binance.com/fapi/v1/exchangeInfo | Current linear USDT contract/quantity-step corroboration | Current snapshot does not establish historical filters |

Original acquisition: 24 November 2026, official public responses saved through Chrome after shell DNS/archive-access failures. Exact URLs, byte hashes, original retrieval time and coverage are in `artifacts/market/data_audit.json`; preserved raw bytes remain private.

No personal trading account, private key or authenticated exchange endpoint was used. No unrestricted market-data redistribution license is asserted. Base fees, flat margin, fills, financing and initial capital are explicit research assumptions. Code licensing is separate and has not yet been selected.

## Research context

- Schmeling, M., Schrimpf, A., and Todorov, K. (2023). *Crypto carry*. BIS Working Papers 1087, April 2023 version. https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf . Used for carry/capital-risk context, not as a target return or a replication claim.
- Ackerer, D., Hugonnier, J., and Jermann, U. (2024). *Perpetual Futures Pricing*, arXiv:2310.11771v2, revised 4 September 2024. https://arxiv.org/abs/2310.11771v2 . Used to distinguish funding anchoring/pricing from net executable strategy profitability.

Primary paper text/abstracts checked 25 November 2026. No external paper's historical yield is substituted for this study's outcomes.
