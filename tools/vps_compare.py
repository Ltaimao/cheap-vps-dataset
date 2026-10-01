#!/usr/bin/env python3
"""vps_compare.py - compare cheap VPS deals from the bundled dataset.

Reads data/vps_plans.csv (a snapshot of real, scraped VPS deal prices) and
prints the cheapest matching plans. Filter by provider, keyword, and/or a
maximum monthly price in USD.

Examples:
    python3 tools/vps_compare.py --top 10
    python3 tools/vps_compare.py --provider hetzner --max-price 5
    python3 tools/vps_compare.py --search "dedicated" --top 5
    python3 tools/vps_compare.py --csv /path/to/vps_plans.csv --provider ovh

Note: the dataset currently carries deal-level pricing only; hardware spec
columns (cpu_cores, ram_gb, ...) are intentionally left blank until the
scraper collects them, so price-per-GB-RAM ranking is not available yet.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

DEFAULT_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "vps_plans.csv")


def load_rows(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def to_usd(row: dict) -> float | None:
    raw = (row.get("price_usd_monthly") or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def matches(row: dict, provider: str | None, search: str | None,
            max_price: float | None) -> bool:
    if provider and provider.lower() not in (row.get("provider") or "").lower():
        return False
    if search and search.lower() not in (row.get("plan_name") or "").lower():
        return False
    if max_price is not None:
        usd = to_usd(row)
        if usd is None or usd > max_price:
            return False
    return True


def fmt_price(row: dict) -> str:
    price, cur = row.get("price") or "", row.get("currency") or ""
    if not price:
        return "n/a"
    return f"{price} {cur}".strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Compare cheap VPS deals from data/vps_plans.csv. "
                    "Prints matching plans sorted by monthly USD price (cheapest first).")
    ap.add_argument("--csv", default=DEFAULT_CSV,
                    help="path to vps_plans.csv (default: repo data/vps_plans.csv)")
    ap.add_argument("--provider", default=None,
                    help="only show this provider (case-insensitive substring)")
    ap.add_argument("--search", default=None,
                    help="only show plans whose name contains this keyword")
    ap.add_argument("--max-price", type=float, default=None, metavar="USD",
                    help="only show plans at or below this monthly USD price")
    ap.add_argument("--top", type=int, default=20,
                    help="show at most N rows (default: 20)")
    ap.add_argument("--all", action="store_true",
                    help="show all matching rows (overrides --top)")
    args = ap.parse_args(argv)

    if not os.path.exists(args.csv):
        print(f"error: CSV not found: {args.csv}", file=sys.stderr)
        return 1

    rows = load_rows(args.csv)
    hits = [r for r in rows if matches(r, args.provider, args.search, args.max_price)]
    # rows without a USD price sort last, keeping their original relative order
    hits.sort(key=lambda r: (to_usd(r) is None, to_usd(r) or 0.0))
    if not args.all:
        hits = hits[:args.top]

    if not hits:
        print("No matching plans.")
        return 0

    name_w = min(72, max(len((r.get("plan_name") or "")[:72]) for r in hits))
    prov_w = min(22, max(len(r.get("provider") or "") for r in hits))
    header = f"{'PROVIDER':<{prov_w}}  {'PLAN':<{name_w}}  {'PRICE':<12}  UPDATED"
    print(header)
    print("-" * len(header))
    for r in hits:
        plan = (r.get("plan_name") or "")[:72]
        updated = (r.get("last_updated") or "")[:10]
        print(f"{(r.get('provider') or ''):<{prov_w}}  {plan:<{name_w}}  "
              f"{fmt_price(r):<12}  {updated}")
    print(f"\n{len(hits)} plan(s) shown. "
          f"Prices are scraped snapshots; confirm on the provider's site before buying.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
