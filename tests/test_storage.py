from pathlib import Path

import duckdb

from local_assist.storage import to_parquet


def test_csv_to_parquet(tmp_path: Path):
    destination = tmp_path / "sample.parquet"
    to_parquet(Path("examples/vedanta.synthetic.csv"), destination)
    assert destination.exists()
    with duckdb.connect() as connection:
        count = connection.execute(
            "SELECT count(*) FROM read_parquet(?)", [str(destination)]
        ).fetchone()
    assert count == (25,)
