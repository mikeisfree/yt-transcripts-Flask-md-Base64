#!/bin/bash

# Skrypt startowy dla YouTube Transcript API

echo "Uruchamianie YouTube Transcript API..."

# Sprawdź czy Python jest dostępny
if ! command -v python3 &> /dev/null; then
    echo "Błąd: Python3 nie jest zainstalowany"
    exit 1
fi

# Sprawdź czy requirements.txt istnieje
if [ ! -f "requirements.txt" ]; then
    echo "Tworzenie requirements.txt..."
    cat > requirements.txt << EOF
flask>=3.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
youtube-transcript-api>=0.6.0
EOF
fi

# Instalacja zależności jeśli potrzebne
if [ ! -d "venv" ]; then
    echo "Tworzenie wirtualnego środowiska..."
    python3 -m venv venv
fi

echo "Aktywacja wirtualnego środowiska i instalacja zależności..."
source venv/bin/activate
pip install -r requirements.txt

# Uruchom API
echo "Start API na porcie 5000..."
export FLASK_APP= api_server.py
export FLASK_ENV=production
python3 api_server.py