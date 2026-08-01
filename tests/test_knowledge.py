from pathlib import Path

from local_assist.knowledge import build_index, retrieve


def test_private_index_retrieves_relevant_context(tmp_path: Path):
    source = tmp_path / "knowledge.jsonl"
    source.write_text(
        '{"topic":"jobs","content":"Python and SQL are relevant skills."}\n'
        '{"topic":"stocks","content":"Vedanta signals must include uncertainty."}\n'
    )
    database = tmp_path / "knowledge.sqlite3"
    result = build_index(database, [source])
    matches = retrieve(database, "How should Vedanta uncertainty be shown?")
    assert result["documents"] == 2
    assert matches[0]["topic"] == "stocks"
