from local_assist.jobs import score_job


def test_job_output_requires_human_submission():
    result = score_job({"display_name": "A", "skills": ["Python", "SQL"]}, "Python SQL role")
    assert result.score > 0
    assert result.requires_human_submission is True
    assert "REVIEW REQUIRED" in result.draft
