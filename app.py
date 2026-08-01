import datetime as dt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from modules import ai_analysis, data
from modules.gauge import render_hawk_dove_gauge
from modules.styling import (
    CREAM_TEXT,
    DOVE_BLUE,
    HAWK_RED,
    TREASURY_GOLD,
    inject_css,
)

load_dotenv()

st.set_page_config(
    page_title="FOMC Tracker",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

#CSS FIX: SUPER MINIMALIS 
st.html("""
<style>
    /* 1. Biarkan header tetap hidup, tapi backgroundnya dibikin transparan */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* 2. Sembunyikan HANYA tombol Deploy (biar estetika tetap premium) */
    .stAppDeployButton {
        display: none !important;
    }

    /* 3. Warnai tombol sidebar bawaan Streamlit biar kelihatan jelas (krem -> emas saat di-hover) */
    [data-testid="stHeader"] button {
        color: #F3EEDF !important;
    }
    [data-testid="stHeader"] button:hover {
        color: #B9975B !important;
    }
</style>
""")

# -------------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<p style='font-family:Fraunces,serif; font-size:1.3rem; color:#F3EEDF; margin-bottom:0;'>FOMC Tracker</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#9C9478; font-size:0.8rem; margin-top:0;'>Federal Reserve policy dashboard</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.08em; color:#B9975B;'>AI Analysis Config</p>",
        unsafe_allow_html=True,
    )
    groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.caption("Dapatkan gratis di [console.groq.com](https://console.groq.com/keys)")

    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:0.78rem; color:#9C9478;'>Data historis: FRED (Federal Reserve Economic Data)"
        "<br>Probabilitas pasar: 30-Day Fed Funds Futures (CME ZQ)"
        "<br>Analisis sentimen: Llama-3.1 via Groq</p>",
        unsafe_allow_html=True,
    )

# -------------------------------------------------------------------------
# HERO - current rate + next meeting countdown
# -------------------------------------------------------------------------
today = dt.date.today()
next_meeting = data.get_next_meeting(today)
lower, upper = data.CURRENT_TARGET_RANGE

hero_col1, hero_col2 = st.columns([2, 1])
with hero_col1:
    days_label = f"{next_meeting.days_away} hari lagi" if next_meeting and next_meeting.days_away > 0 else "Sedang berlangsung / baru saja selesai"
    st.markdown(
        f"""
<div class="ledger-hero">
    <div class="ledger-eyebrow">Federal Open Market Committee &middot; Target Range</div>
    <p class="ledger-rate">{lower:.2f}<span class="unit">%</span> &ndash; {upper:.2f}<span class="unit">%</span></p>
    <p class="ledger-sub">
        Rapat FOMC berikutnya: <strong>{next_meeting.start.strftime('%d %B') if next_meeting else '—'}
        &ndash; {next_meeting.end.strftime('%d %B %Y') if next_meeting else '—'}</strong>
        &middot; {days_label}
        {" &middot; disertai Summary of Economic Projections (dot plot)" if next_meeting and next_meeting.has_sep else ""}
    </p>
</div>
""",
        unsafe_allow_html=True,
    )
