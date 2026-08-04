import datetime as dt
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from modules import ai_analysis, data, fed_wire, news
from modules.gauge import render_hawk_dove_gauge
from modules import styling
from modules.styling import hex_to_rgba

load_dotenv()

st.set_page_config(
    page_title="Market Pulse",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_saved_key(name: str) -> str:
    """
    Look for an API key first in st.secrets (Streamlit Cloud), then in
    environment variables (.env locally). Returns "" if not found, so the
    caller can fall back to a manual sidebar input.
    """
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, "")


# -------------------------------------------------------------------------
# SIDEBAR (theme picker first, so inject_css runs before any other markup)
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<p style='font-family:Fraunces,serif; font-size:1.3rem; color:#F3EEDF; margin-bottom:0;'>Market Pulse</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#9C9478; font-size:0.8rem; margin-top:0;'>Economic & financial markets dashboard</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.08em; color:#B9975B;'>Tampilan</p>",
        unsafe_allow_html=True,
    )
    theme_key = st.selectbox(
        "Tema Warna",
        options=list(styling.THEMES.keys()),
        format_func=lambda k: styling.THEMES[k]["display_name"],
        label_visibility="collapsed",
    )

theme = styling.inject_css(theme_key)

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

    /* 3. Warnai tombol sidebar bawaan Streamlit biar kelihatan jelas */
    [data-testid="stHeader"] button {
        color: #F3EEDF !important;
    }
    [data-testid="stHeader"] button:hover {
        color: #B9975B !important;
    }
</style>
""")

with st.sidebar:
    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.08em; color:#B9975B;'>API Keys</p>",
        unsafe_allow_html=True,
    )
    saved_finnhub_key = get_saved_key("FINNHUB_API_KEY")
    saved_groq_key = get_saved_key("GROQ_API_KEY")

    if saved_finnhub_key:
        finnhub_api_key = saved_finnhub_key
        st.caption("✓ Finnhub API Key dimuat otomatis dari secrets/.env")
    else:
        finnhub_api_key = st.text_input("Finnhub API Key", type="password", placeholder="c...")
        st.caption("Dapatkan gratis di [finnhub.io/register](https://finnhub.io/register) — untuk tab Berita Pasar.")

    if saved_groq_key:
        groq_api_key = saved_groq_key
        st.caption("✓ Groq API Key dimuat otomatis dari secrets/.env")
    else:
        groq_api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        st.caption("Dapatkan gratis di [console.groq.com](https://console.groq.com/keys) — untuk analisis sentimen AI.")

    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-family:IBM Plex Mono,monospace; font-size:0.72rem; text-transform:uppercase; "
        "letter-spacing:0.08em; color:#B9975B;'>Watchlist Personal</p>",
        unsafe_allow_html=True,
    )
    
    # Menyiapkan opsi dari data.py
    available_options = list(data.AVAILABLE_ASSETS.keys())
    default_options = ["Bitcoin", "Emas", "EUR/USD", "S&P 500"]
    
    selected_assets = st.multiselect(
        "Pilih aset yang ingin dipantau di header:",
        options=available_options,
        default=default_options,
        label_visibility="collapsed"
    )

# -------------------------------------------------------------------------
# HERO - multi-asset ticker strip (crypto + forex + stocks), then FOMC rate
# -------------------------------------------------------------------------
today = dt.date.today()
next_meeting = data.get_next_meeting(today)
lower, upper = data.CURRENT_TARGET_RANGE

st.markdown("##### Ringkasan Pasar &middot; Crypto, Forex & Saham")
with st.spinner("Mengambil harga terkini..."):
    snapshot = data.fetch_market_snapshot(selected_assets)

if snapshot:
    ticker_html = "".join(
        f"""
<div class="ticker-item">
    <div class="ticker-symbol">{a['label']}</div>
    <div class="ticker-price">{data.format_price(a['price'], a['category'])}</div>
    <div class="ticker-change {'up' if a['change_pct'] >= 0 else 'down'}">{'+' if a['change_pct'] >= 0 else ''}{a['change_pct']:.2f}%</div>
</div>
"""
        for a in snapshot
    )
    st.markdown(f'<div class="ticker-strip">{ticker_html}</div>', unsafe_allow_html=True)
else:
    st.caption("⚠ Data harga live tidak tersedia saat ini — coba muat ulang halaman.")

hero_col1, hero_col2 = st.columns([2, 1])
with hero_col1:
    days_label = f"{next_meeting.days_away} hari lagi" if next_meeting and next_meeting.days_away > 0 else "Sedang berlangsung / baru saja selesai"
    st.markdown(
        f"""
