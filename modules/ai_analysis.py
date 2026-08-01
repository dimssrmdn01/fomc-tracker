"""
ai_analysis.py
Uses Groq (Llama-3.1) to score FOMC statement text on a Hawkish <-> Dovish
scale and produce a plain-language summary. The user pastes the statement
text (or the app fetches the latest one from the Fed's press-release page)
and the model returns a structured JSON verdict.
"""

from __future__ import annotations

import json
import re

from groq import Groq

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
    Raises ValueError with a friendly message on any failure so the UI
    layer can display it without crashing.
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

    # Defensive parsing: strip markdown fences if the model adds them anyway.
    raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Respons AI tidak dalam format JSON yang valid: {exc}") from exc

    required = {"score", "label", "summary", "key_phrases"}
    if not required.issubset(data.keys()):
        raise ValueError("Respons AI tidak lengkap, coba ulangi analisis.")

    data["score"] = max(-100, min(100, int(data["score"])))
    return data


SAMPLE_STATEMENT = """The Committee decided to maintain the target range for the federal \
funds rate at 3-1/2 to 3-3/4 percent, in support of the Federal Reserve's dual mandate. \
The Committee reaffirmed its policy of maintaining ample reserves in the banking system. \
Economic activity is expanding at a solid pace despite elevated uncertainty. Inflation \
remains somewhat elevated relative to the Committee's 2 percent longer-run goal. The \
Committee will continue to monitor the implications of incoming information for the \
economic outlook and is prepared to adjust the stance of monetary policy as appropriate \
if risks emerge that could impede the attainment of the Committee's goals."""
