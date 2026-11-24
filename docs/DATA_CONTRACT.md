# Market snapshot contract

Use `BTCUSDT.csv`, `ETHUSDT.csv` and `manifest.json` in a private directory. The CLI never sends orders or uses exchange API keys.

CSV columns are `timestamp,symbol,spot,perp,mark,funding,elapsed_hours,spot_fill,perp_fill`. Timestamps must be unique, sorted, timezone-aware UTC and aligned across price sources for the same event. Prices must be positive and finite. Funding is decimal per actual settlement. Fill fractions range from zero to one and are explicit execution assumptions. Quantity is base-asset exposure after contract multiplier conversion. `elapsed_hours` must equal the actual time since the previous row. The first row's interval describes its settlement convention.

The timestamp checks can detect a gap relative to the declared interval. They cannot discover an omitted settlement if a source also changes the declared interval. Independently reconcile all settlement timestamps and cadence changes against the venue history before setting funding_coverage_verified.

Manifest example, with approvals initially false

```json
{
  "kind": "market",
  "source_urls": [],
  "funding_coverage_verified": false,
  "timestamp_alignment_verified": false,
  "rights_reviewed": false,
  "contract_specs_reviewed": false,
  "raw_receipt_paths": [],
  "historical_fee_schedule": "pending",
  "instrument_filter_history": "pending"
}
```

Approvals record a human/data audit. The CLI validates schema and event ordering independently. Retain raw hashes, retrieval timestamps, availability timestamps, funding cadence, price type, interval granularity, fee/spec version and all exceptions. Funding history is realized cash-flow data. Predicted or indicative funding needs a separate availability-timestamped feed.

Binance public archives are a candidate source. Spot archive timestamps from January 2025 use microseconds, while derivatives streams require their own unit checks. Normalize units by the documented stream convention. A timestamp magnitude guess alone is insufficient evidence. A common interval candle does not establish an executable synchronized quote at the funding instant. Mark prices and traded prices serve different roles.

Read the provider terms and record analysis/export/redistribution rights separately. Keep downloaded market data private until sharing rights are confirmed. A code repository license does not automatically license market data.

The environment failed DNS lookup for data.binance.vision on 24 Nov 2026. No market archive was acquired or audited. Market mode currently accepts externally prepared normalized data. An archive adapter remains pending until a representative raw sample is verified.
