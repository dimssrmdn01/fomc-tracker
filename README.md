<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fraunces&weight=600&size=30&pause=1000&color=B9975B&center=true&vCenter=true&width=650&lines=FOMC+Tracker;Federal+Reserve+Policy+Dashboard;Hawkish+%2F+Dovish+AI+Analysis;Real-Time+Rate+Probabilities" alt="Typing SVG" />
</div>

<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F2E1D,100:B9975B&height=150&section=header&text=FOMC%20Tracker&fontSize=38&fontColor=F3EEDF&fontAlignY=38&desc=Federal%20Reserve%20Monetary%20Policy%20Dashboard&descAlignY=58&descSize=16" alt="Banner" width="100%">
</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-1c100b?style=for-the-badge&logo=python&logoColor=B9975B)
![Streamlit](https://img.shields.io/badge/Streamlit-1c100b?style=for-the-badge&logo=streamlit&logoColor=FF4B4B)
![Groq](https://img.shields.io/badge/Groq-1c100b?style=for-the-badge&logo=groq&logoColor=F59E0B)
![Plotly](https://img.shields.io/badge/Plotly-1c100b?style=for-the-badge&logo=plotly&logoColor=3F4F75)

</div>

## Overview

**FOMC Tracker** is a dashboard for following US Federal Reserve monetary policy: the meeting calendar, historical Federal Funds Rate, market-implied move probabilities derived from Fed Funds futures, and an AI-powered hawkish/dovish sentiment score for any FOMC statement text.

The visual design is deliberately grounded in the vocabulary of the subject itself — currency green, treasury parchment, gold-seal accents, and a hand-drawn hawk/dove instrument gauge — rather than a generic dashboard template.

## Features

| Feature | Description |
|---|---|
| **Meeting Calendar** | Full 2026 FOMC schedule with a live countdown to the next decision and SEP/dot-plot markers |
| **Rate History Chart** | Effective Federal Funds Rate pulled live from FRED, with graceful fallback if the network call fails |
| **Move Probabilities** | Cut / Hold / Hike odds estimated from 30-Day Fed Funds futures (CME ZQ), in the spirit of the CME FedWatch methodology |
| **AI Sentiment Analysis** | Paste any FOMC statement or speech excerpt; Llama-3.1 (via Groq) scores it -100 to +100 on a hawkish-dovish scale and explains why |
| **Hawk-Dove Gauge** | A custom SVG instrument gauge visualizing the AI sentiment score |

## Tech Stack

- **Frontend:** Streamlit, custom CSS (Fraunces + Inter + IBM Plex Mono)
- **Data:** FRED (Federal Reserve Economic Data), Yahoo Finance (Fed Funds futures)
- **AI:** Groq API, Llama-3.1-8b-instant
- **Charts:** Plotly

## Project Structure

```
fomc-tracker/
├── app.py                  # Main Streamlit entry point
├── modules/
│   ├── data.py              # FOMC calendar, FRED fetch, probability model
│   ├── ai_analysis.py        # Groq-powered hawkish/dovish scoring
│   ├── gauge.py              # SVG hawk-dove gauge renderer
│   └── styling.py            # Design tokens + injected CSS
├── .streamlit/
│   └── config.toml           # Streamlit theme config
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- A free Groq API key ([console.groq.com/keys](https://console.groq.com/keys)) — only needed for the AI Analysis tab

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

### 4. Run Locally
```bash
streamlit run app.py
```
The app opens at `http://localhost:8501`. Enter your Groq API key in the sidebar to use the AI Analysis tab — the calendar, rate history, and probability tabs work without any key.

## Deployment (Streamlit Community Cloud)

1. Push this repo to your own GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, select this repository and `app.py` as the entry point.
4. (Optional) Under **Advanced settings → Secrets**, add:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
5. Click **Deploy**.

## Disclaimer

This is an educational/portfolio project. Rate probabilities and AI-generated sentiment scores are indicative estimates, not investment advice. Always verify official policy decisions at [federalreserve.gov](https://www.federalreserve.gov).

## Author

Built by **[isi nama kamu di sini]** — an upgraded take on an FOMC tracking concept, with a new architecture, live data sources, and AI-powered sentiment analysis.
