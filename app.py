import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IDX Stochastic Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

/* Root theme */
:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --accent: #00e5a0;
    --accent2: #f97316;
    --accent3: #6366f1;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --border: #1e293b;
    --danger: #ef4444;
    --success: #10b981;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,229,160,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 40% 30% at 90% 10%, rgba(99,102,241,0.06) 0%, transparent 60%);
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem; max-width: 1400px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--accent);
    border: 1px solid rgba(0,229,160,0.3);
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    background: rgba(0,229,160,0.05);
}
.hero-title {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 0%, var(--accent) 60%, var(--accent3) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.8rem;
}
.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: var(--text-muted);
    letter-spacing: 0.05em;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    gap: 1px;
    background: var(--border);
    border-radius: 12px;
    overflow: hidden;
    margin: 1.5rem 0;
}
.stat-item {
    flex: 1;
    background: var(--surface);
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.stat-label {
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Run button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, var(--accent) 0%, #00b87a 100%) !important;
    color: #0a0e1a !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 30px rgba(0,229,160,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 50px rgba(0,229,160,0.4) !important;
}

/* ── Signal card ── */
.signal-card {
    background: var(--surface);
    border: 1px solid rgba(0,229,160,0.2);
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.6rem;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.signal-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(0,229,160,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.signal-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 20px rgba(0,229,160,0.1);
    transform: translateX(4px);
}
.card-ticker {
    font-family: 'Space Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.05em;
}
.card-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: rgba(0,229,160,0.15);
    color: var(--accent);
    border: 1px solid rgba(0,229,160,0.3);
    padding: 2px 8px;
    border-radius: 20px;
    margin-left: 8px;
    vertical-align: middle;
}
.card-values {
    display: flex;
    gap: 1.5rem;
    margin-top: 0.6rem;
}
.val-item { }
.val-label {
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
}
.val-number {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent);
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.4rem; }
.empty-sub { font-size: 0.82rem; font-family: 'Space Mono', monospace; }

/* ── Progress ── */
.stProgress > div > div { background: var(--accent) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Expander / selectbox tweaks ── */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── Sidebar ── */
.css-1d391kg, [data-testid="stSidebar"] {
    background: var(--surface) !important;
}

/* ── Info box ── */
.info-box {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #a5b4fc;
    line-height: 1.6;
}

/* ── Section label ── */
.section-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.8rem;
    font-family: 'Space Mono', monospace;
}

/* ── Scrollable results container ── */
.results-scroll {
    max-height: 600px;
    overflow-y: auto;
    padding-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Ticker Universe ────────────────────────────────────────────────────────────
IDX_TICKERS = [
    # Banks & Finance
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","BRIS.JK","BTPS.JK","BJTM.JK",
    "BNGA.JK","BDMN.JK","BNII.JK","MEGA.JK","PNBN.JK","NISP.JK","BBKP.JK",
    # Telco & Tech
    "TLKM.JK","EXCL.JK","ISAT.JK","GOTO.JK","BUKA.JK","EMTK.JK","MTEL.JK",
    # Consumer & Retail
    "UNVR.JK","ICBP.JK","INDF.JK","MYOR.JK","KLBF.JK","SIDO.JK","ULTJ.JK",
    "HMSP.JK","GGRM.JK","CPIN.JK","JPFA.JK","MAIN.JK","ACES.JK","MAPI.JK",
    "RALS.JK","LPPF.JK","ERAA.JK",
    # Energy & Mining
    "ADRO.JK","PTBA.JK","ITMG.JK","HRUM.JK","BYAN.JK","DSSA.JK","INCO.JK",
    "ANTM.JK","MDKA.JK","TINS.JK","MEDC.JK","ENRG.JK","PGAS.JK",
    # Property & Construction
    "BSDE.JK","SMRA.JK","CTRA.JK","PWON.JK","LPKR.JK","WIKA.JK","PTPP.JK",
    "WSKT.JK","ADHI.JK",
    # Industrial & Transport
    "ASII.JK","AALI.JK","LSIP.JK","SIMP.JK","UNTR.JK","SMGR.JK","INTP.JK",
    "JSMR.JK","GIAA.JK","BIRD.JK","MIKA.JK","HEAL.JK","SILO.JK",
    # Media & Others
    "SCMA.JK","MNCN.JK","LINK.JK","TBIG.JK","TOWR.JK",
    # Misc
    "AKRA.JK","INDF.JK","JPFA.JK","MAIN.JK","ACES.JK","MAPI.JK","BIPI.JK","TPIA.JK","DATA.JK","INET.JK","WIFI.JK",
]

# ── Core Logic ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(ticker: str):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 20:
            return None
        # Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None


def compute_stochastic(df: pd.DataFrame, k_period=14, d_period=3):
    low_min  = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    denom = (high_max - low_min).replace(0, np.nan)
    k = 100 * ((df["Close"] - low_min) / denom)
    d = k.rolling(d_period).mean()
    return k, d


def compute_ema(df: pd.DataFrame, period=50):
    return df["Close"].ewm(span=period, adjust=False).mean()


def check_signal(ticker: str):
    df = fetch_data(ticker)
    if df is None:
        return None

    k, d = compute_stochastic(df)
    ema50 = compute_ema(df, period=50)

    if k.isna().iloc[-1] or d.isna().iloc[-1] or ema50.isna().iloc[-1]:
        return None

    last_close = float(df["Close"].iloc[-1])
    last_ema   = float(ema50.iloc[-1])

    # Golden cross in oversold territory AND price above EMA50 (uptrend filter)
    crossover    = (k.iloc[-2] < d.iloc[-2]) and (k.iloc[-1] > d.iloc[-1])
    oversold     = k.iloc[-1] < 20
    above_trend  = last_close > last_ema

    if crossover and oversold and above_trend:
        return {
            "ticker":  ticker,
            "%K":      round(float(k.iloc[-1]), 2),
            "%D":      round(float(d.iloc[-1]), 2),
            "ema50":   round(last_ema, 2),
            "close":   round(last_close, 2),
            "signal":  "Golden Cross ✦ Oversold ✦ Above EMA50",
            "df":      df,
            "k":       k,
            "d":       d,
            "ema50_series": ema50,
        }
    return None


# ── Chart ─────────────────────────────────────────────────────────────────────
def build_chart(result: dict) -> go.Figure:
    df = result["df"]
    k  = result["k"]
    d  = result["d"]
    ticker = result["ticker"]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.03,
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],   close=df["Close"],
        increasing_line_color="#00e5a0",
        decreasing_line_color="#ef4444",
        increasing_fillcolor="rgba(0,229,160,0.7)",
        decreasing_fillcolor="rgba(239,68,68,0.7)",
        name="Price",
        showlegend=False,
    ), row=1, col=1)

    # EMA 50
    ema50 = result["ema50_series"]
    fig.add_trace(go.Scatter(
        x=ema50.index, y=ema50.values,
        mode="lines",
        line=dict(color="#6366f1", width=1.8, dash="dot"),
        name="EMA 50",
    ), row=1, col=1)

    # Stochastic %K
    fig.add_trace(go.Scatter(
        x=k.index, y=k.values,
        mode="lines",
        line=dict(color="#00e5a0", width=1.8),
        name="%K",
    ), row=2, col=1)

    # Stochastic %D
    fig.add_trace(go.Scatter(
        x=d.index, y=d.values,
        mode="lines",
        line=dict(color="#f97316", width=1.8, dash="dot"),
        name="%D",
    ), row=2, col=1)

    # Oversold / overbought zones
    for level, color in [(20, "rgba(0,229,160,0.08)"), (80, "rgba(239,68,68,0.08)")]:
        fig.add_hline(y=level, line_dash="dash", line_color="rgba(255,255,255,0.15)",
                      line_width=1, row=2, col=1)

    # Crossover marker on latest bar
    fig.add_trace(go.Scatter(
        x=[k.index[-1]], y=[k.iloc[-1]],
        mode="markers",
        marker=dict(size=10, color="#00e5a0", symbol="star",
                    line=dict(color="#fff", width=1.5)),
        name="Signal",
        showlegend=False,
    ), row=2, col=1)

    # Layout
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="Space Mono, monospace", color="#94a3b8", size=11),
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text=f"<b>{ticker}</b>  ·  Stochastic Golden Cross",
            font=dict(color="#e2e8f0", size=14, family="Syne, sans-serif"),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=10),
        ),
        xaxis_rangeslider_visible=False,
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=10)),
        yaxis2=dict(
            range=[-5, 105],
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(size=10),
            tickvals=[0, 20, 50, 80, 100],
        ),
        height=520,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)", showgrid=True)
    return fig


# ── Helpers ───────────────────────────────────────────────────────────────────
def render_hero():
    st.markdown("""
    <div class="hero">
        <div class="hero-tag">IDX · Bursa Efek Indonesia</div>
        <div class="hero-title">Stochastic<br>Golden Cross</div>
        <div class="hero-sub">Screener · Daily Close · Yahoo Finance</div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_card(r, idx):
    k_val = r["%K"]
    d_val = r["%D"]
    ema_val = r["ema50"]
    close_val = r["close"]
    depth = max(0, min(100, (20 - k_val) / 20 * 100))
    ema_gap = round((close_val - ema_val) / ema_val * 100, 1)
    st.markdown(f"""
    <div class="signal-card">
        <div>
            <span class="card-ticker">{r["ticker"].replace(".JK","")}</span>
            <span class="card-badge">⚡ Signal</span>
        </div>
        <div class="card-values">
            <div class="val-item">
                <div class="val-label">%K (Fast)</div>
                <div class="val-number">{k_val}</div>
            </div>
            <div class="val-item">
                <div class="val-label">%D (Slow)</div>
                <div class="val-number">{d_val}</div>
            </div>
            <div class="val-item">
                <div class="val-label">Oversold Depth</div>
                <div class="val-number">{depth:.0f}%</div>
            </div>
            <div class="val-item">
                <div class="val-label">vs EMA50</div>
                <div class="val-number" style="color:#6366f1">+{ema_gap}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    render_hero()

    # ── Controls row
    col_btn, col_upload = st.columns([2, 1])

    with col_upload:
        uploaded = st.file_uploader(
            "Upload ticker list (.txt, one per line)",
            type=["txt"],
            label_visibility="collapsed",
        )

    with col_btn:
        run = st.button("⚡  Run Screener", use_container_width=True)

    # Determine ticker list
    universe = IDX_TICKERS[:]
    if uploaded:
        content = uploaded.read().decode("utf-8")
        custom  = [t.strip().upper() for t in content.splitlines() if t.strip()]
        universe = custom
        st.markdown(f'<div class="info-box">📂 Using uploaded list → {len(universe)} tickers</div>',
                    unsafe_allow_html=True)

    # ── Stats bar
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">{len(universe)}</div>
            <div class="stat-label">Stocks Watched</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">14 / 3</div>
            <div class="stat-label">K / D Period</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">&lt; 20</div>
            <div class="stat-label">Oversold Zone</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">EMA 50</div>
            <div class="stat-label">Trend Filter</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{datetime.now().strftime("%d %b")}</div>
            <div class="stat-label">As Of Date</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Info box
    st.markdown("""
    <div class="info-box">
        SIGNAL  →  %K crosses above %D  &  %K &lt; 20 (oversold)  &  Close &gt; EMA(50) (uptrend)<br>
        DATA    →  Daily close · 3-month lookback · Yahoo Finance (cached 1hr)<br>
        LIMIT   →  Screens up to 100 tickers per run to respect rate limits
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Results area
    if run:
        # Limit universe
        tickers_to_scan = universe[:100]

        results  = []
        progress = st.progress(0, text="Initialising…")
        status   = st.empty()

        for i, ticker in enumerate(tickers_to_scan):
            pct  = (i + 1) / len(tickers_to_scan)
            progress.progress(pct, text=f"Scanning {ticker}…")
            status.markdown(f'<span style="font-family:Space Mono;font-size:0.75rem;color:#64748b">'
                            f'{i+1}/{len(tickers_to_scan)} · {ticker}</span>', unsafe_allow_html=True)
            res = check_signal(ticker)
            if res:
                results.append(res)
            time.sleep(0.05)  # gentle rate limiting

        progress.empty()
        status.empty()

        # Store in session
        st.session_state["results"]  = results
        st.session_state["scanned"]  = len(tickers_to_scan)
        st.session_state["selected"] = None

    # ── Display results
    if "results" in st.session_state:
        results  = st.session_state["results"]
        scanned  = st.session_state.get("scanned", 0)
        selected = st.session_state.get("selected", None)

        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            hit_rate = len(results) / scanned * 100 if scanned else 0
            st.markdown(f"""
            <div class="section-label">Scan complete · {scanned} stocks · {hit_rate:.1f}% hit rate</div>
            """, unsafe_allow_html=True)

            if results:
                # Export CSV
                df_export = pd.DataFrame([
                    {"Ticker": r["ticker"], "%K": r["%K"], "%D": r["%D"], "Signal": r["signal"]}
                    for r in results
                ])
                st.download_button(
                    "⬇ Export CSV",
                    df_export.to_csv(index=False).encode(),
                    file_name=f"idx_signals_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
                st.markdown("<br>", unsafe_allow_html=True)

                for i, r in enumerate(results):
                    render_signal_card(r, i)
                    if st.button(f"View Chart →", key=f"btn_{i}", use_container_width=True):
                        st.session_state["selected"] = i
                        selected = i
            else:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <div class="empty-title">No signals found</div>
                    <div class="empty-sub">No stocks meet the golden cross<br>+ oversold criteria today.</div>
                </div>
                """, unsafe_allow_html=True)

        with col_right:
            if selected is not None and selected < len(results):
                r   = results[selected]
                fig = build_chart(r)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # Quick stats below chart
                c1, c2, c3, c4 = st.columns(4)
                df = r["df"]
                last_close = float(df["Close"].iloc[-1])
                prev_close = float(df["Close"].iloc[-2])
                chg = (last_close - prev_close) / prev_close * 100

                c1.metric("Last Close", f"Rp {last_close:,.0f}", f"{chg:+.2f}%")
                c2.metric("%K (Fast)", f"{r['%K']:.2f}", "Oversold" if r["%K"] < 20 else "")
                c3.metric("%D (Slow)", f"{r['%D']:.2f}")
                c4.metric("EMA 50", f"Rp {r['ema50']:,.0f}", "Price above ✓")
            else:
                st.markdown("""
                <div class="empty-state" style="margin-top:4rem">
                    <div class="empty-icon" style="font-size:2rem">👈</div>
                    <div class="empty-title">Select a stock</div>
                    <div class="empty-sub">Click "View Chart" on any<br>signal to see the chart.</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📡</div>
            <div class="empty-title">Ready to scan</div>
            <div class="empty-sub">Press Run Screener to begin.<br>Results update daily.</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
