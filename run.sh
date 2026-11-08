#!/usr/bin/env bash
echo "========================================================"
echo "  ⚽ TRIBUNA GLOBAL - CHATBOT IA DE FUTBOL"
echo "========================================================"
echo ""

if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] No se encontró Python instalado en el sistema."
    echo "Por favor instala Python 3.10 o superior."
    exit 1
fi

echo "[1/3] Python detectado: $PY_CMD"
echo "[2/3] Verificando dependencias..."
$PY_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check

if [ ! -f .env ] && [ -f .env.example ]; then
    echo "[INFO] Generando .env inicial..."
    cp .env.example .env
fi

echo "[3/3] Iniciando servidor en http://localhost:8501..."
if command -v xdg-open &>/dev/null; then
    xdg-open "http://localhost:8501" &
elif command -v open &>/dev/null; then
    open "http://localhost:8501" &
fi

$PY_CMD -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501

