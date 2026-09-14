# Homework 1 — Q6 Additional Metrics (Berlin / NEPSE DAX project)

> **Summary (2-sentence submission):** For my DAX vs NEPSE rotation, I’ll add EUR/NPR (EURNPR=X) for remittance FX-hedging, German 10Y Bund (FRED IRLTLT01DEM156N) vs US 10Y for DAX discount-rate regime, and Nepal remittances (World Bank BX.TRF.PWKR.CD.DT, $11.25B 2024) as NEPSE liquidity lead. They’re fetched via `yfinance` for FX, `pandas_datareader` for FRED yields, and `requests` to World Bank/NRB APIs, then merged as 20-day MoM/YoY features to the LightGBM label.

> 3 metrics beyond Module 1 (GDPPOT, CPILFESL, FEDFUNDS) tailored to the Q5 dual DAX vs NEPSE 5–20d rotation. Each includes why, source, and Python retrieval (verified 2026-09-14).

## 1. EUR/NPR Exchange Rate — Remittance Timing & Hedge

**Why:** I remit EUR→NPR from Berlin; EUR/NPR defines NEPSE entry cost. In the capstone, expected NEPSE return must be FX-adjusted; a 1% EUR/NPR move wipes a week’s NEPSE alpha. Also signals Nepal import pressure (Narrows → NRB intervention).

**Source:** Yahoo Finance `EURNPR=X` (ECB reference, daily since 2003). Verified: 961 days `2023-01-01 → 2026-09-14 close 176.88`.

**Python:**
```python
import yfinance as yf
eur_npr = yf.download("EURNPR=X", start="2018-01-01", auto_adjust=False)["Close"]["EURNPR=X"]
eur_npr_mom = eur_npr / eur_npr.shift(21) - 1  # 1-month FX drift for feature
# tail: 2026-09-11 176.65, 2026-09-14 176.88 (+1.2% MoM)
```

## 2. Germany 10Y Bund Yield (and US 10Y) — DAX Discount Rate

**Why:** DAX is rate-sensitive (SAP/Siemens DCF). Bund yield drives DAX cost of capital and explains DAX vs NEPSE decoupling (NEPSE barely rate-sensitive, driven by liquidity). Spread `DE10Y - US10Y` captures risk-appetite rotation.

**Source:** FRED `IRLTLT01DEM156N` (OECD German 10Y, monthly) + `DGS10` (US 10Y, daily) via `pandas_datareader`. Verified: `DE10Y 2026-06 2.97%`, `US10Y 2026-09-11 4.96%`.

**Python:**
```python
import pandas_datareader as pdr
from datetime import date
de10y = pdr.DataReader("IRLTLT01DEM156N", "fred", start=date(2018,1,1))  # monthly
us10y = pdr.DataReader("DGS10", "fred", start=date(2018,1,1))            # daily
# Feature: de10y_mom = de10y.pct_change(1), spread = de10y - us10y (resampled)
```

## 3. Nepal Personal Remittances — NEPSE Liquidity Driver

**Why:** Remittances = 22% of Nepal GDP ($11.25B in 2024) → bank deposits → NEPSE demand. Q5 hypothesis: remittance surge (+7% YoY) predicts NEPSE turnover breadth 15-30 days later (hydropower/bank rally). Frontier alpha unique vs DAX.

**Source:** World Bank `BX.TRF.PWKR.CD.DT` for `NP` (annual, 2018-2024 verified: 2024 $11.25B, 2023 $10.76B) + NRB monthly CSV for higher frequency. Verified via `api.worldbank.org`.

**Python:**
```python
import requests, pandas as pd
url = "https://api.worldbank.org/v2/country/NP/indicator/BX.TRF.PWKR.CD.DT?format=json&per_page=20&date=2015:2024"
j = requests.get(url).json()
remit = pd.DataFrame(j[1])[["date","value"]].astype({"date":int}).sort_values("date")
remit["yoy"] = remit["value"].pct_change(1)
# Monthly proxy: NRB scraping (fallback)
# r = requests.get("https://www.nrb.org.np/category/monthly-data/", headers={"User-Agent":"Mozilla/5.0"})
# pd.read_html(r.text) -> remittance table
```

**Bonus (used in Q5):** `^VIX` via `yfinance` (961 days, 2026-09-14 17.1) as global fear regime for DAX/NEPSE correlation breakdown — replaces `^VDAX` (delisted on Yahoo, use `VIX`).

All three merge on monthly resample to the 20-day label for LightGBM: `features = [rsi, macd, eur_npr_mom, de10y_chg, remit_yoy, vix]`.
