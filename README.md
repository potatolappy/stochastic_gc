# IDX Stochastic Golden Cross Screener

A lightweight, mobile-friendly web app that screens Indonesian stocks (IDX) for **Stochastic Golden Cross** signals in oversold territory.

## What it does

Scans up to 100 IDX stocks and flags any where:
- `%K` crosses **above** `%D` (golden crossover)
- `%K` is **below 20** (oversold zone)

Built with Streamlit + yfinance + Plotly.

---

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud (Free)

1. Push this folder to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file path** → `app.py`
5. Click **Deploy** — done!

---

## Deploy to Hugging Face Spaces (Alternative)

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose **Streamlit** as the SDK
3. Upload `app.py` and `requirements.txt`
4. The Space will auto-build and launch

---

## Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `k_period` | 14 | Lookback window for %K |
| `d_period` | 3  | Smoothing window for %D |
| Oversold   | < 20 | Zone considered oversold |
| Data cache | 1 hr | Results cached per session |

---

## Custom Ticker List

Upload a `.txt` file (one ticker per line, Yahoo Finance format) via the UI:

```
BBCA.JK
TLKM.JK
GOTO.JK
```

---

## Limitations

- Daily close data only (not real-time)
- Yahoo Finance rate limits: max ~100 tickers per run
- Data accuracy subject to Yahoo Finance availability

---

## Possible Enhancements

- Add RSI or EMA trend filter
- Telegram/email alerts
- Historical signal tracking
- Watchlist persistence
