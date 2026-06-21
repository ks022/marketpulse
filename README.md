# MarketPulse — real-time stock intelligence platform

An end-to-end data engineering + AI project: real-time and historical
stock data flows through a streaming pipeline into a warehouse, where
an AI agent layer lets you ask questions in plain English.

## Phase 1 — Data ingestion (this phase)

We're landing data in a **bronze layer**: raw, untouched, exactly as it
arrived from the source. Two scripts:

- `ingestion/fetch_historical.py` — backfills daily OHLCV history via yfinance
- `ingestion/fetch_live_quote.py` — polls Finnhub for live quotes every 15s

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Get a free Finnhub API key: sign up at https://finnhub.io/register
   (free tier is plenty for this project).

3. Copy `.env.example` to `.env` and paste in your key:
   ```bash
   cp .env.example .env
   ```

4. Run the historical backfill:
   ```bash
   python ingestion/fetch_historical.py --tickers AAPL MSFT GOOGL TSLA NVDA
   ```
   Check `data/raw/historical/` — you should see Parquet files per ticker.

5. Run the live quote poller (let it run a minute or two, then Ctrl+C):
   ```bash
   python ingestion/fetch_live_quote.py
   ```
   Check `data/raw/live_quotes/` — you should see a `.jsonl` file growing.

## Why polling instead of streaming, for now

The live quote script polls every 15 seconds — simple, but wasteful and
not truly real-time. In Phase 2, we replace this with Finnhub's
websocket feed pushed through Kafka, so you'll see firsthand *why*
streaming architectures exist and what problem they actually solve.

## Suggested next step

Push this to a GitHub repo now, before we add more. Starting version
control from commit #1 is itself a habit worth having on a DE resume.

## Roadmap

| Phase | Status |
|---|---|
| 1. Ingestion (APIs → bronze) | ← you are here |
| 2. Streaming (Kafka/Redpanda) | next |
| 3. Lake + warehouse | |
| 4. Orchestration (Airflow) | |
| 5. Transformation (dbt) | |
| 6. Data quality (Great Expectations) | |
| 7. AI agent: text-to-SQL | |
| 8. AI agent: anomaly detection + reports (RAG) | |
| 9. Dashboard (Streamlit) | |
| 10. Cloud deployment (AWS) + CI/CD | |
| 11. Polish + documentation | |
