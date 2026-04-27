from __future__ import annotations

from pathlib import Path

import yfinance as yf


DEFAULT_TICKER = "2330.TW"
PERIOD = "3y"
INTERVAL = "1d"
OUTPUT_PATH = Path("data") / "2330_TW.csv"


def download_price(ticker: str = DEFAULT_TICKER) -> None:
    """Download daily OHLCV price data and save it to CSV."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = yf.download(ticker, period=PERIOD, interval=INTERVAL, auto_adjust=False)

    if data.empty:
        raise ValueError(f"No data downloaded for ticker: {ticker}")

    data.to_csv(OUTPUT_PATH)

    print(f"Saved {ticker} data to: {OUTPUT_PATH}")
    print("Last 5 rows:")
    print(data.tail(5))


if __name__ == "__main__":
    download_price()
