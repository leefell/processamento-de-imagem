#!/bin/bash
# Equivalente a um "npm run dev": sobe a interface do corretor de gabarito.
# Uso: ./run.sh
set -e
cd "$(dirname "$0")"
./.venv/bin/python -m streamlit run app.py
