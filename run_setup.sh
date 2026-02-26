#!/usr/bin/env bash
# Run on Unix/macOS: create venv, install deps, prepare DB and run app
set -e
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python setup_everything.py
python scripts/auto_populate.py
echo "Starting Flask app..."
python app.py