<div class="ledger-hero">
    <div class="ledger-eyebrow">Federal Reserve &middot; Kebijakan Moneter</div>
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
        <div><div style="color:{theme['info']}; font-weight:600; font-size:1.1rem;">{probs['cut']}%</div><div style="font-size:0.7rem;">CUT</div></div>
        <div><div style="color:#6B6250; font-weight:600; font-size:1.1rem;">{probs['hold']}%</div><div style="font-size:0.7rem;">HOLD</div></div>
        <div><div style="color:{theme['down']}; font-weight:600; font-size:1.1rem;">{probs['hike']}%</div><div style="font-size:0.7rem;">HIKE</div></div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )
    if probs["source"] == "fallback":
        st.caption("⚠ Data futures live tidak tersedia - menampilkan estimasi cadangan.")

st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------------
tab_news, tab_calendar, tab_wire, tab_history, tab_ai, tab_corr = st.tabs(
    ["Berita Pasar", "FOMC & Bank Sentral", "Fed Wire", "Riwayat Suku Bunga", "Analisis Statement", "Korelasi Pasar"]
)

# --- TAB: Berita Pasar (general economic & financial news) --------------
with tab_news:
    st.markdown("#### Berita Ekonomi & Pasar Finansial")
    st.caption(
        "Feed berita terkini dari Finnhub, otomatis ditandai per topik. "
        "Klik 'Analisis Sentimen Pasar' untuk penilaian AI atas mood pasar secara keseluruhan."
    )

    if not finnhub_api_key:
        st.info("Masukkan Finnhub API key di sidebar untuk memuat berita terkini.")
    else:
        if "news_items" not in st.session_state:
            st.session_state["news_items"] = None
        if "news_diag" not in st.session_state:
            st.session_state["news_diag"] = None

        col_refresh, col_filter = st.columns([1, 3])
        with col_refresh:
            if st.button("Muat Ulang Berita"):
                try:
                    with st.spinner("Mengambil berita dari Finnhub..."):
                        items_, diag_ = news.fetch_market_news(finnhub_api_key)
                    st.session_state["news_items"] = items_
                    st.session_state["news_diag"] = diag_
                except ValueError as e:
                    st.error(str(e))

        if st.session_state["news_items"] is None:
            try:
                with st.spinner("Mengambil berita dari Finnhub..."):
                    items_, diag_ = news.fetch_market_news(finnhub_api_key)
                st.session_state["news_items"] = items_
                st.session_state["news_diag"] = diag_
            except ValueError as e:
                st.error(str(e))

        items = st.session_state["news_items"]
        diag = st.session_state["news_diag"]

        if diag is not None:
            with st.expander("Detail sumber data"):
                for cat, count in diag.counts.items():
                    if cat in diag.errors:
                        st.caption(f"⚠ `{cat}`: gagal — {diag.errors[cat]}")
                    else:
                        st.caption(f"✓ `{cat}`: {count} artikel")

        if items:
            with col_filter:
                selected_tag = st.radio(
                    "Filter topik", news.ALL_TAGS, horizontal=True, label_visibility="collapsed"
                )
            filtered = news.filter_by_tag(items, selected_tag)

            if st.button("Analisis Sentimen Pasar", type="primary"):
                if not groq_api_key:
                    st.error("Masukkan Groq API Key di sidebar terlebih dahulu.")
                elif not filtered:
                    st.error("Tidak ada berita pada kategori ini untuk dianalisis.")
                else:
                    try:
                        with st.spinner("Menganalisis mood pasar..."):
                            headlines = [n.headline for n in filtered[:40]]
                            result = ai_analysis.analyze_news_sentiment(headlines, groq_api_key)
                        st.session_state["news_sentiment"] = result
                    except ValueError as e:
                        st.error(str(e))

            if "news_sentiment" in st.session_state:
                result = st.session_state["news_sentiment"]
                col_gauge, col_detail = st.columns([1, 1.3])
                with col_gauge:
                    st.markdown(
                        render_hawk_dove_gauge(
                            result["score"], result["label"],
                            left_label="BEARISH", right_label="BULLISH", theme=theme,
                        ),
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="gauge-caption">Skor Sentimen Pasar</div>', unsafe_allow_html=True)
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
                st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

            st.markdown("##### Feed Berita")
            if not filtered:
                cat_error = diag.errors.get(
                    {"Kripto": "crypto", "Forex": "forex"}.get(selected_tag, ""), None
                ) if diag else None
                if cat_error:
                    st.warning(f"Gagal mengambil berita kategori '{selected_tag}' dari Finnhub: {cat_error}")
                else:
                    st.info(f"Belum ada berita untuk kategori '{selected_tag}' saat ini. Coba 'Muat Ulang Berita' atau pilih kategori lain.")
            for n in filtered:
                tags_html = "".join(f'<span class="news-tag">{t}</span>' for t in n.tags)
                st.markdown(
                    f"""
<div class="news-card">
    <div class="news-meta">{n.source} &middot; {n.datetime.strftime('%d %b %Y, %H:%M')}</div>
    <p class="news-headline"><a href="{n.url}" target="_blank">{n.headline}</a></p>
    <div>{tags_html}</div>
    {f'<p class="news-summary">{n.summary}</p>' if n.summary else ''}
</div>
""",
                    unsafe_allow_html=True,
                )
        elif items is not None:
            st.info("Belum ada berita untuk ditampilkan.")

# --- TAB: FOMC & Bank Sentral (FOMC calendar + CPI + NFP schedules) -----
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
    <div style="margin-left:auto; font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:{theme['accent'] if m.is_next else theme['sidebar_label']};">{status}</div>
</div>
"""
        )
    st.caption("Empat dari delapan rapat (Maret, Juni, September, Desember) disertai Summary of Economic Projections (dot plot).")

    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)

    col_cpi, col_nfp = st.columns(2)
    with col_cpi:
        st.markdown("##### Jadwal Rilis CPI (Inflasi)")
        cpi_schedule = data.get_release_schedule(data.CPI_CALENDAR_2026, today)
        for r in cpi_schedule:
            if r.days_away < -3:
                continue
            css_class = "meeting-row is-next" if r.is_next else "meeting-row"
            status = "→ BERIKUTNYA" if r.is_next else ("selesai" if r.release_date < today else "")
            st.html(
                f"""
<div class="{css_class}">
    <div class="meeting-date">{r.release_date.strftime('%d %b %Y')}</div>
    <div style="font-size:0.75rem; color:{theme['sidebar_label']};">Data {r.reference_month}</div>
    <div style="margin-left:auto; font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:{theme['accent'] if r.is_next else theme['sidebar_label']};">{status}</div>
</div>
"""
            )
        st.caption("Sumber: U.S. Bureau of Labor Statistics.")

    with col_nfp:
        st.markdown("##### Jadwal Rilis NFP (Employment Situation)")
        nfp_schedule = data.get_release_schedule(data.NFP_CALENDAR_2026, today)
        for r in nfp_schedule:
            if r.days_away < -3:
                continue
            css_class = "meeting-row is-next" if r.is_next else "meeting-row"
            status = "→ BERIKUTNYA" if r.is_next else ("selesai" if r.release_date < today else "")
            st.html(
                f"""
<div class="{css_class}">
    <div class="meeting-date">{r.release_date.strftime('%d %b %Y')}</div>
    <div style="font-size:0.75rem; color:{theme['sidebar_label']};">Data {r.reference_month}</div>
    <div style="margin-left:auto; font-family:'IBM Plex Mono',monospace; font-size:0.72rem; color:{theme['accent'] if r.is_next else theme['sidebar_label']};">{status}</div>
</div>
"""
            )
        st.caption("Sumber: U.S. Bureau of Labor Statistics.")

# --- TAB: Fed Wire (official RSS feed + rough keyword lean) -------------
with tab_wire:
    st.markdown("#### Fed Wire &middot; Rilis Resmi federalreserve.gov")
    st.caption(
        "Feed RSS resmi rilis pers Federal Reserve. Tag Hawkish/Dovish di sini murni "
        "hitungan kata kunci sederhana pada judul — bukan model NLP atau analisis "
        "mendalam. Untuk penilaian AI yang sesungguhnya atas teks statement, pakai "
        "tab 'Analisis Statement FOMC'."
    )

    if st.button("Muat Ulang Fed Wire"):
        st.session_state.pop("fed_wire_items", None)

    if "fed_wire_items" not in st.session_state:
        try:
            with st.spinner("Mengambil RSS feed dari federalreserve.gov..."):
                st.session_state["fed_wire_items"] = fed_wire.fetch_fed_press_wire()
        except ValueError as e:
            st.session_state["fed_wire_items"] = None
            st.error(str(e))

    wire_items = st.session_state.get("fed_wire_items")
    if wire_items:
        for w in wire_items:
            time_str = w.published.strftime("%d %b %Y, %H:%M") if w.published else "—"
            st.markdown(
                f"""
<div class="wire-row">
    <p class="wire-title"><a href="{w.link}" target="_blank">{w.title}</a></p>
    <div class="wire-meta">{time_str}</div>
    <span class="wire-lean {w.lean_class}">{w.lean}</span>
</div>
""",
                unsafe_allow_html=True,
            )
    elif wire_items is not None:
        st.info("Belum ada rilis untuk ditampilkan.")

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
            line=dict(color=theme["accent"], width=2.5),
            fill="tozeroy",
            fillcolor=hex_to_rgba(theme["accent"], 0.10),
            name="Effective Fed Funds Rate",
        )
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme["text"], family="Inter"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        xaxis=dict(showgrid=False, title=None),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", title="Rate (%)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Sumber: FRED series DFF (Effective Federal Funds Rate), Federal Reserve Bank of St. Louis.")

    #BACKTEST KITA
    st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
    st.markdown("#### Backtest Akurasi Pasar (Fed Funds Futures)")
    st.caption(
        "Mengevaluasi seberapa akurat tebakan pasar (menggunakan harga penutupan instrumen ZQ=F satu hari sebelum rapat) "
        "dibandingkan dengan keputusan suku bunga aktual yang diambil oleh FOMC."
    )

    if st.button("Jalankan Backtest Historis"):
        with st.spinner("Menarik data historis dari Yahoo Finance dan menghitung akurasi..."):
            bt_df, bt_accuracy = data.run_fomc_backtest()
            
            if not bt_df.empty:
                col_acc, col_space = st.columns([1, 3])
                with col_acc:
                    st.markdown(
                        f"""
                        <div class="parchment-card" style="text-align: center;">
                            <div class="label">Akurasi Historis Pasar</div>
                            <div style="color:{theme['info']}; font-size:2rem; font-weight:700;">
                                {bt_accuracy:.1f}%
                            </div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(
                    bt_df,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.error("Gagal mengambil data historis untuk backtest.")

#TAB: Analisis Statement FOMC 
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
            st.markdown(
                render_hawk_dove_gauge(result["score"], result["label"], theme=theme),
                unsafe_allow_html=True,
            )
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
                line=dict(color=theme["accent"], width=2),
                marker=dict(size=9, color=theme["accent"]),
            )
        )
        fig_hist.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.25)")
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=theme["text"], family="Inter"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=280,
            yaxis=dict(range=[-105, 105], title="Skor", gridcolor="rgba(255,255,255,0.08)"),
            xaxis=dict(title="Urutan analisis dalam sesi ini", dtick=1),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Riwayat ini hanya tersimpan selama sesi browser aktif dan akan hilang saat halaman di-refresh.")

