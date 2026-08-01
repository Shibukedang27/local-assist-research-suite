import json
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from local_assist.stocks import fetch_yahoo_history


class Response(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def test_fetch_writes_local_csv(tmp_path: Path):
    timestamps = [1_700_000_000 + index * 86_400 for index in range(25)]
    quote = {key: [100 + index for index in range(25)] for key in ("open", "high", "low", "close")}
    quote["volume"] = [1000 + index for index in range(25)]
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": timestamps,
                    "meta": {"currency": "INR"},
                    "indicators": {"quote": [quote]},
                }
            ]
        }
    }
    destination = tmp_path / "vedanta.csv"
    with patch("local_assist.stocks.urlopen", return_value=Response(json.dumps(payload).encode())):
        result = fetch_yahoo_history(destination, months=3)
    assert result["rows"] == 25
    assert destination.read_text().count("\n") == 26
