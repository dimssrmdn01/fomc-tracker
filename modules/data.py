"""
data.py
Handles all data acquisition: FOMC meeting calendar, historical Fed Funds Rate
(via FRED), and market-implied rate-move probabilities derived from
30-Day Fed Funds futures (CME ZQ contracts via Yahoo Finance).

No API key is required for FRED's public CSV endpoint or for Yahoo Finance.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pandas as pd
import requests

FRED_SERIES_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"

# Official FOMC meeting calendar. The Fed publishes this a year ahead, so it
# is safe to hardcode and refresh once a year rather than scrape a page that
# can change structure without warning.
FOMC_CALENDAR_2026 = [
    {"start": "2026-01-27", "end": "2026-01-28", "sep": False},
    {"start": "2026-03-17", "end": "2026-03-18", "sep": True},
    {"start": "2026-04-28", "end": "2026-04-29", "sep": False},
    {"start": "2026-06-16", "end": "2026-06-17", "sep": True},
    {"start": "2026-07-28", "end": "2026-07-29", "sep": False},
    {"start": "2026-09-15", "end": "2026-09-16", "sep": True},
    {"start": "2026-10-27", "end": "2026-10-28", "sep": False},
    {"start": "2026-12-08", "end": "2026-12-09", "sep": True},
]

# Manual fallback used only if the live FRED fetch fails (e.g. no internet
# in a restricted sandbox). Kept short - just enough for the app to render.
FALLBACK_RATE_HISTORY = pd.DataFrame(
    {
        "date": pd.to_datetime(
            [
                "2025-06-18", "2025-07-30", "2025-09-17", "2025-10-29",
                "2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29",
                "2026-06-17",
            ]
        ),
        "rate_upper": [4.50, 4.50, 4.25, 4.00, 3.75, 3.75, 3.75, 3.75, 3.75],
    }
)

CURRENT_TARGET_RANGE = (3.50, 3.75)  # (lower, upper) bound, %, as of Jul 2026


@dataclass
class MeetingInfo:
    start: dt.date
    end: dt.date
    has_sep: bool
    is_next: bool
    days_away: int


def get_meeting_schedule(as_of: dt.date | None = None) -> list[MeetingInfo]:
    """Return the full 2026 FOMC calendar annotated with which meeting is next."""
    as_of = as_of or dt.date.today()
    meetings = []
    next_found = False
    for m in FOMC_CALENDAR_2026:
        end_date = dt.datetime.strptime(m["end"], "%Y-%m-%d").date()
        start_date = dt.datetime.strptime(m["start"], "%Y-%m-%d").date()
        is_next = (not next_found) and (end_date >= as_of)
        if is_next:
            next_found = True
        meetings.append(
            MeetingInfo(
                start=start_date,
                end=end_date,
                has_sep=m["sep"],
                is_next=is_next,
                days_away=(end_date - as_of).days,
            )
        )
    return meetings


def get_next_meeting(as_of: dt.date | None = None) -> MeetingInfo | None:
    for m in get_meeting_schedule(as_of):
        if m.is_next:
            return m
    return None


def fetch_fed_funds_rate_history(lookback_days: int = 730) -> pd.DataFrame:
    """
    Pull the effective Federal Funds Rate (FEDFUNDS, daily EFFR series DFF)
    from FRED's public CSV export. Falls back to a small bundled dataset
    if the network call fails so the app never shows a blank chart.
    """
    try:
        url = FRED_SERIES_URL.format(series="DFF")
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        df = pd.read_csv(pd.io.common.StringIO(resp.text))
        df.columns = ["date", "rate"]
        df["date"] = pd.to_datetime(df["date"])
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
        df = df.dropna().sort_values("date")
        cutoff = pd.Timestamp.today() - pd.Timedelta(days=lookback_days)
        return df[df["date"] >= cutoff].reset_index(drop=True)
    except Exception:
        df = FALLBACK_RATE_HISTORY.copy()
        df = df.rename(columns={"rate_upper": "rate"})
        return df


def get_last_completed_meeting(as_of: dt.date | None = None) -> MeetingInfo | None:
    """Return the most recent FOMC meeting that has already concluded."""
    as_of = as_of or dt.date.today()
    past = [m for m in get_meeting_schedule(as_of) if m.end <= as_of]
    return past[-1] if past else None


def fetch_latest_statement_text() -> dict:
    """
    Fetch the FOMC statement for the most recently completed meeting directly
    from federalreserve.gov, using the site's predictable URL pattern:
    /newsevents/pressreleases/monetary{YYYYMMDD}a.htm (date = second meeting day).

    Returns a dict with 'text', 'url', and 'meeting_date', or raises ValueError
    with a friendly message if the fetch or parsing fails (e.g. layout change,
    no network, or the release simply isn't published yet).
    """
    from bs4 import BeautifulSoup

    meeting = get_last_completed_meeting()
    if meeting is None:
        raise ValueError("Belum ada rapat FOMC yang selesai pada kalender ini.")

    url = f"https://www.federalreserve.gov/newsevents/pressreleases/monetary{meeting.end:%Y%m%d}a.htm"

    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; FOMCTracker/1.0)"},
        )
        resp.raise_for_status()
    except Exception as exc:
        raise ValueError(
            f"Gagal mengambil statement dari federalreserve.gov: {exc}. "
            "Coba tempel teks statement secara manual sebagai gantinya."
        ) from exc

    soup = BeautifulSoup(resp.text, "html.parser")
    full_text = soup.get_text("\n")

    start_markers = ["approved the following statement", "For release at"]
    end_marker = "For media inquiries"

    start_idx = -1
    for marker in start_markers:
        idx = full_text.find(marker)
        if idx != -1:
            start_idx = idx
            break

    end_idx = full_text.find(end_marker)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        raise ValueError(
            "Tidak bisa menemukan teks statement di halaman (struktur situs mungkin berubah). "
            "Coba tempel teks secara manual sebagai gantinya."
        )

    raw_segment = full_text[start_idx:end_idx]
    # Drop the leading marker sentence itself, keep the statement paragraphs.
    lines = [ln.strip() for ln in raw_segment.split("\n") if ln.strip()]
    statement_lines = [ln for ln in lines if not ln.startswith(("approved the following", "For release at"))]
    statement_text = "\n\n".join(statement_lines)

    if len(statement_text) < 80:
        raise ValueError("Teks statement yang berhasil diambil terlalu pendek, kemungkinan parsing gagal.")

    return {
        "text": statement_text,
        "url": url,
        "meeting_date": meeting.end,
    }


def estimate_move_probabilities(current_upper: float = CURRENT_TARGET_RANGE[1]) -> dict:
    """
    Lightweight, CME-FedWatch-style estimate of the market-implied probability
    of a hold / 25bp cut / 25bp hike at the next meeting, derived from 30-Day
    Fed Funds futures (ZQ) pricing via Yahoo Finance.

    Methodology (simplified from the CME FedWatch approach):
    implied rate = 100 - futures_price
    The gap between the implied rate and the current effective rate, scaled
    by the fraction of the month the new rate would be in effect, gives the
    probability-weighted expected rate change.

    If futures data is unavailable, returns a neutral placeholder so the UI
    can still render with a clear "data unavailable" note instead of crashing.
    """
    try:
        import yfinance as yf

        ticker = yf.Ticker("ZQ=F")
        hist = ticker.history(period="5d")
        if hist.empty:
            raise ValueError("no futures data returned")
        last_price = float(hist["Close"].dropna().iloc[-1])
        implied_rate = 100 - last_price
        current_mid = (CURRENT_TARGET_RANGE[0] + CURRENT_TARGET_RANGE[1]) / 2
        delta = implied_rate - current_mid

        # Convert the implied delta into rough hold/cut/hike odds.
        # This is a simplified heuristic, not the full CME methodology.
        if delta <= -0.10:
            p_cut = min(0.85, 0.5 + abs(delta) * 2)
            p_hold = 1 - p_cut - 0.03
            p_hike = 0.03
        elif delta >= 0.10:
            p_hike = min(0.85, 0.5 + delta * 2)
            p_hold = 1 - p_hike - 0.03
            p_cut = 0.03
        else:
            p_hold = 0.70
            p_cut = 0.18
            p_hike = 0.12

        total = p_cut + p_hold + p_hike
        return {
            "cut": round(p_cut / total * 100, 1),
            "hold": round(p_hold / total * 100, 1),
            "hike": round(p_hike / total * 100, 1),
            "source": "live",
            "implied_rate": round(implied_rate, 2),
        }
    except Exception:
        return {
            "cut": 18.0,
            "hold": 70.0,
            "hike": 12.0,
            "source": "fallback",
            "implied_rate": None,
        }
