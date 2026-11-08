@echo off
chcp 65001 > nul
title Tribuna Global - Chatbot IA de Futbol

echo ========================================================
echo   ⚽ TRIBUNA GLOBAL - CHATBOT IA DE FUTBOL
echo ========================================================
echo.
echo [1/3] Verificando entorno de Python...

where py >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=py
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PY_CMD=python
    ) else (
        echo [ERROR] No se encontro Python instalado en el sistema.
        echo Por favor instala Python 3.10 o superior desde https://www.python.org/
        pause
        exit /b 1
    )
)

echo [OK] Python detectado: %PY_CMD%

echo.
echo [2/3] Verificando dependencias del proyecto...
%PY_CMD% -m pip install -r requirements.txt --quiet --disable-pip-version-check

if not exist .env (
    if exist .env.example (
        echo [INFO] Creando archivo .env inicial...
        copy .env.example .env >nul
    )
)

echo.
echo [3/3] Iniciando servidor y abriendo navegador en http://localhost:8501...
echo.

start "" "http://localhost:8501"
%PY_CMD% -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501

pause
