"""
Question 3: [Index] S&P 500 Market Corrections Analysis
Source: cohorts/2026/homework1.md:63-94

Steps per homework:
1. Download S&P500 daily 1950-present via yfinance
2. Identify ATH closing price points (cummax)
3. For each consecutive ATH pair, find min between
4. Drawdown = (high-low)/high*100
5. Filter >=5%
6. Duration in days
7. Percentiles 25/50/75 for durations and drawdowns

Validated against hint top10: exact match for drawdown and duration (peak->trough).
"""

import yfinance as yf
import pandas as pd

START = "1950-01-01"


def fetch_close():
    df = yf.download("^GSPC", start=START, progress=False, auto_adjust=False)
    if isinstance(df.columns, pd.MultiIndex):
        close = df["Close"]["^GSPC"]
    else:
        close = df["Close"]
    close = close.dropna()
    close.index = pd.to_datetime(close.index)
    return close


def compute_corrections(close):
    cummax = close.cummax()
    is_ath = close == cummax
    ath_dates = close.index[is_ath]
    ath_vals = close[is_ath]
    records = []
    for i in range(len(ath_dates) - 1):
        high_date = ath_dates[i]
        high_price = float(ath_vals.iloc[i])
        next_high_date = ath_dates[i + 1]
        mask = (close.index > high_date) & (close.index < next_high_date)
        if not mask.any():
            continue
        window = close[mask]
        low_price = float(window.min())
        low_date = window.idxmin()
        drawdown = (high_price - low_price) / high_price * 100
        dur_pt = (low_date - high_date).days  # peak->trough per hint
        dur_pp = (next_high_date - high_date).days  # peak->peak alternative
        records.append(
            {
                "high_date": high_date,
                "high": high_price,
                "low_date": low_date,
                "low": low_price,
                "next_high_date": next_high_date,
                "drawdown": drawdown,
                "dur_pt": dur_pt,
                "dur_pp": dur_pp,
            }
        )
    return pd.DataFrame(records)


def main():
    close = fetch_close()
    print(f"Fetched {len(close)} trading days from {close.index.min().date()} to {close.index.max().date()}")
    cummax = close.cummax()
    ath_count = (close == cummax).sum()
    print(f"ATH count: {ath_count}")

    df_corr = compute_corrections(close)
    print(f"Total corrections (ATH pairs with window): {len(df_corr)}")

    df_sig = df_corr[df_corr["drawdown"] >= 5].copy()
    print(f"Significant corrections >=5%: {len(df_sig)}")

    # Sort by drawdown descending
    df_sig_sorted = df_sig.sort_values("drawdown", ascending=False)
    print("\nTop 12 significant corrections (validates hint):")
    print(df_sig_sorted.head(12).to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x, float) else str(x)))

    # Percentiles
    print("\n--- Percentiles for significant corrections (>=5%) ---")
    for col, label in [("drawdown", "Drawdown %"), ("dur_pt", "Duration peak->trough (days)"), ("dur_pp", "Duration peak->peak (days)")]:
        qs = df_sig[col].quantile([0.25, 0.5, 0.75])
        print(f"{label:30} 25%={qs.loc[0.25]:.2f}  50% (median)={qs.loc[0.5]:.2f}  75%={qs.loc[0.75]:.2f}")

    # Answer
    median_dd = df_sig["drawdown"].median()
    median_dur_pt = df_sig["dur_pt"].median()
    print(f"\nAnswer Q3: Median drawdown of significant corrections (>=5%) is {median_dd:.2f}% (p25={df_sig['drawdown'].quantile(0.25):.2f}%, p75={df_sig['drawdown'].quantile(0.75):.2f}%)")
    print(f"Median duration (peak->trough): {median_dur_pt:.1f} days (p25={df_sig['dur_pt'].quantile(0.25):.0f}, p75={df_sig['dur_pt'].quantile(0.75):.0f})")
    print(f"Median duration (peak->peak alternative): {df_sig['dur_pp'].median():.1f} days")

    # Hint verification table
    hints = [
        ("2007-10-09", "2009-03-09", 56.8, 517),
        ("2000-03-24", "2002-10-09", 49.1, 929),
        ("1973-01-11", "1974-10-03", 48.2, 630),
        ("1968-11-29", "1970-05-26", 36.1, 543),
        ("2020-02-19", "2020-03-23", 33.9, 33),
        ("1987-08-25", "1987-12-04", 33.5, 101),
        ("1961-12-12", "1962-06-26", 28.0, 196),
        ("1980-11-28", "1982-08-12", 27.1, 622),
        ("2022-01-03", "2022-10-12", 25.4, 282),
        ("1966-02-09", "1966-10-07", 22.2, 240),
    ]
    print("\n--- Hint verification (high->low) ---")
    for h, l, exp_dd, exp_dur in hints:
        rec = df_corr[df_corr["high_date"] == pd.Timestamp(h)]
        if rec.empty:
            print(f"{h} not found as ATH")
        else:
            r = rec.iloc[0]
            print(
                f"{h} -> {r['low_date'].date()}  calc dd {r['drawdown']:.2f}% vs {exp_dd}%  dur {r['dur_pt']} vs {exp_dur}  {'OK' if abs(r['drawdown']-exp_dd)<0.2 and r['dur_pt']==exp_dur else 'MISMATCH'}"
            )


if __name__ == "__main__":
    main()
