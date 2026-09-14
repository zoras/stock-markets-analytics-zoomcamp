# Homework 1 — Q5 Capstone Proposal (Berlin / NEPSE)

> **Summary (2-sentence submission):** I want to build a dual-market 5–20 day prediction and rotation model for Germany’s DAX 40 vs Nepal’s NEPSE Top-15 (hydropower/banks), forecasting return terciles to overweight the stronger market hedged for EUR/NPR for remittance timing from Berlin. I’ll use RSI/MACD/Bollinger/volatility/illiquidity plus Nepal remittance, monsoon/hydro seasonality, ZEW and FinBERT news sentiment, trained as LightGBM with a 20-day cost-aware backtest (2018-26 split).

**Author context:** Live in Berlin, Germany; origin Nepal — interested in bridging developed (DAX) and frontier (NEPSE) markets.

> Paste-ready for https://courses.datatalks.club/sma-zoomcamp-2026/homework/hw01

## Proposal: Dual-Market 5-20 Day Prediction & Rotation — NEPSE vs DAX

### Asset / Markets
- **Germany — DAX 40** (`^GDAXI` via `yfinance`) + 10 largest DAX stocks (SAP, Siemens, Allianz, etc.)
- **Nepal — NEPSE Index** and Top-15 stocks by turnover (NABIL, NTC, HIDCL, etc. via `nepse-api` / scraper `merolagani` / `nepalstock.com.np` — NEPSE has no Yahoo ticker, requires web-scrape `nepsealpha.com`). Focus on **Hydropower + Commercial Banks** (60%+ of NEPSE cap) where seasonality is strong.

### Prediction Task
For each market, predict **5-day forward direction and 20-day return tercile** (down/flat/up) for the index and for individual Top-10 stocks. Then a simple rotation: overweight the market with higher expected risk-adjusted return, hedged for `EUR/NPR` (forex via `yfinance EUR=X` + NRB rates).

### Features (from Module 1-2 patterns)
- **Technical (per stock/index):** RSI(14), MACD(12,26,9), Bollinger(20,2), 20/50 MA crossover, 20-day realized volatility, Amihud illiquidity (crucial for NEPSE thin trading)
- **Market-structure:** NEPSE turnover breadth, DAX put/call ratio
- **Macro / cross-market:** `EUR/NPR`, Nepal remittance inflows (monthly from NRB, FRED), DAX: ZEW Sentiment + EUR/USD, US 10Y, Brent; Nepal: hydropower generation seasonality (NEA) + monsoon index
- **News sentiment:** Nepali + German financial headlines → FinBERT score (lagged 1d)

### Model & Validation
Baseline Logistic Regression + LightGBM classifier (tercile), time-series split (2018-2023 train, 2024 val, 2025-26 test to avoid NEPSE 2021 bubble leakage). Evaluate with hit-rate, PR-AUC, and Module 4 backtest: 20-day rebalance, 0.3% NEPSE / 0.05% DAX costs, max 40% per market.

### Why This
Tests if frontier seasonality/liquidity signals are exploitable vs DAX efficiency; gives practical remittance-timing overlay (when NEPSE expected drawdown > DAX, defer NPR conversion). Stretch goal: deployment as daily Telegram alert from Berlin (Module 5).

### Data Retrieval (Python)
`yfinance` for DAX/EUR, `requests + BeautifulSoup` for NEPSE, `pandas_datareader` for FRED/NRB CSVs — all patterns from `01-intro-and-data-sources/[2026]_Module_01_Colab_Introduction_and_Data_Sources.ipynb`.
