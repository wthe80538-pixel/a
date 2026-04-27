from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("data") / "2330_TW.csv"
OUTPUT_PATH = Path("data") / "2330_TW_features.csv"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize possible yfinance CSV column formats into flat OHLCV names."""
    df = df.copy()

    # Handle yfinance multi-level headers if present.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]) for col in df.columns]

    # If Date is saved as index and appears as unnamed column after read_csv.
    if "Date" not in df.columns:
        first_col = str(df.columns[0])
        if first_col.lower().startswith("unnamed"):
            df = df.rename(columns={df.columns[0]: "Date"})

    required = {"Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"}
    missing = required.difference(set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns in input CSV: {sorted(missing)}")

    return df


def build_features() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)
    df = _normalize_columns(df)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Base return feature (today vs yesterday): only uses current/past data.
    df["daily_return"] = df["Close"].pct_change()

    # Moving-average features: rolling windows use current and historical values only.
    df["ma_5"] = df["Close"].rolling(window=5, min_periods=5).mean()
    df["ma_20"] = df["Close"].rolling(window=20, min_periods=20).mean()
    df["ma_60"] = df["Close"].rolling(window=60, min_periods=60).mean()

    # Volume moving averages.
    df["volume_ma_5"] = df["Volume"].rolling(window=5, min_periods=5).mean()
    df["volume_ma_20"] = df["Volume"].rolling(window=20, min_periods=20).mean()

    # 20-day historical volatility from daily returns.
    df["volatility_20"] = df["daily_return"].rolling(window=20, min_periods=20).std(ddof=0)

    # Targets: allowed to use future information.
    df["target_5d_return"] = df["Close"].shift(-5) / df["Close"] - 1
    df["target_up_5d"] = (df["target_5d_return"] > 0).astype(np.int8)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved features to: {OUTPUT_PATH}")
    print(df.tail(5))


if __name__ == "__main__":
    build_features()
