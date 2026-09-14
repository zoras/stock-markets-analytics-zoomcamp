"""
Question 1: [Index] S&P 500 Stocks Added to the Index
Source: cohorts/2026/homework1.md:6-32

Implements steps described in homework:
1. Download Wikipedia S&P 500 list with headers (hint code)
2. Create DataFrame with tickers, names, year added
3. Extract year and count additions per year from 2020
4. Answer which year had highest additions

Also answers Additional: how many stocks >20 years in index.
"""

import requests
import pandas as pd
from io import StringIO

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_sp500():
    # Hint code from homework1.md:14-18
    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()
    # Use StringIO wrapper to avoid lxml file-path misinterpretation
    tables = pd.read_html(StringIO(response.text))
    df = tables[0]  # main table: 503 rows x 8 cols
    return df

def main():
    df = fetch_sp500()
    print(f"Fetched {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # Step 1: DataFrame with tickers, names, year added
    # Keep Symbol, Security, Date added
    df["Date added"] = pd.to_datetime(df["Date added"], errors="coerce")
    assert df["Date added"].isna().sum() == 0, "Unexpected NaT in Date added"

    df["year_added"] = df["Date added"].dt.year

    # Small preview
    print("\n--- Preview ---")
    print(df[["Symbol", "Security", "Date added", "year_added"]].head().to_string(index=False))

    # Step 2: counts per year
    counts = df["year_added"].value_counts().sort_index()  # type: ignore[attr-defined]
    print("\n--- Counts per year (from 2020) ---")
    from_2020 = counts[counts.index >= 2020].sort_values(ascending=False)  # type: ignore[attr-defined]
    print(from_2020.to_string())
    # also print sorted by year for reference
    print("\n--- Counts per year 2020-2026 sorted by year ---")
    print(counts[counts.index >= 2020].sort_index().to_string())  # type: ignore[attr-defined]

    # Step 3: answer
    max_year = int(from_2020.idxmax())  # type: ignore[arg-type]
    max_count = int(from_2020.max())  # type: ignore[arg-type]
    print(f"\nAnswer Q1: Year with highest additions (from 2020) is {max_year} with {max_count} stocks")

    # Detail: list tickers for max year
    print(f"\nStocks added in {max_year}:")
    added_max = df[df["year_added"] == max_year][["Symbol", "Security", "Date added"]].sort_values("Date added")  # type: ignore[attr-defined]
    print(added_max.to_string(index=False))
    print(f"Count verification: {len(added_max)}")

    # Additional: >20 years
    ref_date = pd.Timestamp("2026-09-04")  # Wikipedia last edited date, close to homework timing
    cutoff = ref_date - pd.DateOffset(years=20)  # type: ignore[operator]
    more20_exact = (df["Date added"] < cutoff).sum()
    more20_year_lt2006 = (df["year_added"] < 2006).sum()          # strictly >20 calendar years (2005 and before)
    more20_year_le2006 = (df["year_added"] <= 2006).sum()         # inclusive 2006
    more20_year_le2005 = (df["year_added"] <= 2005).sum()         # same as <2006

    print("\n--- Additional: >20 years in index (as of 2026) ---")
    print(f"Reference cutoff (20y before {ref_date.date()}): {cutoff.date()}")
    print(f"Stocks added before {cutoff.date()} (exact date < cutoff): {more20_exact}")
    print(f"Stocks with year_added < 2006 (i.e., <=2005, strict >20y): {more20_year_lt2006}")
    print(f"Stocks with year_added <= 2006 (inclusive): {more20_year_le2006}")
    # If someone uses 2026-20=2006 as boundary, answer 227 or 218 depending on inclusive.
    # Provide median context
    print(f"\nNote: if counting full calendar years as of 2026, >20 years means added in 2005 or earlier => {more20_year_le2005}")

if __name__ == "__main__":
    main()
