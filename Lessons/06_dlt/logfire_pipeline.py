"""Load recent Logfire records into DuckDB with dlt.

Required environment variables (kept in .env):
    LOGFIRE_READ_TOKEN

Optional:
    LOGFIRE_BASE_URL=https://logfire-eu.pydantic.dev
    LOGFIRE_LOOKBACK_DAYS=7
"""

import os
from datetime import UTC, datetime, timedelta
from typing import Any, Iterator

import dlt
import requests
from dotenv import load_dotenv


load_dotenv()

READ_TOKEN = os.environ["LOGFIRE_READ_TOKEN"]
BASE_URL = os.getenv("LOGFIRE_BASE_URL", "https://logfire-eu.pydantic.dev")
LOOKBACK_DAYS = int(os.getenv("LOGFIRE_LOOKBACK_DAYS", "7"))


@dlt.resource(name="records", write_disposition="replace")
def logfire_records() -> Iterator[dict[str, Any]]:
    """Fetch Logfire records, preserving nested fields for dlt normalization."""
    query = "SELECT * FROM records"
    response = requests.post(
        f"{BASE_URL.rstrip('/')}/v2/query",
        headers={"Authorization": f"Bearer {READ_TOKEN}", "Accept": "application/json"},
        json={
            "sql": query,
            "min_timestamp": (datetime.now(UTC) - timedelta(days=LOOKBACK_DAYS)).isoformat(),
            "limit": 10_000,
        },
        timeout=60,
    )
    response.raise_for_status()

    # The JSON API returns {"schema": ..., "data": [record, ...]}.
    for record in response.json()["data"]:
        yield record


def main() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_traces",
        destination="duckdb",
        dataset_name="agent_traces",
    )
    load_info = pipeline.run(logfire_records())
    print(load_info)
    print(f"DuckDB database: {pipeline.destination_client().config.credentials}")


if __name__ == "__main__":
    main()
