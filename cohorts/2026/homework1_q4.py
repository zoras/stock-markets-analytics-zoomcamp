"""
Question 4: [Stocks] Earnings Surprise Analysis for Amazon (AMZN)
Source: cohorts/2026/homework1.md:97-125

Steps per homework:
1. get_earnings_dates() -> 25 entries starting 2020-10-29 (1 future NaN)
2. Download historical price data
3. 2-day returns: Close_Day3 / Close_Day1 -1 for 3 consecutive trading days, Day2 ~ earnings
4. Median for positive surprises + correlation surprise vs return via pd.corr()
"""

import yfinance as yf
import pandas as pd

TICKER = "AMZN"


def fetch_earnings(limit=25):
    obj = yf.Ticker(TICKER)
    df = obj.get_earnings_dates(limit=limit)
    # yfinance now returns 100 by default; limit ensures 25 as per homework description: 2020-10-29 onward + 1 future
    # Ensure sorted newest first then take head 25 if needed
    if len(df) > limit:
        df = df.head(limit)
    return df


def fetch_prices(start="2019-01-01"):
    # Complete history needed for 2-day windows around earnings from 2020 onward
    df = yf.download(TICKER, start=start, progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        close = df["Close"][TICKER] if TICKER in df["Close"].columns else df["Close"].iloc[:, 0]
    else:
        close = df["Close"]
    close = close.dropna()
    return close


def compute_2d_returns(close):
    # close: Series with DatetimeIndex (trading days)
    tmp = pd.DataFrame({"Close": close})
    tmp["Close_Day1"] = tmp["Close"].shift(1)
    tmp["Close_Day3"] = tmp["Close"].shift(-1)
    tmp["2d_ret"] = tmp["Close_Day3"] / tmp["Close_Day1"] - 1
    # Day2_date normalized to midnight for merging
    tmp["Day2_date"] = pd.to_datetime(tmp.index.normalize())
    return tmp


def main():
    earn = fetch_earnings(limit=25)
    print(f"Earnings rows: {len(earn)} from {earn.index.min().date()} to {earn.index.max().date()}")
    print(earn.to_string())
    print(f"\nColumns: {list(earn.columns)}")
    print(f"Future NaN count (Reported EPS): {earn['Reported EPS'].isna().sum()}")

    close = fetch_prices()
    print(f"\nPrice rows: {len(close)} from {close.index.min().date()} to {close.index.max().date()}")

    ret_df = compute_2d_returns(close)
    # Build Day2_date -> 2d_ret map
    ret_by_day2 = dict(zip(ret_df["Day2_date"], ret_df["2d_ret"]))

    # Merge each earnings date to 2d_ret
    records = []
    for idx, row in earn.iterrows():
        earn_date_only = pd.Timestamp(idx.date()).normalize()
        # Exact Day2 match
        ret = ret_by_day2.get(earn_date_only, float("nan"))
        matched = earn_date_only if pd.notna(ret) else None
        # If earnings on non-trading day (weekend/holiday), use next trading day
        if pd.isna(ret):
            candidates = [d for d in ret_by_day2.keys() if d >= earn_date_only]
            if candidates:
                nxt = min(candidates)
                ret = ret_by_day2[nxt]
                matched = nxt
        records.append(
            {
                "earn_date": earn_date_only.date(),
                "matched_day2": matched.date() if matched is not None else None,
                "surprise": row["Surprise(%)"],
                "ret_2d": ret,
                "reported": row["Reported EPS"],
                "estimate": row["EPS Estimate"],
            }
        )

    res = pd.DataFrame(records)
    print("\n--- Earnings + 2d returns ---")
    print(res.to_string(index=False))

    # Filter positive surprises (>0) and valid ret
    positive = res[(res["surprise"] > 0) & res["surprise"].notna() & res["ret_2d"].notna()].copy()
    print(f"\nPositive surprises: {len(positive)} / {len(res)} (excluding future and negatives)")

    median_ret = positive["ret_2d"].median()
    print(f"Median 2-day return (positive surprises): {median_ret*100:.4f}% ({median_ret:.6f})")

    # Correlation via pd.corr() as hint
    corr_matrix = positive[["surprise", "ret_2d"]].corr()
    print("\nCorrelation (positive surprises) via pd.corr():")
    print(corr_matrix.to_string())
    corr_val = corr_matrix.loc["surprise", "ret_2d"]
    print(f"\nCorrelation surprise vs 2d_ret (positive): {corr_val:.4f}")

    # Also all valid (including negatives) for reference
    all_valid = res[res["surprise"].notna() & res["ret_2d"].notna()]
    corr_all = all_valid[["surprise", "ret_2d"]].corr().loc["surprise", "ret_2d"]
    print(f"Correlation all valid (incl. negatives, n={len(all_valid)}): {corr_all:.4f}")

    # Answer summary
    print(f"\nAnswer Q4: Median 2-day % change after positive surprise = {median_ret*100:.2f}% (median {median_ret:.4f})")
    print(f"Correlation (positive) = {corr_val:.3f} (all valid = {corr_all:.3f})")

    # Details sorted
    print("\nPositive surprises sorted by surprise:")
    print(positive.sort_values("surprise", ascending=False).to_string(index=False))

    # Additional: check distribution
    print(f"\nPositive ret stats:")
    print(positive["ret_2d"].describe().to_string())


if __name__ == "__main__":
    main()
