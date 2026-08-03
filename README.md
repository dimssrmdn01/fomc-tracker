<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fraunces&weight=600&size=30&pause=1000&color=B9975B&center=true&vCenter=true&width=650&lines=Market+Pulse;Crypto+%2C+Forex+%26+Stocks+Dashboard;FOMC+Hawkish+%2F+Dovish+AI+Analysis;Real-Time+Multi-Asset+Snapshot" alt="Typing SVG" />
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F2E1D,100:B9975B&height=150&section=header&text=Market%20Pulse&fontSize=38&fontColor=F3EEDF&fontAlignY=38&desc=Economic%20%26%20Financial%20Markets%20Dashboard&descAlignY=58&descSize=16" alt="Banner" width="100%">
</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-1c100b?style=for-the-badge&logo=python&logoColor=B9975B)
![Streamlit](https://img.shields.io/badge/Streamlit-1c100b?style=for-the-badge&logo=streamlit&logoColor=FF4B4B)
![Groq](https://img.shields.io/badge/Groq-1c100b?style=for-the-badge&logo=groq&logoColor=F59E0B)
![Finnhub](https://img.shields.io/badge/Finnhub-1c100b?style=for-the-badge&logo=data:image/svg+xml;base64,&logoColor=00C48C)
![Plotly](https://img.shields.io/badge/Plotly-1c100b?style=for-the-badge&logo=plotly&logoColor=3F4F75)

</div>

## Overview

**Market Pulse** is a dashboard for following crypto, forex, and stock markets alongside US Federal Reserve monetary policy: a live multi-asset price ticker, an economic/financial news feed with AI sentiment scoring, the official Fed press-release wire, the FOMC meeting calendar plus CPI and NFP release schedules, historical Fed Funds Rate, market-implied move probabilities, and an AI-powered hawkish/dovish score for any FOMC statement text.

The visual design is deliberately grounded in the vocabulary of the subject itself — currency green, treasury parchment, gold-seal accents, and a hand-drawn hawk/dove instrument gauge — rather than a generic dashboard template. Three color themes are available (Ledger Hijau, Midnight Slate, Terminal Amber).

## Features

| Feature | Description |
|---|---|
| **Multi-Asset Ticker** | Live BTC, ETH, SOL, EUR/USD, USD/JPY, USD/IDR, S&P 500, and Nasdaq prices with % change, pulled via Yahoo Finance |
| **Berita Pasar (News Feed)** | Economic & financial news from Finnhub across general, forex, and crypto categories, auto-tagged by topic (Bank Sentral, Inflasi, Pasar Saham, Kripto, Forex, Komoditas) |
| **Market Sentiment (AI)** | AI-scored Bearish ↔ Bullish read on the overall mood of the current news feed |
| **Fed Wire** | Official Federal Reserve press-release RSS feed, with a lightweight keyword-based Hawkish/Dovish/Neutral lean (clearly labeled as a rough heuristic, not an NLP model) |
| **FOMC Meeting Calendar** | Full 2026 FOMC schedule with a live countdown to the next decision and SEP/dot-plot markers |
| **CPI & NFP Calendars** | Official U.S. Bureau of Labor Statistics release schedules for CPI and the Employment Situation (NFP) report |
| **Rate History Chart** | Effective Federal Funds Rate pulled live from FRED, with graceful fallback if the network call fails |
| **Move Probabilities** | Cut / Hold / Hike odds estimated from 30-Day Fed Funds futures (CME ZQ), in the spirit of the CME FedWatch methodology |
| **FOMC Statement Analysis (AI)** | Paste any FOMC statement or speech excerpt; Llama-3.1 (via Groq) scores it -100 to +100 on a hawkish-dovish scale and explains why |
| **Hawk-Dove / Bear-Bull Gauge** | A custom SVG instrument gauge, reused for both the FOMC statement score and the general market sentiment score |
| **Theme Selector** | Three color palettes (Ledger Hijau, Midnight Slate, Terminal Amber), applied consistently across charts, the gauge, and all UI elements |

## Tech Stack

- **Frontend:** Streamlit, custom CSS (Fraunces + Inter + IBM Plex Mono)
- **Market Data:** Yahoo Finance (crypto/forex/stock prices, Fed Funds futures), FRED (Federal Reserve Economic Data)
- **News:** Finnhub API (general/forex/crypto market news)
- **Official Sources:** federalreserve.gov (press releases, RSS wire), U.S. Bureau of Labor Statistics (CPI/NFP calendars)
- **AI:** Groq API, Llama-3.1-8b-instant
- **Charts:** Plotly

## Project Structure

```
fomc-tracker/
├── app.py                  # Main Streamlit entry point
├── modules/
│   ├── data.py              # Market snapshot, FOMC/CPI/NFP calendars, FRED fetch, probability model
│   ├── news.py               # Finnhub news fetch + topic tagging
│   ├── fed_wire.py           # Official Fed RSS feed + keyword lean heuristic
│   ├── ai_analysis.py        # Groq-powered hawkish/dovish and bearish/bullish scoring
│   ├── gauge.py              # Theme-aware SVG sentiment gauge renderer
│   └── styling.py            # Theme palettes + injected CSS
├── .streamlit/
│   └── config.toml           # Streamlit theme config
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- A free Groq API key ([console.groq.com/keys](https://console.groq.com/keys)) — only needed for the AI Analysis tabs
- A free Finnhub API key ([finnhub.io/register](https://finnhub.io/register)) — only needed for the Berita Pasar (news) tab

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/fomc-tracker.git
cd fomc-tracker
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys (optional but recommended)
Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_...
FINNHUB_API_KEY=...
```
The app also reads these from Streamlit secrets on Streamlit Cloud — see Deployment below. Without them, the app still runs; the sidebar will prompt for manual entry when a key-dependent tab is opened.

### 5. Run Locally
```bash
streamlit run app.py
```
The app opens at `http://localhost:8501`. The multi-asset ticker, FOMC calendar, CPI/NFP schedules, Fed Wire, and rate history work with no keys at all.

## Deployment (Streamlit Community Cloud)

1. Push this repo to your own GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select this repository and `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_..."
   FINNHUB_API_KEY = "..."
   ```
5. Click **Deploy**.

## Disclaimer

This is an educational/portfolio project. Market data, rate probabilities, and AI-generated sentiment scores (including the Fed Wire's keyword-based lean) are indicative estimates only, not investment advice. Always verify official policy decisions and economic releases at [federalreserve.gov](https://www.federalreserve.gov) and [bls.gov](https://www.bls.gov).

## Author

Built by **Dimas Arya Ramadhan** — an upgraded take on an FOMC tracking concept, expanded into a broader crypto/forex/stocks dashboard with live multi-source news, an official Fed RSS wire, and AI-powered sentiment analysis.
