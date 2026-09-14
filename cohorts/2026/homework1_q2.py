"""
Question 2: [Macro] Indexes YTD (as of 21 August 2026)
Source: cohorts/2026/homework1.md:35-60

Implements hint from homework1.md:52:
  use start_date='2026-01-01' and end_date='2026-08-21' with yfinance

Calculates YTD return as Close_last / Close_first -1 per ticker.
Answers: how many of 10 indexes outperform US (^GSPC).

Additional: 3/5/10 year comparison.
"""

import yfinance as yf
import pandas as pd

TICKERS = {
    "US S&P500": "^GSPC",
    "China Shanghai": "000001.SS",
    "Hong Kong HSI": "^HSI",
    "Australia ASX200": "^AXJO",
    "India Nifty": "^NSEI",
    "Canada TSX": "^GSPTSE",
    "Germany DAX": "^GDAXI",
    "UK FTSE": "^FTSE",
    "Japan Nikkei": "^N225",
    "Mexico IPC": "^MXX",
    "Brazil Ibovespa": "^BVSP",
}

START = "2026-01-01"
END = "2026-08-21"  # inclusive as per question; yfinance end is exclusive so we add 1 day
END_EXCL = (pd.Timestamp(END) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")


def fetch_ytd(start=START, end_excl=END_EXCL):
    """Download closes and compute YTD. Returns dict name->ret and details."""
    df = yf.download(list(TICKERS.values()), start=start, end=end_excl, progress=False, auto_adjust=False)
    if df.empty:
        raise RuntimeError("Empty download - check network/tickers")
    # yfinance returns MultiIndex columns (Price, Ticker) when auto_adjust=False
    close = df["Close"] if "Close" in df.columns.get_level_values(0) else df
    details = {}
    for name, ticker in TICKERS.items():
        s = close[ticker].dropna()
        if s.empty:
            continue
        # First available >= start, last available <= END
        s_filt = s[(s.index >= start) & (s.index <= END)]
        if len(s_filt) < 2:
            s_filt = s
        first_date, first = s_filt.index[0], float(s_filt.iloc[0])
        last_date, last = s_filt.index[-1], float(s_filt.iloc[-1])
        ret = last / first - 1
        details[name] = {
            "ticker": ticker,
            "first_date": first_date.date(),
            "first_close": first,
            "last_date": last_date.date(),
            "last_close": last,
            "ret": ret,
        }
    return details


def print_ytd(details):
    sorted_names = sorted(details, key=lambda n: details[n]["ret"], reverse=True)
    print(f"\nYTD {START} to {END} (Close-to-Close):")
    print(f"{'Index':20} {'Ticker':10} {'First':12} {'Last':12} {'Return':>8}")
    print("-" * 72)
    for n in sorted_names:
        d = details[n]
        print(f"{n:20} {d['ticker']:10} {d['first_close']:8.2f} {d['last_close']:8.2f} {d['ret']*100:7.2f}%  ({d['first_date']} -> {d['last_date']})")
    us_ret = details["US S&P500"]["ret"]
    better = [n for n, d in details.items() if n != "US S&P500" and d["ret"] > us_ret]
    print(f"\nUS S&P500 YTD: {us_ret*100:.2f}%")
    print(f"Indexes better than US: {len(better)} / 9 others (10 total) -> {', '.join(better) if better else 'none'}")
    # Sensitivity check: literal hint end exclusive (2026-08-21 exclusive means last is 2026-08-20)
    print(f"\nAnswer Q2: {len(better)} indexes outperform US YTD as of {END}")
    return better, us_ret


def calc_period(start, end):
    end_excl = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    df = yf.download(list(TICKERS.values()), start=start, end=end_excl, progress=False, auto_adjust=False)
    close = df["Close"] if "Close" in df.columns.get_level_values(0) else df
    rets = {}
    for name, ticker in TICKERS.items():
        s = close[ticker].dropna()
        s_filt = s[(s.index >= start) & (s.index <= end)]
        if len(s_filt) < 2:
            s_filt = s
        rets[name] = float(s_filt.iloc[-1]) / float(s_filt.iloc[0]) - 1
    return rets


def additional():
    periods = {
        "3Y": ("2023-08-21", "2026-08-21"),
        "5Y": ("2021-08-21", "2026-08-21"),
        "10Y": ("2016-08-21", "2026-08-21"),
    }
    print("\n--- Additional: 3/5/10 year returns vs US (Close-to-Close, ignore FX) ---")
    for label, (s, e) in periods.items():
        rets = calc_period(s, e)
        us = rets["US S&P500"]
        better = [n for n, r in rets.items() if n != "US S&P500" and r > us]
        sorted_rets = sorted(rets.items(), key=lambda x: x[1], reverse=True)
        print(f"\n{label} ({s} to {e})  US {us*100:.2f}%  Better: {len(better)}/9 {better}")
        for n, r in sorted_rets:
            mark = "*" if n in better else " "
            print(f"  {mark} {n:20} {r*100:7.2f}%")


def main():
    details = fetch_ytd()
    print_ytd(details)

    # Show sensitivity to literal hint end
    print("\n--- Sensitivity (if using end='2026-08-21' exclusive -> last 2026-08-20) ---")
    df_hint = yf.download(list(TICKERS.values()), start=START, end=END, progress=False, auto_adjust=False)
    close_hint = df_hint["Close"] if "Close" in df_hint.columns.get_level_values(0) else df_hint
    hint_rets = {}
    for name, ticker in TICKERS.items():
        s = close_hint[ticker].dropna()
        hint_rets[name] = float(s.iloc[-1]) / float(s.iloc[0]) - 1
    us_hint = hint_rets["US S&P500"]
    better_hint = [n for n, r in hint_rets.items() if n != "US S&P500" and r > us_hint]
    print(f"US {us_hint*100:.2f}% Better {len(better_hint)}: {better_hint}")

    additional()


if __name__ == "__main__":
    main()
