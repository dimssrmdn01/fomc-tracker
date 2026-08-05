<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fraunces&weight=600&size=28&pause=1000&color=B9975B&center=true&vCenter=true&width=650&lines=Market+Pulse;Crypto+%2C+Forex+%26+Stocks+Dashboard;Real-Time+Data+%2B+AI+Sentiment;Bilingual+%C2%B7+ID+%2F+EN" alt="Typing SVG" />
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F2E1D,100:B9975B&height=150&section=header&text=Market%20Pulse&fontSize=38&fontColor=F3EEDF&fontAlignY=38&desc=Economic%20%26%20Financial%20Markets%20Dashboard&descAlignY=58&descSize=16" alt="Banner" width="100%">
</div>

<div align="center">

[![Live Demo](https://img.shields.io/badge/▶_Live_Demo-B9975B?style=for-the-badge&logoColor=white)](https://dimss-market-pulse.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.9+-1c100b?style=for-the-badge&logo=python&logoColor=B9975B)
![Streamlit](https://img.shields.io/badge/Streamlit-1c100b?style=for-the-badge&logo=streamlit&logoColor=FF4B4B)
![Groq](https://img.shields.io/badge/Groq-1c100b?style=for-the-badge&logo=groq&logoColor=F59E0B)
![Plotly](https://img.shields.io/badge/Plotly-1c100b?style=for-the-badge&logo=plotly&logoColor=3F4F75)

</div>

## About

**Market Pulse** tracks crypto, forex, and stock markets alongside US Federal Reserve policy in one dashboard  a live multi-asset ticker, an AI-scored news feed, the official Fed press wire, FOMC/CPI/NFP calendars, historical rate data, a real backtest of market-implied predictions, and a cross-asset correlation matrix.

Every number on the AI-generated side is labeled for what it actually is. The Fed Wire's Hawkish/Dovish tags are a plain keyword count on release titles, not an NLP model the real AI scoring lives in the Statement Analysis tab, which sends actual statement text to an LLM. The backtest compares the market's own implied prediction (from historical Fed Funds futures pricing) against real FOMC outcomes, so the accuracy shown is calculated, not asserted.

The design leans into the vocabulary of the subject itself currency green, treasury parchment, gold-seal accents, and a hand-drawn hawk/dove instrument gauge instead of a generic dashboard template. Three color themes are available (Ledger Hijau, Midnight Slate, Terminal Amber), and the entire UI switches between Indonesian and English with one click.

## Features

**Market Overview**
Live prices for a customizable watchlist (crypto, forex, indices pick your own set in the sidebar), an AI-generated market recap that narrates *what already happened* today from price action and headlines (not a prediction), and a Finnhub-powered news feed auto-tagged by topic with an AI Bearish↔Bullish sentiment score.

**Federal Reserve & Macro Calendar**
The full FOMC meeting schedule with SEP/dot-plot markers, official BLS release dates for CPI and NFP, and a live wire of Fed press releases straight from federalreserve.gov.

**Quantitative Tools**
Historical Effective Fed Funds Rate from FRED, a backtest that scores how often Fed Funds futures correctly called the actual FOMC decision, and a 6-month rolling correlation heatmap across major crypto/forex/equity/rate instruments.

**AI Statement Analysis**
Paste any FOMC statement or Fed speech excerpt and get a -100 to +100 hawkish–dovish score with a plain-language explanation, powered by Llama-3.1 via Groq.

## Tech Stack

| Layer | Tools |
|---|---|
| Frontend | Streamlit, custom CSS (Fraunces + Inter + IBM Plex Mono) |
| Market Data | Yahoo Finance (prices, futures), FRED (Fed Funds Rate) |
| News | Finnhub API |
| Official Sources | federalreserve.gov (press releases, RSS), U.S. Bureau of Labor Statistics (CPI/NFP) |
| AI | Groq API — Llama-3.1-8b-instant |
| Charts | Plotly |

## Project Structure

```
market-pulse/
├── app.py                    Main Streamlit entry point
├── modules/
│   ├── data.py                Market snapshot, calendars, FRED, backtest, correlation
│   ├── news.py                 Finnhub news fetch + topic tagging
│   ├── fed_wire.py             Official Fed RSS feed + keyword lean heuristic
│   ├── ai_analysis.py          Groq-powered scoring (statement, news, recap)
│   ├── gauge.py                Theme-aware SVG sentiment gauge
│   └── styling.py              Theme palettes + injected CSS
├── .streamlit/config.toml     Streamlit theme config
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

**Prerequisites:** Python 3.9+, a free [Groq API key](https://console.groq.com/keys) for AI features, a free [Finnhub API key](https://finnhub.io/register) for the news feed.

```bash
git clone https://github.com/dimssrmdn01/market-pulse.git
cd market-pulse
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Add your keys to a `.env` file:
```
GROQ_API_KEY=gsk_...
FINNHUB_API_KEY=...
```

Then run it:
```bash
streamlit run app.py
```

The ticker, calendars, Fed Wire, rate history, and backtest all work with zero API keys only the news feed and AI-powered tabs need them.

## Deployment

Push to your own GitHub, then deploy free on [Streamlit Community Cloud](https://share.streamlit.io): select this repo and `app.py`, and under **Advanced settings → Secrets** add the same two keys in TOML format.

## Disclaimer

Educational and portfolio project. Market data, backtest results, and AI-generated scores are indicative estimates, not investment advice. Always verify official policy decisions and economic releases at [federalreserve.gov](https://www.federalreserve.gov) and [bls.gov](https://www.bls.gov).

## Author

Built by **Dimas Arya Ramadhan** — started as a single-purpose FOMC tracker, grown into a bilingual, multi-asset dashboard with live news, an official Fed wire, a real backtest, and cross-asset correlation analysis.

<div align="center">
  <sub>⭐ If this project is useful to you, consider starring the repo.</sub>
</div>
