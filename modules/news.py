"""
news.py
Fetches general economic & financial market news via the Finnhub API.

Free tier: https://finnhub.io/register (no credit card required).
Endpoint docs: https://finnhub.io/docs/api/market-news
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import requests

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"

# Finnhub's "general" category already leans economic/financial (it excludes
# sports/entertainment). We layer a light keyword tagger on top so the UI
# can group articles (e.g. surface anything Fed/central-bank related).
CATEGORY_KEYWORDS = {
    "Bank Sentral": [
        "fed", "fomc", "federal reserve", "powell", "ecb", "bank of england",
        "boe", "bank of japan", "boj", "interest rate", "rate cut", "rate hike",
        "central bank", "monetary policy",
    ],
    "Inflasi": ["inflation", "cpi", "pce", "consumer price"],
    "Pasar Saham": ["stocks", "s&p", "nasdaq", "dow jones", "wall street", "equities"],
    "Kripto": ["crypto", "bitcoin", "ethereum"],
    "Komoditas": ["oil", "gold", "commodity", "opec"],
}

ALL_TAGS = ["Semua"] + list(CATEGORY_KEYWORDS.keys()) + ["Umum"]


@dataclass
class NewsItem:
    headline: str
    summary: str
    source: str
    url: str
    datetime: dt.datetime
    image: str | None
    tags: list[str]


def _tag_article(headline: str, summary: str) -> list[str]:
    text = f"{headline} {summary}".lower()
    tags = [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in text for kw in kws)]
    return tags or ["Umum"]


def fetch_market_news(api_key: str, category: str = "general", limit: int = 30) -> list[NewsItem]:
    """
    Fetch recent general market/economic news from Finnhub.
    Raises ValueError with a friendly message on failure so the UI layer
    can display it without crashing.
    """
    if not api_key:
        raise ValueError("Finnhub API key belum diisi. Masukkan di sidebar terlebih dahulu.")

    try:
        resp = requests.get(
            FINNHUB_NEWS_URL,
            params={"category": category, "token": api_key},
            timeout=10,
        )
        resp.raise_for_status()
        raw_items = resp.json()
    except Exception as exc:
        raise ValueError(f"Gagal mengambil berita dari Finnhub: {exc}") from exc

    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("Finnhub tidak mengembalikan data berita. Cek kembali API key kamu.")

    items = []
    for raw in raw_items[:limit]:
        try:
            headline = (raw.get("headline") or "").strip()
            summary = (raw.get("summary") or "").strip()
            if not headline:
                continue
            items.append(
                NewsItem(
                    headline=headline,
                    summary=summary,
                    source=raw.get("source", "—"),
                    url=raw.get("url", ""),
                    datetime=dt.datetime.fromtimestamp(raw.get("datetime", 0)),
                    image=raw.get("image") or None,
                    tags=_tag_article(headline, summary),
                )
            )
        except Exception:
            continue

    items.sort(key=lambda n: n.datetime, reverse=True)
    return items


def filter_by_tag(items: list[NewsItem], tag: str) -> list[NewsItem]:
    if tag == "Semua":
        return items
    return [n for n in items if tag in n.tags]