st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
st.caption(
    "Market Pulse adalah proyek edukasi dan portofolio. Data pasar dan estimasi probabilitas bersifat indikatif, "
    "bukan nasihat investasi. Selalu verifikasi keputusan kebijakan resmi di federalreserve.gov."
)

#TAB: Korelasi Pasar 
with tab_corr:
    st.markdown("#### Matriks Korelasi Aset Makro (Heatmap)")
    st.caption(
        "Menganalisis korelasi pergerakan harian (daily returns) antar instrumen utama "
        "selama 6 bulan terakhir. Nilai mendekati +1 berarti bergerak searah (korelasi positif kuat), "
        "sedangkan mendekati -1 berlawanan arah (korelasi negatif)."
    )
    
    with st.spinner("Menghitung matriks korelasi dari Yahoo Finance..."):
        corr_matrix = data.fetch_correlation_data(lookback_days=180)
        
    if not corr_matrix.empty:
        colorscale = [
            [0.0, theme["down"]],     
            [0.5, "rgba(0,0,0,0)"],   
            [1.0, theme["info"]]      
        ]
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale="RdBu", 
            zmid=0, 
            zmin=-1, zmax=1,
            texttemplate="%{z:.2f}",
            hoverinfo="x+y+z",
            showscale=True
        ))
        
        fig_corr.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=theme["text"], family="Inter"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=450,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False, autorange="reversed") 
        )
        
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.error("Gagal mengambil data untuk matriks korelasi.")