"""
styling.py
Design tokens, theme palettes, and injected CSS for Market Pulse.

Multiple color themes are supported (Ledger Hijau, Midnight Slate, Terminal
Amber). inject_css() returns the active theme's color dict so Python-side
rendering (Plotly charts, inline HTML, the SVG gauge) can reuse the exact
same palette instead of hardcoding colors that would drift from the CSS.
"""

import streamlit as st

THEMES = {
    "ledger": {
        "display_name": "Ledger Hijau (Klasik)",
        "bg1": "#173C27",
        "bg2": "#0F2E1D",
        "bg3": "#081A11",
        "card": "#EDE6D6",
        "card_dim": "#DDD3BC",
        "accent": "#B9975B",
        "down": "#A63D40",
        "info": "#3E6E8E",
        "up": "#6FB98F",
        "ink": "#1B1B16",
        "text": "#F3EEDF",
        "text_dim": "#C9C1A8",
        "sidebar_label": "#9C9478",
    },
    "midnight": {
        "display_name": "Midnight Slate",
        "bg1": "#1E293B",
        "bg2": "#0F172A",
        "bg3": "#020617",
        "card": "#E2E8F0",
        "card_dim": "#CBD5E1",
        "accent": "#93C5FD",
        "down": "#F87171",
        "info": "#818CF8",
        "up": "#34D399",
        "ink": "#0F172A",
        "text": "#F1F5F9",
        "text_dim": "#94A3B8",
        "sidebar_label": "#64748B",
    },
    "amber": {
        "display_name": "Terminal Amber",
        "bg1": "#1A1A1A",
        "bg2": "#0A0A0A",
        "bg3": "#000000",
        "card": "#F5E6C8",
        "card_dim": "#E0C9A0",
        "accent": "#FFB000",
        "down": "#FF5F56",
        "info": "#5FA8D3",
        "up": "#4ADE80",
        "ink": "#1A1200",
        "text": "#FFD98A",
        "text_dim": "#B08B3E",
        "sidebar_label": "#8A6A2E",
    },
}
DEFAULT_THEME = "ledger"

# Backward-compatible module-level constants (ledger/default palette), for
# any code that still imports fixed color names directly.
LEDGER_GREEN = THEMES["ledger"]["bg2"]
LEDGER_GREEN_2 = THEMES["ledger"]["bg1"]
PARCHMENT = THEMES["ledger"]["card"]
PARCHMENT_DIM = THEMES["ledger"]["card_dim"]
TREASURY_GOLD = THEMES["ledger"]["accent"]
HAWK_RED = THEMES["ledger"]["down"]
DOVE_BLUE = THEMES["ledger"]["info"]
BULL_GREEN = THEMES["ledger"]["up"]
INK = THEMES["ledger"]["ink"]
CREAM_TEXT = THEMES["ledger"]["text"]


