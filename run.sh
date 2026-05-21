#!/usr/bin/env bash
set -euo pipefail

# Simple helper to run the Streamlit app
if ! command -v streamlit >/dev/null 2>&1; then
  echo "streamlit not found. Install dependencies with: pip install -r requirements.txt"
  exit 1
fi

streamlit run app.py
