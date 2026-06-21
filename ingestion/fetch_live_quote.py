"""
Phase 1: Live quote polling (preview of streaming)

Polls Finnhub's REST quote endpoint every N seconds for a list of
tickers and appends raw JSON snapshots to data/raw/live_quotes/.

This is intentionally simple (polling, not streaming) so you can see
*why* polling doesn't scale for real-time data before we replace this
with a Kafka + websocket pipeline in Phase 2.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/quote"
RAW_DATA_DIR = Path("data/raw/live_quotes")
TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
POLL_INTERVAL_SECONDS = 15


def fetch_quote(ticker: str) -> dict:
    resp = requests.get(BASE_URL, params={"symbol": ticker, "token": API_KEY}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    data["ticker"] = ticker
    data["polled_at"] = datetime.now(timezone.utc).isoformat()
    return data


def append_snapshot(snapshot: dict):
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = RAW_DATA_DIR / f"quotes_{today}.jsonl"
    with open(out_path, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


def main():
    if not API_KEY:
        raise RuntimeError("FINNHUB_API_KEY not set. Copy .env.example to .env and add your key.")

    logger.info(f"Polling {len(TICKERS)} tickers every {POLL_INTERVAL_SECONDS}s. Ctrl+C to stop.")
    try:
        while True:
            for ticker in TICKERS:
                try:
                    snapshot = fetch_quote(ticker)
                    append_snapshot(snapshot)
                    logger.info(f"{ticker}: price={snapshot.get('c')}")
                except requests.RequestException as e:
                    logger.error(f"Failed to fetch {ticker}: {e}")
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Stopped polling.")


if __name__ == "__main__":
    main()