with hero_col2:
    probs = data.estimate_move_probabilities()
    st.markdown(
        f"""
<div class="parchment-card">
    <div class="label">Probabilitas Pasar &middot; Rapat Berikutnya</div>
    <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'IBM Plex Mono',monospace;">
        <div><div style="color:{DOVE_BLUE}; font-weight:600; font-size:1.1rem;">{probs['cut']}%</div><div style="font-size:0.7rem;">CUT</div></div>
        <div><div style="color:#6B6250; font-weight:600; font-size:1.1rem;">{probs['hold']}%</div><div style="font-size:0.7rem;">HOLD</div></div>
        <div><div style="color:{HAWK_RED}; font-weight:600; font-size:1.1rem;">{probs['hike']}%</div><div style="font-size:0.7rem;">HIKE</div></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if probs["source"] == "fallback":
        st.caption("⚠ Data futures live tidak tersedia — menampilkan estimasi cadangan.")

st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------------
tab_calendar, tab_history, tab_ai = st.tabs(["Kalender Rapat", "Riwayat Suku Bunga", "Analisis AI"])

with tab_calendar:
    st.markdown("#### Jadwal Rapat FOMC 2026")
    schedule = data.get_meeting_schedule(today)
    for m in schedule:
        css_class = "meeting-row is-next" if m.is_next else "meeting-row"
        status = "→ RAPAT BERIKUTNYA" if m.is_next else ("selesai" if m.end < today else "")
        sep_tag = '<span class="meeting-tag">SEP + Dot Plot</span>' if m.has_sep else ""
        
        st.html(
            f"""
<div class="{css_class}">
    <div class="meeting-date">{m.start.strftime('%d %b')} &ndash; {m.end.strftime('%d %b %Y')}</div>
    {sep_tag}
    <div style="margin-left:auto; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:{TREASURY_GOLD if m.is_next else '#9C9478'};">{status}</div>
</div>
"""
        )
    st.caption("Empat dari delapan rapat (Maret, Juni, September, Desember) disertai Summary of Economic Projections (dot plot).")

with tab_history:
    st.markdown("#### Riwayat Effective Federal Funds Rate")
    with st.spinner("Mengambil data dari FRED..."):
        rate_df = data.fetch_fed_funds_rate_history(lookback_days=730)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rate_df["date"],
            y=rate_df["rate"],
            mode="lines",
            line=dict(color=TREASURY_GOLD, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(185,151,91,0.10)",
            name="Effective Fed Funds Rate",
        )
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=CREAM_TEXT, family="Inter"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Rate (%)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Sumber: FRED series DFF (Effective Federal Funds Rate), Federal Reserve Bank of St. Louis.")

with tab_ai:
    st.markdown("#### Analisis Sentimen Hawkish / Dovish")
    st.caption(
        "Tempel teks statement FOMC (atau bagian pidato Chair), atau ambil otomatis rilis resmi terakhir. "
        "AI akan menilai kecenderungan kebijakan pada skala -100 (sangat dovish) sampai +100 (sangat hawkish)."
    )

    source_choice = st.radio(
        "Sumber teks",
        ["Ambil otomatis dari federalreserve.gov", "Tempel manual", "Contoh statement (Juli 2026)"],
        horizontal=True,
    )

    if "statement_buffer" not in st.session_state:
        st.session_state["statement_buffer"] = ""

    if source_choice == "Ambil otomatis dari federalreserve.gov":
        if st.button("Ambil Statement Terbaru"):
            try:
                with st.spinner("Mengambil rilis resmi dari federalreserve.gov..."):
                    fetched = data.fetch_latest_statement_text()
                st.session_state["statement_buffer"] = fetched["text"]
                st.success(f"Berhasil diambil — rilis rapat {fetched['meeting_date'].strftime('%d %B %Y')}. [Lihat sumber]({fetched['url']})")
            except ValueError as e:
                st.error(str(e))
        statement_text = st.text_area("Teks Statement FOMC", value=st.session_state["statement_buffer"], height=200)
    elif source_choice == "Contoh statement (Juli 2026)":
        statement_text = st.text_area("Teks Statement FOMC", value=ai_analysis.SAMPLE_STATEMENT, height=200)
    else:
        statement_text = st.text_area(
            "Teks Statement FOMC", value="", height=200, placeholder="Tempel teks statement di sini..."
        )

    analyze_clicked = st.button("Analisis Sekarang", type="primary")

    if "analysis_history" not in st.session_state:
        st.session_state["analysis_history"] = []

    if analyze_clicked:
        if not groq_api_key:
            st.error("Masukkan Groq API Key di sidebar terlebih dahulu.")
        else:
            try:
                with st.spinner("Menganalisis nada kebijakan..."):
                    result = ai_analysis.analyze_statement(statement_text, groq_api_key)
                st.session_state["last_analysis"] = result
                st.session_state["analysis_history"].append(
                    {
                        "waktu": dt.datetime.now().strftime("%H:%M:%S"),
                        "score": result["score"],
                        "label": result["label"],
                    }
                )
            except ValueError as e:
                st.error(str(e))

    if "last_analysis" in st.session_state:
        result = st.session_state["last_analysis"]
        col_gauge, col_detail = st.columns([1, 1.3])
        with col_gauge:
            st.markdown(render_hawk_dove_gauge(result["score"], result["label"]), unsafe_allow_html=True)
            st.markdown('<div class="gauge-caption">Skor Sentimen Kebijakan</div>', unsafe_allow_html=True)
        with col_detail:
            st.markdown(
                f"""
<div class="parchment-card">
    <div class="label">Ringkasan</div>
    <p style="margin-top:0.5rem; line-height:1.5;">{result['summary']}</p>
    <div class="label" style="margin-top:1rem;">Frasa Kunci</div>
    <ul style="margin-top:0.4rem;">
        {''.join(f'<li>{p}</li>' for p in result['key_phrases'])}
    </ul>
</div>
""",
                unsafe_allow_html=True,
            )

    if len(st.session_state["analysis_history"]) > 1:
        st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
        st.markdown("##### Tren Skor Sentimen (sesi ini)")
        hist_df = pd.DataFrame(st.session_state["analysis_history"])
        fig_hist = go.Figure()
        fig_hist.add_trace(
            go.Scatter(
                x=list(range(1, len(hist_df) + 1)),
                y=hist_df["score"],
                mode="lines+markers+text",
                text=hist_df["label"],
                textposition="top center",
                line=dict(color=TREASURY_GOLD, width=2),
                marker=dict(size=9, color=TREASURY_GOLD),
            )
        )
        fig_hist.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.25)")
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=CREAM_TEXT, family="Inter"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=280,
            yaxis=dict(range=[-105, 105], title="Skor", gridcolor="rgba(255,255,255,0.08)"),
            xaxis=dict(title="Urutan analisis dalam sesi ini", dtick=1),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Riwayat ini hanya tersimpan selama sesi browser aktif dan akan hilang saat halaman di-refresh.")

st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
st.caption(
    "FOMC Tracker adalah proyek edukasi dan portofolio. Data pasar dan estimasi probabilitas bersifat indikatif, "
    "bukan nasihat investasi. Selalu verifikasi keputusan kebijakan resmi di federalreserve.gov."
)
