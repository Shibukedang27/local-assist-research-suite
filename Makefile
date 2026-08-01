.PHONY: check test

check:
	python -m ruff check .
	python -m ruff format --check .
	python -m pytest -q

test:
	python -m pytest -q

