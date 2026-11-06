@echo off
chcp 65001 > nul
echo ========================================================
echo   Iniciando Tribuna Global - Chatbot IA de Futbol
echo ========================================================
echo.
echo Conectando servidor local en http://localhost:8501...
echo.
py -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause

