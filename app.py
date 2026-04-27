import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IDX Screener",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg:      #07090f;
    --surface: #0e1117;
    --surf2:   #161b24;
    --green:   #3ddc84;
    --orange:  #f0883e;
    --blue:    #58a6ff;
    --red:     #f85149;
    --text:    #e6edf3;
    --muted:   #7d8590;
    --border:  #21262d;
    --gdim:    rgba(61,220,132,0.12);
    --gbdr:    rgba(61,220,132,0.28);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Container — tight on mobile ── */
.block-container {
    padding: 1rem 0.75rem 4rem !important;
    max-width: 680px !important;
}

/* ── Hero ── */
.hero {
    padding: 1.8rem 0 1.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.4rem;
}
.hero-eye {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 0.5rem;
}
.hero-title {
    font-size: clamp(1.75rem, 7vw, 2.8rem);
    font-weight: 700;
    line-height: 1.1;
    color: var(--text);
    margin-bottom: 0.35rem;
}
.hero-title em { color: var(--green); font-style: normal; }
.hero-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ── Stats grid — 2×2 on mobile, 4×1 on wider ── */
.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: var(--border);
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.1rem;
}
@media (min-width: 520px) {
    .stats-grid { grid-template-columns: repeat(4, 1fr); }
}
.stat-cell {
    background: var(--surface);
    padding: 0.8rem 0.6rem;
    text-align: center;
}
.stat-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--green);
    line-height: 1;
}
.stat-lbl {
    font-size: 0.6rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 3px;
}

/* ── Info pill ── */
.info-pill {
    background: rgba(88,166,255,0.07);
    border: 1px solid rgba(88,166,255,0.18);
    border-radius: 7px;
    padding: 0.75rem 0.9rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.67rem;
    color: #8ab4f8;
    line-height: 1.8;
    margin-bottom: 1.1rem;
    word-break: break-word;
}

/* ── Run button ── */
.stButton > button {
    width: 100% !important;
    background: var(--green) !important;
    color: #07090f !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 0.8rem !important;
    transition: opacity 0.15s !important;
    margin-bottom: 0.8rem !important;
}
.stButton > button:hover { opacity: 0.82 !important; }

/* ── Signal card ── */
.sig-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--green);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.45rem;
}
.sig-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 0.55rem;
}
.sig-ticker {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.04em;
}
.badges { display: flex; gap: 4px; flex-wrap: wrap; }
.badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}
.b-green  { background: var(--gdim); color: var(--green); border: 1px solid var(--gbdr); }
.b-orange { background: rgba(240,136,62,0.12); color: var(--orange); border: 1px solid rgba(240,136,62,0.28); }
.b-blue   { background: rgba(88,166,255,0.10); color: var(--blue);   border: 1px solid rgba(88,166,255,0.28); }
.b-red    { background: rgba(248,81,73,0.10);  color: var(--red);    border: 1px solid rgba(248,81,73,0.28); }
.b-muted  { background: rgba(125,133,144,0.10); color: var(--muted); border: 1px solid rgba(125,133,144,0.22); }
.sig-vals {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
}
.sv-lbl {
    font-size: 0.58rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 2px;
}
.sv-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--green);
}
.sv-num-red {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--red);
}
.sv-num-muted {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--muted);
}

/* ── Section label ── */
.sec-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* ── Section header (larger) ── */
.sec-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--blue);
    margin: 1.6rem 0 0.7rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid rgba(88,166,255,0.20);
}

/* ── Chart browser card ── */
.browser-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--blue);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.7rem;
}
.browser-vals {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    margin-top: 0.55rem;
}
.sv-num-blue {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--blue);
}
.sv-num-red {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--red);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--surf2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    border-radius: 6px !important;
    width: 100% !important;
    margin-bottom: 0.7rem !important;
}

/* ── Metric ── */
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.95rem !important;
}
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; }

/* ── Select box ── */
[data-baseweb="select"] {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

/* ── Empty state ── */
.empty {
    text-align: center;
    padding: 3rem 1rem;
    color: var(--muted);
}
.empty-icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
.empty-title { font-size: 0.95rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.empty-sub { font-size: 0.72rem; font-family: 'IBM Plex Mono', monospace; line-height: 1.6; }

/* ── Misc ── */
.stProgress > div > div { background: var(--green) !important; }
hr { border-color: var(--border) !important; margin: 0.9rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Ticker universe (deduped) ─────────────────────────────────────────────────
IDX_TICKERS = list(dict.fromkeys([
    "BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","BRIS.JK","BTPS.JK","BJTM.JK",
    "BNGA.JK","BDMN.JK","BNII.JK","MEGA.JK","PNBN.JK","NISP.JK","BBKP.JK",
    "TLKM.JK","EXCL.JK","ISAT.JK","GOTO.JK","BUKA.JK","EMTK.JK","MTEL.JK",
    "UNVR.JK","ICBP.JK","INDF.JK","MYOR.JK","KLBF.JK","SIDO.JK","ULTJ.JK",
    "HMSP.JK","GGRM.JK","CPIN.JK","JPFA.JK","MAIN.JK","ACES.JK","MAPI.JK",
    "RALS.JK","LPPF.JK","ERAA.JK",
    "ADRO.JK","PTBA.JK","ITMG.JK","HRUM.JK","BYAN.JK","DSSA.JK","INCO.JK",
    "ANTM.JK","MDKA.JK","TINS.JK","MEDC.JK","ENRG.JK","PGAS.JK",
    "BSDE.JK","SMRA.JK","CTRA.JK","PWON.JK","LPKR.JK","WIKA.JK","PTPP.JK",
    "WSKT.JK","ADHI.JK",
    "ASII.JK","AALI.JK","LSIP.JK","SIMP.JK","UNTR.JK","SMGR.JK","INTP.JK",
    "JSMR.JK","GIAA.JK","BIRD.JK","MIKA.JK","HEAL.JK","SILO.JK",
    "SCMA.JK","MNCN.JK","LINK.JK","TBIG.JK","TOWR.JK",
    "AKRA.JK","BIPI.JK","TPIA.JK","DATA.JK","INET.JK","WIFI.JK","PANI.JK",
    "FREN.JK","ARTO.JK","ADMF.JK","APLN.JK","BSSR.JK","BTEK.JK",
    "BNBR.JK","DEWA.JK","BULL.JK","PPRE.JK","SMAA.JK","KIJA.JK",
    "VKTR.JK","ELSA.JK","OILS.JK","BULL.JK","WIIM.JK","BDMN.JK","ISAT.JK","TPIA.JK","TPIA.JK",
    "DKFT.JK","ENRG.JK","BIPI.JK","WIFI.JK","INET.JK","ESSA.JK","MBMA.JK", "AMMN.JK","ANTM.JK","MDKA.JK","EMTK.JK","BRMS.JK",   
]))

# ── Data fetch ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_data(ticker: str):
    try:
        df = yf.download(ticker, period="60d", interval="1d",
                         progress=False, auto_adjust=True)
        if df.empty or len(df) < 30:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

# ── Stochastic Slow ───────────────────────────────────────────────────────────
def compute_stochastic(df, fast_k=10, slow_k=5, slow_d=5):
    lo = df["Low"].rolling(fast_k).min()
    hi = df["High"].rolling(fast_k).max()
    fk = 100 * ((df["Close"] - lo) / (hi - lo).replace(0, np.nan))
    sk = fk.rolling(slow_k).mean()
    sd = sk.rolling(slow_d).mean()
    return sk, sd

# ── Parabolic SAR ─────────────────────────────────────────────────────────────
def compute_psar(df, af0=0.02, af_step=0.02, af_max=0.2):
    hi    = df["High"].values
    lo    = df["Low"].values
    n     = len(lo)
    sar   = np.full(n, np.nan)
    trend = np.ones(n, dtype=int)
    ep    = np.full(n, np.nan)
    af    = np.full(n, af0)

    sar[0]   = lo[0]
    ep[0]    = hi[0]

    for i in range(1, n):
        ps, pe, pa, pt = sar[i-1], ep[i-1], af[i-1], trend[i-1]
        if pt == 1:
            ns = ps + pa * (pe - ps)
            ns = min(ns, lo[i-1], lo[max(0,i-2)])
            if lo[i] < ns:
                trend[i], sar[i], ep[i], af[i] = -1, pe, lo[i], af0
            else:
                trend[i] = 1
                sar[i]   = ns
                if hi[i] > pe:
                    ep[i] = hi[i]; af[i] = min(pa + af_step, af_max)
                else:
                    ep[i] = pe; af[i] = pa
        else:
            ns = ps + pa * (pe - ps)
            ns = max(ns, hi[i-1], hi[max(0,i-2)])
            if hi[i] > ns:
                trend[i], sar[i], ep[i], af[i] = 1, pe, hi[i], af0
            else:
                trend[i] = -1
                sar[i]   = ns
                if lo[i] < pe:
                    ep[i] = lo[i]; af[i] = min(pa + af_step, af_max)
                else:
                    ep[i] = pe; af[i] = pa

    return (pd.Series(sar,   index=df.index),
            pd.Series(trend, index=df.index))

# ── Phase 1: Golden Cross + Oversold only (no PSAR) ──────────────────────────
def check_signal(ticker: str):
    df = fetch_data(ticker)
    if df is None:
        return None

    sk, sd = compute_stochastic(df)

    if sk.isna().iloc[-1] or sd.isna().iloc[-1]:
        return None

    crossover = (sk.iloc[-2] < sd.iloc[-2]) and (sk.iloc[-1] > sd.iloc[-1])
    oversold  = sk.iloc[-1] < 20

    if crossover and oversold:
        close = float(df["Close"].iloc[-1])
        prev  = float(df["Close"].iloc[-2])
        return {
            "ticker":   ticker,
            "%K":       round(float(sk.iloc[-1]), 2),
            "%D":       round(float(sd.iloc[-1]), 2),
            "close":    round(close, 2),
            "chg":      round((close - prev) / prev * 100, 2),
            # PSAR fields filled in phase 2
            "sar":      None,
            "sar_pct":  None,
            "sar_bull": None,
            "sar_s":    None,
            "trend":    None,
            "df":       df,
            "sk":       sk,
            "sd":       sd,
        }
    return None

# ── Phase 2: Enrich result with PSAR ─────────────────────────────────────────
def enrich_with_psar(r: dict) -> dict:
    df = r["df"]
    sar, trend = compute_psar(df)

    if sar.isna().iloc[-1]:
        r["sar_s"] = sar
        r["trend"] = trend
        return r

    sar_val      = float(sar.iloc[-1])
    r["sar"]     = round(sar_val, 2)
    r["sar_pct"] = round((r["close"] - sar_val) / sar_val * 100, 2)
    r["sar_bull"]= int(trend.iloc[-1]) == 1
    r["sar_s"]   = sar
    r["trend"]   = trend
    return r

# ── Get chart data without signal requirement ─────────────────────────────────
def get_chart_data(ticker: str):
    """Fetch and compute indicators for any ticker, no signal filter."""
    df = fetch_data(ticker)
    if df is None:
        return None
    sk, sd     = compute_stochastic(df)
    sar, trend = compute_psar(df)
    close      = float(df["Close"].iloc[-1])
    prev       = float(df["Close"].iloc[-2])
    sar_val    = float(sar.iloc[-1])
    return {
        "ticker":  ticker,
        "%K":      round(float(sk.iloc[-1]), 2),
        "%D":      round(float(sd.iloc[-1]), 2),
        "sar":     round(sar_val, 2),
        "close":   round(close, 2),
        "chg":     round((close - prev) / prev * 100, 2),
        "sar_pct": round((close - sar_val) / sar_val * 100, 2),
        "sar_bull": int(trend.iloc[-1]) == 1,
        "crossover": (sk.iloc[-2] < sd.iloc[-2]) and (sk.iloc[-1] > sd.iloc[-1]),
        "oversold": float(sk.iloc[-1]) < 20,
        "df":      df,
        "sk":      sk,
        "sd":      sd,
        "sar_s":   sar,
        "trend":   trend,
    }

# ── Chart ─────────────────────────────────────────────────────────────────────
def build_chart(r):
    df    = r["df"]
    sk    = r["sk"]
    sd    = r["sd"]
    sar   = r["sar_s"]
    trend = r["trend"]
    name  = r["ticker"].replace(".JK", "")

    bull_sar = sar.where(trend ==  1)
    bear_sar = sar.where(trend == -1)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.60, 0.40], vertical_spacing=0.02)

    # Candles
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#3ddc84", decreasing_line_color="#f85149",
        increasing_fillcolor="rgba(61,220,132,0.75)",
        decreasing_fillcolor="rgba(248,81,73,0.75)",
        name="Price", showlegend=False,
    ), row=1, col=1)

    # PSAR dots
    fig.add_trace(go.Scatter(
        x=bull_sar.index, y=bull_sar.values, mode="markers",
        marker=dict(size=4, color="#3ddc84"), name="PSAR ↑",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=bear_sar.index, y=bear_sar.values, mode="markers",
        marker=dict(size=4, color="#f85149"), name="PSAR ↓",
    ), row=1, col=1)

    # Slow%K / Slow%D
    fig.add_trace(go.Scatter(
        x=sk.index, y=sk.values, mode="lines",
        line=dict(color="#3ddc84", width=1.8), name="Slow%K",
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=sd.index, y=sd.values, mode="lines",
        line=dict(color="#f0883e", width=1.8, dash="dot"), name="Slow%D",
    ), row=2, col=1)

    # Oversold / overbought bands
    fig.add_hrect(y0=0,  y1=20,  fillcolor="rgba(61,220,132,0.06)",  line_width=0, row=2, col=1)
    fig.add_hrect(y0=80, y1=100, fillcolor="rgba(248,81,73,0.06)",   line_width=0, row=2, col=1)
    for lvl in [20, 80]:
        fig.add_hline(y=lvl, line_dash="dash",
                      line_color="rgba(255,255,255,0.1)", line_width=1,
                      row=2, col=1)

    # Signal star if crossover in oversold
    if r.get("crossover") and r.get("oversold"):
        fig.add_trace(go.Scatter(
            x=[sk.index[-1]], y=[sk.iloc[-1]], mode="markers",
            marker=dict(size=11, color="#3ddc84", symbol="star",
                        line=dict(color="#fff", width=1.5)),
            name="Signal", showlegend=False,
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,23,0.9)",
        font=dict(family="IBM Plex Mono, monospace", color="#7d8590", size=10),
        margin=dict(l=0, r=0, t=34, b=0),
        title=dict(text=f"<b>{name}</b> · Stoch Slow + PSAR",
                   font=dict(color="#e6edf3", size=13,
                             family="DM Sans, sans-serif")),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        xaxis_rangeslider_visible=False,
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", tickfont=dict(size=9)),
        yaxis2=dict(range=[-5, 105], gridcolor="rgba(255,255,255,0.04)",
                    tickfont=dict(size=9), tickvals=[0,20,50,80,100]),
        height=440,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)")
    return fig

# ── UI helpers ────────────────────────────────────────────────────────────────
def render_hero(n):
    st.markdown(f"""
    <div class="hero">
        <div class="hero-eye">IDX · Bursa Efek Indonesia</div>
        <div class="hero-title">IDX <em>Screener</em></div>
        <div class="hero-meta">
            Slow Stoch(10/5/5) · Oversold &lt;20 · Parabolic SAR<br>
            60-day daily · {datetime.now().strftime("%d %b %Y")}
        </div>
    </div>
    <div class="stats-grid">
        <div class="stat-cell">
            <div class="stat-num">{n}</div>
            <div class="stat-lbl">Stocks</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">10/5/5</div>
            <div class="stat-lbl">Stoch</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">&lt;20</div>
            <div class="stat-lbl">Oversold</div>
        </div>
        <div class="stat-cell">
            <div class="stat-num">PSAR</div>
            <div class="stat-lbl">Trend</div>
        </div>
    </div>
    <div class="info-pill">
        SIGNAL → Slow%K crosses above Slow%D<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Slow%K &lt; 20 (oversold zone)<br>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Price above Parabolic SAR (bull)<br>
        DATA &nbsp;&nbsp;→ 60-day daily · cached 1 hr
    </div>
    """, unsafe_allow_html=True)


def render_card(r, idx):
    k, d = r["%K"], r["%D"]

    # Border colour based on PSAR state
    if r.get("sar_bull") is True:
        border_color = "#f0883e"   # orange — bullish
    elif r.get("sar_bull") is False:
        border_color = "#f85149"   # red — bearish
    else:
        border_color = "#3ddc84"   # green — pending

    # PSAR badge
    if r.get("sar_bull") is True:
        psar_badge = '<span class="badge b-orange">PSAR ↑</span>'
    elif r.get("sar_bull") is False:
        psar_badge = '<span class="badge b-red">PSAR ↓</span>'
    else:
        psar_badge = '<span class="badge b-muted">PSAR …</span>'

    # vs SAR value
    if r.get("sar_pct") is not None:
        sar_sign = "+" if r["sar_pct"] >= 0 else ""
        sar_display = f"{sar_sign}{r['sar_pct']}%"
        sar_cls = "sv-num" if r["sar_pct"] >= 0 else "sv-num-red"
    else:
        sar_display = "—"
        sar_cls = "sv-num-muted"

    st.markdown(f"""
    <div class="sig-card" style="border-left-color:{border_color}">
        <div class="sig-top">
            <span class="sig-ticker">{r["ticker"].replace(".JK","")}</span>
            <div class="badges">
                <span class="badge b-green">✦ Cross</span>
                <span class="badge b-green">Oversold</span>
                {psar_badge}
            </div>
        </div>
        <div class="sig-vals">
            <div>
                <div class="sv-lbl">Slow%K</div>
                <div class="sv-num">{k}</div>
            </div>
            <div>
                <div class="sv-lbl">Slow%D</div>
                <div class="sv-num">{d}</div>
            </div>
            <div>
                <div class="sv-lbl">Close</div>
                <div class="sv-num">{r["close"]:,}</div>
            </div>
            <div>
                <div class="sv-lbl">vs SAR</div>
                <div class="{sar_cls}">{sar_display}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_browser_card(r):
    """Card for the Chart Browser section — blue accent, shows indicator status."""
    chg_color = "var(--green)" if r["chg"] >= 0 else "var(--red)"
    chg_sign  = "+" if r["chg"] >= 0 else ""
    sar_label = "PSAR ↑" if r["sar_bull"] else "PSAR ↓"
    sar_cls   = "b-orange" if r["sar_bull"] else "b-red"

    badges = f'<span class="badge b-blue">{sar_label}</span>'
    if r["oversold"]:
        badges += ' <span class="badge b-green">Oversold</span>'
    if r["crossover"]:
        badges += ' <span class="badge b-green">✦ Cross</span>'

    num_cls_sar = "sv-num" if r["sar_bull"] else "sv-num-red"

    st.markdown(f"""
    <div class="browser-card">
        <div class="sig-top">
            <span class="sig-ticker">{r["ticker"].replace(".JK","")}</span>
            <div class="badges">{badges}</div>
        </div>
        <div class="browser-vals">
            <div>
                <div class="sv-lbl">Close</div>
                <div class="sv-num-blue">{r["close"]:,}</div>
            </div>
            <div>
                <div class="sv-lbl">Chg%</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.88rem;font-weight:600;color:{chg_color}">
                    {chg_sign}{r["chg"]}%
                </div>
            </div>
            <div>
                <div class="sv-lbl">Slow%K</div>
                <div class="sv-num-blue">{r["%K"]}</div>
            </div>
            <div>
                <div class="sv-lbl">Slow%D</div>
                <div class="sv-num-blue">{r["%D"]}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    universe = IDX_TICKERS[:]
    render_hero(len(universe))

    run = st.button("⚡  Run Screener", use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Scan
    if run:
        to_scan  = universe[:100]
        results  = []
        prog     = st.progress(0, text="Starting…")
        status   = st.empty()

        for i, ticker in enumerate(to_scan):
            prog.progress((i + 1) / len(to_scan), text=f"[Phase 1] Scanning {ticker}…")
            status.markdown(
                f'<span style="font-family:IBM Plex Mono;font-size:0.68rem;'
                f'color:#7d8590">{i+1}/{len(to_scan)} · {ticker}</span>',
                unsafe_allow_html=True,
            )
            res = check_signal(ticker)
            if res:
                results.append(res)
            time.sleep(0.05)

        prog.empty(); status.empty()
        st.session_state.update(results=results, scanned=len(to_scan), selected=None, psar_done=False)

    # ── Show screener results
    if "results" not in st.session_state:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">📡</div>
            <div class="empty-title">Ready to scan</div>
            <div class="empty-sub">Tap Run Screener to begin.<br>Results cached for 1 hour.</div>
        </div>""", unsafe_allow_html=True)
    else:
        results   = st.session_state["results"]
        scanned   = st.session_state.get("scanned", 0)
        selected  = st.session_state.get("selected", None)
        psar_done = st.session_state.get("psar_done", False)

        hit = len(results) / scanned * 100 if scanned else 0
        st.markdown(
            f'<div class="sec-lbl">{scanned} scanned · {len(results)} golden crosses · {hit:.1f}% hit rate</div>',
            unsafe_allow_html=True,
        )

        if not results:
            st.markdown("""
            <div class="empty">
                <div class="empty-icon">🔍</div>
                <div class="empty-title">No golden crosses today</div>
                <div class="empty-sub">No stocks had Slow%K cross above Slow%D in oversold zone.<br>Try again after market close.</div>
            </div>""", unsafe_allow_html=True)
        else:
            # Phase 2 banner while PSAR is pending
            if not psar_done:
                st.markdown(f"""
                <div style="background:rgba(61,220,132,0.07);border:1px solid rgba(61,220,132,0.20);
                border-radius:7px;padding:0.6rem 0.9rem;font-family:'IBM Plex Mono',monospace;
                font-size:0.67rem;color:#3ddc84;line-height:1.7;margin-bottom:1rem;">
                    <strong style="color:#fff">Phase 1 complete</strong> — {len(results)} stocks with Stochastic Golden Cross in oversold zone.<br>
                    Loading PSAR trend below ↓ — orange border = bullish, red = bearish.
                </div>
                """, unsafe_allow_html=True)

            # CSV export
            df_export = pd.DataFrame([{
                "Ticker": r["ticker"], "Close": r["close"], "Chg%": r["chg"],
                "Slow%K": r["%K"], "Slow%D": r["%D"],
                "PSAR": r.get("sar", "—"), "Above PSAR%": r.get("sar_pct", "—"),
                "PSAR Bull": r.get("sar_bull", "—"),
            } for r in results])
            st.download_button(
                "⬇  Export CSV", df_export.to_csv(index=False).encode(),
                file_name=f"idx_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )

            # ── Phase 2: enrich with PSAR ─────────────────────────────────
            if not psar_done:
                prog2   = st.progress(0, text="Loading PSAR…")
                status2 = st.empty()
                for i, r in enumerate(results):
                    prog2.progress((i + 1) / len(results),
                                   text=f"[Phase 2] PSAR for {r['ticker']}…")
                    status2.markdown(
                        f'<span style="font-family:IBM Plex Mono;font-size:0.68rem;color:#7d8590">'
                        f'PSAR {i+1}/{len(results)} · {r["ticker"]}</span>',
                        unsafe_allow_html=True,
                    )
                    results[i] = enrich_with_psar(r)
                prog2.empty(); status2.empty()
                st.session_state["results"]   = results
                st.session_state["psar_done"] = True
                st.rerun()

            for i, r in enumerate(results):
                render_card(r, i)
                if st.button(f"View chart →  {r['ticker'].replace('.JK','')}", 
                             key=f"btn_{i}", use_container_width=True):
                    st.session_state["selected"] = i if selected != i else None
                    selected = st.session_state["selected"]

                if selected == i:
                    fig = build_chart(r)
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": False})
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Close",  f"Rp {r['close']:,}", f"{r['chg']:+.2f}%")
                    c2.metric("Slow%K", f"{r['%K']:.1f}")
                    c3.metric("Slow%D", f"{r['%D']:.1f}")
                    sar_delta = (f"+{r['sar_pct']}%" if r.get("sar_pct") is not None and r["sar_pct"] >= 0
                                 else f"{r['sar_pct']}%" if r.get("sar_pct") is not None else "—")
                    c4.metric("vs SAR", sar_delta)
                    st.markdown("<hr>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # ── CHART BROWSER ────────────────────────────────────────────────────────
    # ════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="sec-header">📊 Chart Browser</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sec-lbl">Browse any ticker in the universe — no signal filter</div>',
        unsafe_allow_html=True,
    )

    # Ticker selector — clean labels (strip .JK), keep value mapping
    label_to_ticker = {t.replace(".JK", ""): t for t in universe}
    labels = list(label_to_ticker.keys())

    col_sel, col_btn = st.columns([3, 1])
    with col_sel:
        chosen_label = st.selectbox(
            "Select ticker",
            options=labels,
            index=labels.index("ISAT") if "ISAT" in labels else 0,
            label_visibility="collapsed",
        )
    with col_btn:
        load_chart = st.button("Load  →", key="browse_load", use_container_width=True)

    # Also allow multi-select to compare a few tickers at once
    with st.expander("📋  Compare multiple tickers", expanded=False):
        multi_labels = st.multiselect(
            "Pick up to 5 tickers",
            options=labels,
            default=[],
            max_selections=5,
            label_visibility="collapsed",
        )
        load_multi = st.button("Load selected charts", key="browse_multi_load",
                               use_container_width=True)

    # ── Single ticker chart
    if load_chart:
        ticker = label_to_ticker[chosen_label]
        with st.spinner(f"Fetching {ticker}…"):
            r = get_chart_data(ticker)
        if r is None:
            st.error(f"Could not load data for {ticker}. Yahoo Finance may be rate-limiting — try again shortly.")
        else:
            render_browser_card(r)
            fig = build_chart(r)
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Close",  f"Rp {r['close']:,}", f"{r['chg']:+.2f}%")
            c2.metric("Slow%K", f"{r['%K']:.1f}")
            c3.metric("Slow%D", f"{r['%D']:.1f}")
            sar_delta = f"+{r['sar_pct']}%" if r["sar_pct"] >= 0 else f"{r['sar_pct']}%"
            c4.metric("vs SAR", sar_delta)

    # ── Multi-ticker charts
    if load_multi and multi_labels:
        for lbl in multi_labels:
            ticker = label_to_ticker[lbl]
            with st.spinner(f"Fetching {ticker}…"):
                r = get_chart_data(ticker)
            if r is None:
                st.warning(f"No data for {ticker} — skipped.")
                continue
            render_browser_card(r)
            fig = build_chart(r)
            st.plotly_chart(fig, use_container_width=True,
                            config={"displayModeBar": False})
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Close",  f"Rp {r['close']:,}", f"{r['chg']:+.2f}%")
            c2.metric("Slow%K", f"{r['%K']:.1f}")
            c3.metric("Slow%D", f"{r['%D']:.1f}")
            sar_delta = f"+{r['sar_pct']}%" if r["sar_pct"] >= 0 else f"{r['sar_pct']}%"
            c4.metric("vs SAR", sar_delta)
            st.markdown("<hr>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
