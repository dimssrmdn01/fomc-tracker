"""
ai_analysis.py
Uses Groq (Llama-3.1) for two kinds of scoring:

1. analyze_statement()      - FOMC statement text -> Hawkish <-> Dovish scale
                               (monetary-policy specific, unchanged behavior)
2. analyze_news_sentiment() - a batch of general market headlines -> Bearish
                               <-> Bullish scale (for the broader news feed)

Both return a structured JSON verdict parsed defensively, and raise
ValueError with a friendly Indonesian message on any failure so the UI
layer can display it without crashing.
"""
from __future__ import annotations
import json
import re
from groq import Groq

# ---------------------------------------------------------------------
# 1. FOMC statement -> hawkish/dovish (original behavior, untouched)
# ---------------------------------------------------------------------
SYSTEM_PROMPT = """You are a monetary policy analyst. You will be given the text of an \
FOMC (Federal Open Market Committee) statement or press conference excerpt. \
Score it on a hawkish-dovish scale and explain your reasoning briefly.
Return ONLY valid JSON, no markdown fences, no preamble, in exactly this shape:
{
  "score": <integer from -100 (extremely dovish) to 100 (extremely hawkish), 0 = neutral>,
  "label": "<one of: Very Dovish, Dovish, Neutral, Hawkish, Very Hawkish>",
  "summary": "<2-3 sentence plain-language summary of the key stance, in Indonesian>",
  "key_phrases": ["<up to 4 short phrases from the text that most influenced the score>"]
}
"""


def analyze_statement(statement_text: str, api_key: str, model: str = "llama-3.1-8b-instant") -> dict:
    """
    Send FOMC statement text to Groq for hawkish/dovish scoring.
    """
    if not statement_text or len(statement_text.strip()) < 50:
        raise ValueError("Teks statement terlalu pendek untuk dianalisis. Tempel minimal satu paragraf penuh.")
    if not api_key:
        raise ValueError("Groq API key belum diisi. Masukkan di sidebar terlebih dahulu.")

    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": statement_text[:6000]},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        raw = completion.choices[0].message.content.strip()
    except Exception as exc:
        raise ValueError(f"Gagal menghubungi Groq API: {exc}") from exc

    return _parse_score_response(raw)


SAMPLE_STATEMENT = """The Committee decided to maintain the target range for the federal \
funds rate at 3-1/2 to 3-3/4 percent, in support of the Federal Reserve's dual mandate. \
The Committee reaffirmed its policy of maintaining ample reserves in the banking system. \
Economic activity is expanding at a solid pace despite elevated uncertainty. Inflation \
remains somewhat elevated relative to the Committee's 2 percent longer-run goal. The \
Committee will continue to monitor the implications of incoming information for the \
economic outlook and is prepared to adjust the stance of monetary policy as appropriate \
if risks emerge that could impede the attainment of the Committee's goals."""


# ---------------------------------------------------------------------
# 2. General market news -> bearish/bullish (new)
# ---------------------------------------------------------------------
NEWS_SYSTEM_PROMPT = """You are a financial markets analyst. You will be given a batch of \
recent economic and financial news headlines with short summaries. Assess the OVERALL \
market sentiment they convey and explain your reasoning briefly.
Return ONLY valid JSON, no markdown fences, no preamble, in exactly this shape:
{
  "score": <integer from -100 (extremely bearish / negative for markets) to 100 (extremely bullish / positive), 0 = neutral>,
  "label": "<one of: Very Bearish, Bearish, Neutral, Bullish, Very Bullish>",
  "summary": "<2-3 sentence plain-language summary of the overall market mood, in Indonesian>",
  "key_phrases": ["<up to 4 short headlines/phrases that most influenced the score>"]
}
"""


def analyze_news_sentiment(
    headlines: list[str], api_key: str, model: str = "llama-3.1-8b-instant"
) -> dict:
    """
    Send a batch of general market news headlines/summaries to Groq and get
    back an overall bearish/bullish market-sentiment verdict.
    """
    if not headlines:
        raise ValueError("Tidak ada berita untuk dianalisis.")
    if not api_key:
        raise ValueError("Groq API key belum diisi. Masukkan di sidebar terlebih dahulu.")

    joined = "\n".join(f"- {h}" for h in headlines[:40])

    client = Groq(api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": NEWS_SYSTEM_PROMPT},
                {"role": "user", "content": joined[:6000]},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        raw = completion.choices[0].message.content.strip()
    except Exception as exc:
        raise ValueError(f"Gagal menghubungi Groq API: {exc}") from exc

    return _parse_score_response(raw)


# ---------------------------------------------------------------------
# Shared defensive JSON parsing for both scoring functions
# ---------------------------------------------------------------------
def _parse_score_response(raw: str) -> dict:
    import re
    import json
    
    # 1. Pastikan string tidak kosong
    if not raw or not raw.strip():
        return {
            "score": 0,
            "label": "NETRAL",
            "summary": "API Groq mengembalikan respons kosong. Coba muat ulang.",
            "key_phrases": ["Empty Response"]
        }
        
    raw = raw.strip()
    
    # 
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        raw_json = match.group(0)
    else:
        raw_json = raw # Fallback kalau regex gak nemu kurung kurawal

    #
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "score": 0,
            "label": "NETRAL",
            "summary": f"Gagal membaca format AI. (Error: {str(exc)}). Silakan coba lagi.",
            "key_phrases": ["JSON Error"]
        }

    # 
    required = {"score", "label", "summary", "key_phrases"}
    if not required.issubset(data.keys()):
        return {
            "score": 0,
            "label": "NETRAL",
            "summary": "Respons AI berhasil dibaca tapi ada data yang kurang lengkap.",
            "key_phrases": ["Incomplete Data"]
        }

    # 
    try:
        data["score"] = max(-100, min(100, int(data["score"])))
    except (ValueError, TypeError):
        data["score"] = 0

    return data