def get_theme(name: str) -> dict:
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def inject_css(theme_name: str = DEFAULT_THEME) -> dict:
    """
    Inject the CSS for the given theme and return its color dict, so the
    caller can reuse the exact same palette for Python-rendered elements
    (Plotly charts, the SVG gauge, inline f-string HTML).
    """
    t = get_theme(theme_name)
    st.markdown(
        f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3, .display {{ font-family: 'Fraunces', serif !important; }}
.mono {{ font-family: 'IBM Plex Mono', monospace !important; }}
.stApp {{
    background: radial-gradient(circle at 20% 0%, {t['bg1']} 0%, {t['bg2']} 55%, {t['bg3']} 100%);
    color: {t['text']};
}}
#MainMenu, footer {{visibility: hidden;}}
.ledger-hero {{
    padding: 2.4rem 2.4rem 2rem 2.4rem;
    border-radius: 4px;
    background: linear-gradient(135deg, {t['accent']}24, {t['info']}14);
    border: 1px solid {t['accent']}59;
    position: relative;
    margin-bottom: 1.6rem;
}}
.ledger-hero::before {{
    content: "";
    position: absolute; inset: 8px;
    border: 1px solid {t['accent']}2e;
    border-radius: 2px;
    pointer-events: none;
}}
.ledger-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-size: 0.72rem;
    color: {t['accent']};
    margin-bottom: 0.6rem;
}}
.ledger-rate {{
    font-family: 'Fraunces', serif;
    font-size: 3.4rem;
    font-weight: 600;
    color: {t['text']};
    line-height: 1;
    margin: 0;
}}
.ledger-rate .unit {{ font-size: 1.4rem; color: {t['accent']}; margin-left: 0.3rem;}}
.ledger-sub {{
    color: {t['text_dim']};
    font-size: 0.95rem;
    margin-top: 0.6rem;
    max-width: 620px;
}}
.parchment-card {{
    background: {t['card']};
    color: {t['ink']};
    border-radius: 3px;
    padding: 1.2rem 1.4rem;
    border: 1px solid {t['card_dim']};
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
    border-left: 3px solid {t['accent']}4d;
    margin-bottom: 0.35rem;
    border-radius: 2px;
    background: rgba(255,255,255,0.03);
}}
.meeting-row.is-next {{
    border-left-color: {t['accent']};
    background: {t['accent']}1a;
}}
.meeting-date {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    min-width: 150px;
    color: {t['text']};
}}
.meeting-tag {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 999px;
    background: {t['accent']}2e;
    color: {t['accent']};
    border: 1px solid {t['accent']}4d;
}}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {t['bg2']} 0%, {t['bg3']} 100%);
    border-right: 1px solid {t['accent']}26;
}}
section[data-testid="stSidebar"] .stTextInput input, section[data-testid="stSidebar"] textarea {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid {t['accent']}40 !important;
    color: {t['text']} !important;
    border-radius: 3px !important;
}}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
.stTabs [data-baseweb="tab"] {{
    background: rgba(255,255,255,0.04);
    border-radius: 3px 3px 0 0;
    color: {t['text_dim']};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}
.stTabs [aria-selected="true"] {{
    background: {t['accent']}29 !important;
    color: {t['accent']} !important;
}}
.stButton>button {{
    background: {t['accent']};
    color: {t['ink']};
    border: none;
    border-radius: 3px;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
}}
.stButton>button:hover {{
    filter: brightness(1.12);
}}
.gauge-caption {{
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: {t['text_dim']};
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}}
.divider-line {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {t['accent']}66, transparent);
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
    border-left: 3px solid {t['accent']}4d;
    margin-bottom: 0.5rem;
}}
.news-card:hover {{
    background: {t['accent']}12;
}}
.news-headline {{
    font-family: 'Fraunces', serif;
    font-size: 1.02rem;
    color: {t['text']};
    margin: 0;
}}
.news-headline a {{
    color: {t['text']};
    text-decoration: none;
}}
.news-headline a:hover {{
    color: {t['accent']};
}}
.news-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['sidebar_label']};
}}
.news-tag {{
    display: inline-block;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1px 8px;
    border-radius: 999px;
    background: {t['info']}2e;
    color: {t['info']};
    border: 1px solid {t['info']}4d;
    margin-right: 4px;
}}
.news-summary {{
    font-size: 0.85rem;
    color: {t['text_dim']};
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
    border: 1px solid {t['accent']}2e;
    border-radius: 3px;
    padding: 0.65rem 0.9rem;
}}
.ticker-symbol {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: {t['accent']};
}}
.ticker-price {{
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: {t['text']};
    margin-top: 0.1rem;
}}
.ticker-change {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    margin-top: 0.15rem;
}}
.ticker-change.up {{ color: {t['up']}; }}
.ticker-change.down {{ color: {t['down']}; }}
.wire-row {{
    padding: 0.7rem 0.9rem;
    border-left: 3px solid {t['accent']}4d;
    margin-bottom: 0.4rem;
    border-radius: 2px;
    background: rgba(255,255,255,0.03);
}}
.wire-title {{
    font-family: 'Fraunces', serif;
    font-size: 0.98rem;
    color: {t['text']};
    margin: 0;
}}
.wire-title a {{ color: {t['text']}; text-decoration: none; }}
.wire-title a:hover {{ color: {t['accent']}; }}
.wire-meta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: {t['sidebar_label']};
    margin-top: 0.2rem;
}}
.wire-lean {{
    display: inline-block;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1px 8px;
    border-radius: 999px;
    margin-top: 0.3rem;
}}
.wire-lean.hawkish {{ background: {t['down']}2e; color: {t['down']}; border: 1px solid {t['down']}4d; }}
.wire-lean.dovish {{ background: {t['info']}2e; color: {t['info']}; border: 1px solid {t['info']}4d; }}
.wire-lean.neutral {{ background: {t['accent']}2e; color: {t['accent']}; border: 1px solid {t['accent']}4d; }}
</style>
""",
        unsafe_allow_html=True,
    )
    return t