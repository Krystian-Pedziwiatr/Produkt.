@echo off
setlocal

echo ▶ Sprawdzanie Pythona...
where python >nul 2>nul
if errorlevel 1 (
    echo ❌ Python nie jest zainstalowany lub nie jest w PATH
    pause
    exit /b 1
)

echo ▶ Tworzenie / aktywacja venv...
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate

echo ▶ Aktualizacja pip...
python -m pip install --upgrade pip

echo ▶ Instalacja zależności...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Błąd instalacji pakietów
    pause
    exit /b 1
)

echo ▶ Uruchamianie aplikacji...
python shopbooster.py

pause
