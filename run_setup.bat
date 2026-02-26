@echo off
REM Run on Windows: create venv, install deps, prepare DB and run app
if not exist .venv ( 
    python -m venv .venv
)
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python scripts\full_setup.py
echo Starting Flask app...
.venv\Scripts\python app.py