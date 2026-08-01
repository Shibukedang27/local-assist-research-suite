from pathlib import Path

import pytest

from local_assist.approvals import approve_review, create_review


def test_review_approval_never_submits(tmp_path: Path):
    database = tmp_path / "reviews.sqlite3"
    pending = create_review(database, "example job", "example draft")
    assert pending["status"] == "pending"
    approved = approve_review(database, pending["id"])
    assert approved["status"] == "approved"
    assert approved["submission_performed"] is False
    with pytest.raises(ValueError):
        approve_review(database, pending["id"])
