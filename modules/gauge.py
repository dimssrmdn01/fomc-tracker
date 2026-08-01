"""
gauge.py
The signature visual element of the app: a hand-drawn-style semicircular
"Hawk-Dove Meter" that renders the AI sentiment score (-100 to 100) as a
needle position, echoing the exact vocabulary Fed-watchers use.
"""

import math

from .styling import DOVE_BLUE, HAWK_RED, TREASURY_GOLD, PARCHMENT, INK


def render_hawk_dove_gauge(score: int, label: str) -> str:
    """
    score: -100 (very dovish) to 100 (very hawkish)
    Returns raw SVG markup for a semicircular gauge with a needle.
    """
    score = max(-100, min(100, score))
    # Map score (-100..100) to angle (180deg..0deg) across a semicircle.
    angle_deg = 180 - ((score + 100) / 200) * 180
    angle_rad = math.radians(angle_deg)

    cx, cy, r = 200, 190, 150
    needle_len = 128
    nx = cx + needle_len * math.cos(angle_rad)
    ny = cy - needle_len * math.sin(angle_rad)

    # Tick marks every 20 degrees across the arc for a ledger/instrument feel.
    ticks = []
    for i in range(0, 181, 30):
        a = math.radians(i)
        x1 = cx + (r - 6) * math.cos(a)
        y1 = cy - (r - 6) * math.sin(a)
        x2 = cx + (r + 6) * math.cos(a)
        y2 = cy - (r + 6) * math.sin(a)
        ticks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{PARCHMENT}" stroke-width="2" opacity="0.55"/>')
    ticks_svg = "\n".join(ticks)

    svg = f"""
<svg viewBox="0 0 400 240" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{DOVE_BLUE}"/>
      <stop offset="50%" stop-color="{TREASURY_GOLD}"/>
      <stop offset="100%" stop-color="{HAWK_RED}"/>
    </linearGradient>
  </defs>

  <path d="M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
        fill="none" stroke="url(#arcGradient)" stroke-width="18" stroke-linecap="round"/>

  {ticks_svg}

  <text x="{cx - r - 6}" y="{cy + 26}" font-family="IBM Plex Mono, monospace" font-size="12" fill="{DOVE_BLUE}" text-anchor="start">DOVISH</text>
  <text x="{cx + r + 6}" y="{cy + 26}" font-family="IBM Plex Mono, monospace" font-size="12" fill="{HAWK_RED}" text-anchor="end">HAWKISH</text>

  <circle cx="{cx}" cy="{cy}" r="9" fill="{TREASURY_GOLD}" stroke="{PARCHMENT}" stroke-width="2"/>
  <line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{PARCHMENT}" stroke-width="4" stroke-linecap="round"/>
  <circle cx="{nx:.1f}" cy="{ny:.1f}" r="5" fill="{PARCHMENT}"/>

  <text x="{cx}" y="{cy - 40}" font-family="Fraunces, serif" font-size="26" font-weight="600" fill="{PARCHMENT}" text-anchor="middle">{score:+d}</text>
  <text x="{cx}" y="{cy - 16}" font-family="IBM Plex Mono, monospace" font-size="13" letter-spacing="1" fill="{TREASURY_GOLD}" text-anchor="middle">{label.upper()}</text>
</svg>
"""
    return svg
