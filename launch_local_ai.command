#!/bin/zsh
set -e

PROJECT_DIR="${0:A:h}"
cd "$PROJECT_DIR"

if [[ ! -x .venv/bin/local-assist ]]; then
  echo "Local Assist is not installed. Run the Quick start steps in README.md."
  read -k 1 "?Press any key to close."
  exit 1
fi

export PYTHONPATH="$PROJECT_DIR/src"
exec .venv/bin/python scripts/chat_scratch_model.py
