#!/usr/bin/env bash
set -e

echo "▶ Sprawdzanie Pythona..."
if ! command -v python3 &> /dev/null; then
  echo "❌ Python3 nie jest zainstalowany."
  exit 1
fi

echo "▶ Tworzenie / aktywacja venv..."
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

echo "▶ Aktualizacja pip..."
pip install --upgrade pip

echo "▶ Instalacja zależności..."
pip install -r requirements.txt

echo "▶ Uruchamianie aplikacji..."
python shopbooster.py
