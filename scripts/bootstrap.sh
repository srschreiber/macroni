#!/usr/bin/env bash
set -e

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "Bootstrap complete."
echo "Activate with: source .venv/bin/activate"
