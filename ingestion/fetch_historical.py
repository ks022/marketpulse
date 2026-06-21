"""
Phase 1: Historical data ingestion (bronze layer)

Pulls daily OHLCV (open/high/low/close/volume) for a list of tickers
using yfinance and lands it as partitioned Parquet files under
data/raw/historical/{ticker}/{ticker}_{start}_{end}.parquet

This is a "bronze" landing zone: raw, untransformed, as close to the
source as possible. We never overwrite or mutate raw data -- later
pipeline stages (silver/gold) read from here and transform it.
"""

import argparse
import logging
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_DIR = Path("data/raw/historical")


def fetch_ticker_history(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Fetch daily OHLCV history for a single ticker."""
    logger.info(f"Fetching {ticker} from {start} to {end}")
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        logger.warning(f"No data returned for {ticker}")
        return df
    df = df.reset_index()
    df.columns = [str(c).lower() for c in df.columns]
    df["ticker"] = ticker
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def save_to_bronze(df: pd.DataFrame, ticker: str, start: str, end: str) -> Path:
    """Land raw data as Parquet, partitioned by ticker."""
    ticker_dir = RAW_DATA_DIR / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)
    out_path = ticker_dir / f"{ticker}_{start}_{end}.parquet"
    df.to_parquet(out_path, index=False)
    logger.info(f"Wrote {len(df)} rows -> {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Fetch historical stock data into the bronze layer")
    parser.add_argument("--tickers", nargs="+", default=["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"])
    parser.add_argument("--start", default="2023-01-01")
    parser.add_argument("--end", default=str(date.today()))
    args = parser.parse_args()

    for ticker in args.tickers:
        df = fetch_ticker_history(ticker, args.start, args.end)
        if not df.empty:
            save_to_bronze(df, ticker, args.start, args.end)

    logger.info("Historical ingestion complete.")


if __name__ == "__main__":
    main()
