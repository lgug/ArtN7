#!/bin/bash

set -e

BASE_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$BASE_DIR/ArtN7"
VENV_DIR="$BASE_DIR/venv"
REQUIREMENTS="$BASE_DIR/requirements.txt"
APP_PORT=8008
STATIC_ROOT="$PROJECT_DIR/staticfiles"

echo "🔍 Controllo ambiente virtuale..."
if [ ! -d "$VENV_DIR" ]; then
    echo "⚙️ Creazione ambiente virtuale..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "📦 Installazione dipendenze..."
pip install --upgrade pip
pip install -r "$REQUIREMENTS"

echo "🛠️ Migrazioni..."
python manage.py migrate

echo "📂 Raccolta file statici..."
python manage.py collectstatic --noinput

# Avvia il server di sviluppo Django solo per i file statici sulla porta 8001
echo "📂 Servizio statici su http://localhost:$APP_PORT"
python manage.py runserver 0.0.0.0:$APP_PORT --insecure