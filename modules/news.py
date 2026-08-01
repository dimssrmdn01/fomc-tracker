"""
news.py
Fetches economic & financial market news via the Finnhub API.

Free tier: https://finnhub.io/register (no credit card required).
Endpoint docs: https://finnhub.io/docs/api/market-news

Finnhub's /news endpoint takes a `category` param with a fixed set of
values: "general", "forex", "crypto", "merger". We pull all three relevant
categories directly and merge them, tagging each article with the category
it actually came from (plus a light keyword pass for finer-grained tags
like Bank Sentral / Makro Ekonomi within the general feed). Per-category fetch
failures are collected as diagnostics rather than silently swallowed, so
the UI can explain *why* a filter came up empty instead of showing nothing.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import requests

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"

# Categories fetched directly from Finnhub (these are the only values its
# API accepts for general market news, aside from "merger").
FINNHUB_CATEGORIES = {
    "general": "Umum",
    "forex": "Forex",
    "crypto": "Kripto",
}

# --- UPGRADE: Extra keyword-based tagging untuk Makroekonomi & CPI/PPI ---
CATEGORY_KEYWORDS = {
    "Bank Sentral": [
        "fed", "fomc", "federal reserve", "powell", "ecb", "bank of england",
        "boe", "bank of japan", "boj", "interest rate", "rate cut", "rate hike",
        "central bank", "monetary policy",
    ],
    "Data Makro (CPI/PPI)": [
        "inflation", "cpi", "ppi", "pce", "consumer price", "producer price", 
        "gdp", "nfp", "payroll", "jobless claims", "labor market", "employment", 
        "retail sales", "economic growth", "makro"
    ],
    "Pasar Saham": ["stocks", "s&p", "nasdaq", "dow jones", "wall street", "equities"],
    "Komoditas": ["oil", "gold", "commodity", "opec", "crude"],
}

ALL_TAGS = ["Semua", "Bank Sentral", "Data Makro (CPI/PPI)", "Pasar Saham", "Kripto", "Forex", "Komoditas", "Umum"]


@dataclass
class NewsItem:
    headline: str
    summary: str
    source: str
    url: str
    datetime: dt.datetime
    image: str | None
    tags: list[str]


@dataclass
class FetchDiagnostics:
    """Per-category fetch results, so the UI can explain empty filters."""
    counts: dict = field(default_factory=dict)   # e.g. {"general": 25, "forex": 0}
    errors: dict = field(default_factory=dict)   # e.g. {"forex": "403 Client Error..."}


def _keyword_tags(headline: str, summary: str) -> list[str]:
    text = f"{headline} {summary}".lower()
    return [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in text for kw in kws)]


def _fetch_one_category(finnhub_category: str, base_tag: str, api_key: str, limit: int) -> list[NewsItem]:
    resp = requests.get(
        FINNHUB_NEWS_URL,
        params={"category": finnhub_category, "token": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    raw_items = resp.json()

    if not isinstance(raw_items, list):
        raise ValueError(f"Respons tidak terduga dari Finnhub: {raw_items}")

    items = []
    for raw in raw_items[:limit]:
        try:
            headline = (raw.get("headline") or "").strip()
            summary = (raw.get("summary") or "").strip()
            if not headline:
                continue
            tags = [base_tag] + _keyword_tags(headline, summary)
            tags = list(dict.fromkeys(tags))  # de-dupe, keep order
            items.append(
                NewsItem(
                    headline=headline,
                    summary=summary,
                    source=raw.get("source", "—"),
                    url=raw.get("url", ""),
                    datetime=dt.datetime.fromtimestamp(raw.get("datetime", 0)),
                    image=raw.get("image") or None,
                    tags=tags,
                )
            )
        except Exception:
            continue
    return items


def fetch_market_news(api_key: str, limit_per_category: int = 25) -> tuple[list[NewsItem], FetchDiagnostics]:
    """
    Fetch recent market news from Finnhub across general, forex, and crypto
    categories, merge and de-duplicate by URL, sort newest first.

    Returns (items, diagnostics). Raises ValueError only if EVERY category
    fails or the key is missing, so the UI layer can crash-guard the totally
    broken case while still surfacing partial failures via diagnostics.
    """
    if not api_key:
        raise ValueError("Finnhub API key belum diisi. Masukkan di sidebar terlebih dahulu.")

    all_items: list[NewsItem] = []
    diag = FetchDiagnostics()

    for finnhub_category, base_tag in FINNHUB_CATEGORIES.items():
        try:
            fetched = _fetch_one_category(finnhub_category, base_tag, api_key, limit_per_category)
            diag.counts[finnhub_category] = len(fetched)
            all_items.extend(fetched)
        except Exception as exc:
            diag.counts[finnhub_category] = 0
            diag.errors[finnhub_category] = str(exc)

    if not all_items:
        detail = "; ".join(f"{k}: {v}" for k, v in diag.errors.items())
        raise ValueError(f"Finnhub tidak mengembalikan data berita sama sekali. Detail: {detail or 'tidak diketahui'}")

    # De-dupe by URL (Finnhub occasionally repeats an article across feeds).
    seen = set()
    deduped = []
    for item in all_items:
        if item.url in seen:
            continue
        seen.add(item.url)
        deduped.append(item)

    deduped.sort(key=lambda n: n.datetime, reverse=True)
    return deduped, diag


def filter_by_tag(items: list[NewsItem], tag: str) -> list[NewsItem]:
    if tag == "Semua":
        return items
    return [n for n in items if tag in n.tags]