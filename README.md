# cheap-vps-dataset

A snapshot dataset of real, scraped VPS deal prices from 28 hosting providers,
plus a small command-line tool to compare them.

This dataset is maintained alongside VPS Deals Wire, an independent comparison
site for cheap VPS plans: https://www.vpsdealswire.com/

## What's inside

- `data/vps_plans.csv` — 231 deal rows from 28 providers (snapshot date: 2026-10-01).
  Each row is one price the scraper actually found on a provider's own page;
  nothing is invented or estimated.
- `tools/vps_compare.py` — filter and rank the CSV from your terminal
  (see `--help`).

## Column reference

| column | meaning |
|---|---|
| `provider` | provider name as shown on the source site |
| `plan_name` | deal/plan title exactly as scraped (may be terse) |
| `cpu_cores`, `ram_gb`, `storage_gb`, `storage_type`, `bandwidth_tb` | hardware specs — **not collected yet, intentionally blank** |
| `price` | listed price in the original `currency` |
| `currency` | ISO currency code of the listed price (USD, EUR, GBP) |
| `price_usd_monthly` | monthly price in USD; blank for non-USD rows (no FX conversion applied) |
| `offer_url` | provider page where the price was found |
| `source_url` | page actually fetched by the scraper |
| `last_updated` | when this row was scraped (UTC, ISO 8601) |

## Update frequency

Prices on the source site are re-scraped every 6 hours. This CSV is a
point-in-time snapshot; regenerate it from a fresh scrape when you need
current numbers. Row counts and the snapshot date are recorded in
`data/vps_plans.csv`'s provenance line below.

- Snapshot date: 2026-10-01
- Rows: 231
- Providers: 28 — the site's live comparison set. The tracker follows 31
  providers; 3 (A2 Hosting, Hetzner Cloud, ServerMania) are currently
  delisted because their pages could not be fetched, so the live site —
  and this dataset — covers the remaining 28.
- 230 rows come from the 2026-10-01 scrape; 1 HostHatch row comes from a
  real browser re-fetch on 2026-09-26 (see `last_updated`). This mirrors
  exactly what the live site renders.

## Generation method

Rows are extracted verbatim from the site's latest scraper output
(`offers.json`, produced by `scraper.py`). The single HostHatch row comes
from the site's refetch log — a real browser re-fetch with captured page
evidence, the same row the live site renders. No rows are hand-edited
and no values are estimated.

## Quick start

```bash
python3 tools/vps_compare.py --top 10
python3 tools/vps_compare.py --provider hetzner --max-price 5
python3 tools/vps_compare.py --search "storage" --top 5
```

## License

MIT — see `LICENSE`. Prices belong to their respective providers; verify on
the provider's site before buying.
