"""
styling.py
Design tokens and injected CSS for Market Pulse.

Design direction: grounded in the actual visual vocabulary of US monetary
policy and financial markets — currency green, treasury parchment, gold-seal
accents, and the hawk/dove and bull/bear terminology analysts actually use.
Deliberately avoids the generic cream+terracotta / near-black+neon defaults.
"""

import streamlit as st

# ---- Design tokens -----------------------------------------------------
LEDGER_GREEN = "#0F2E1D"     # base dark surface, deep currency green
LEDGER_GREEN_2 = "#173C27"   # slightly lighter panel green
PARCHMENT = "#EDE6D6"        # light card / paper surface
PARCHMENT_DIM = "#DDD3BC"
TREASURY_GOLD = "#B9975B"    # accent, seal / foil
HAWK_RED = "#A63D40"         # rate-hike / inflation-hawk / bearish / price-down indicator
DOVE_BLUE = "#3E6E8E"        # rate-cut / dove indicator
BULL_GREEN = "#6FB98F"       # price-up / bullish indicator
INK = "#1B1B16"
CREAM_TEXT = "#F3EEDF"


def inject_css() -> None:
    st.markdown(
        f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3, .display {{ font-family: 'Fraunces', serif !important; }}
.mono {{ font-family: 'IBM Plex Mono', monospace !important; }}
.stApp {{
    background: radial-gradient(circle at 20% 0%, {LEDGER_GREEN_2} 0%, {LEDGER_GREEN} 55%, #081A11 100%);
    color: {CREAM_TEXT};
}}
#MainMenu, footer {{visibility: hidden;}}
.ledger-hero {{
    padding: 2.4rem 2.4rem 2rem 2.4rem;
    border-radius: 4px;
    background: linear-gradient(135deg, rgba(185,151,91,0.14), rgba(62,110,142,0.08));
    border: 1px solid rgba(185,151,91,0.35);
    position: relative;
    margin-bottom: 1.6rem;
}}
.ledger-hero::before {{
    content: "";
    position: absolute; inset: 8px;
    border: 1px solid rgba(185,151,91,0.18);
    border-radius: 2px;
    pointer-events: none;
}}
.ledger-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-size: 0.72rem;
    color: {TREASURY_GOLD};
    margin-bottom: 0.6rem;
}}
.ledger-rate {{
    font-family: 'Fraunces', serif;
    font-size: 3.4rem;
    font-weight: 600;
    color: {CREAM_TEXT};
    line-height: 1;
    margin: 0;
}}
.ledger-rate .unit {{ font-size: 1.4rem; color: {TREASURY_GOLD}; margin-left: 0.3rem;}}
.ledger-sub {{
    color: #C9C1A8;
    font-size: 0.95rem;
    margin-top: 0.6rem;
    max-width: 620px;
}}
.parchment-card {{
    background: {PARCHMENT};
    color: {INK};
    border-radius: 3px;
    padding: 1.2rem 1.4rem;
    border: 1px solid {PARCHMENT_DIM};
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
}}
.parchment-card .label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6B6250;
}}
.parchment-card .value {{
    font-family: 'Fraunces', serif;
    font-size: 1.65rem;
    font-weight: 600;
    margin-top: 0.15rem;
}}
.meeting-row {{
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.7rem 0.9rem;
    border-left: 3px solid rgba(185,151,91,0.3);
    margin-bottom: 0.35rem;
    border-radius: 2px;
    background: rgba(255,255,255,0.03);
}}
.meeting-row.is-next {{
    border-left-color: {TREASURY_GOLD};
    background: rgba(185,151,91,0.10);
}}
.meeting-date {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    min-width: 150px;
    color: {CREAM_TEXT};
}}
.meeting-tag {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 999px;
    background: rgba(185,151,91,0.18);
    color: {TREASURY_GOLD};
    border: 1px solid rgba(185,151,91,0.3);
}}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0B2417 0%, #071A10 100%);
    border-right: 1px solid rgba(185,151,91,0.15);
}}
section[data-testid="stSidebar"] .stTextInput input, section[data-testid="stSidebar"] textarea {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(185,151,91,0.25) !important;
    color: {CREAM_TEXT} !important;
    border-radius: 3px !important;
}}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{
    background: rgba(255,255,255,0.04);
    border-radius: 3px 3px 0 0;
    color: #C9C1A8;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.stTabs [aria-selected="true"] {{
    background: rgba(185,151,91,0.16) !important;
    color: {TREASURY_GOLD} !important;
}}
.stButton>button {{
    background: {TREASURY_GOLD};
    color: {INK};
    border: none;
    border-radius: 3px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
}}
.stButton>button:hover {{
    background: #CBA96C;
}}
.gauge-caption {{
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #C9C1A8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}}
.divider-line {{
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(185,151,91,0.4), transparent);
    margin: 1.6rem 0;
    border: none;
}}
.news-card {{
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.9rem 1rem;
    border-radius: 3px;
    background: rgba(255,255,255,0.03);
    border-left: 3px solid rgba(185,151,91,0.3);
    margin-bottom: 0.5rem;
}}
.news-card:hover {{
    background: rgba(185,151,91,0.07);
}}
.news-headline {{
    font-family: 'Fraunces', serif;
    font-size: 1.02rem;
    color: {CREAM_TEXT};
    margin: 0;
}}
.news-headline a {{
    color: {CREAM_TEXT};
    text-decoration: none;
}}
.news-headline a:hover {{
    color: {TREASURY_GOLD};
}}
.news-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9C9478;
}}
.news-tag {{
    display: inline-block;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1px 8px;
    border-radius: 999px;
    background: rgba(62,110,142,0.18);
    color: {DOVE_BLUE};
    border: 1px solid rgba(62,110,142,0.3);
    margin-right: 4px;
}}
.news-summary {{
    font-size: 0.85rem;
    color: #C9C1A8;
    margin-top: 0.15rem;
    line-height: 1.45;
}}
.ticker-strip {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-bottom: 1.4rem;
}}
.ticker-item {{
    flex: 1 1 140px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(185,151,91,0.18);
    border-radius: 3px;
    padding: 0.65rem 0.9rem;
}}
.ticker-symbol {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {TREASURY_GOLD};
}}
.ticker-price {{
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: {CREAM_TEXT};
    margin-top: 0.1rem;
}}
.ticker-change {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    margin-top: 0.15rem;
}}
.ticker-change.up {{ color: {BULL_GREEN}; }}
.ticker-change.down {{ color: {HAWK_RED}; }}
</style>
""",
        unsafe_allow_html=True,
    )
