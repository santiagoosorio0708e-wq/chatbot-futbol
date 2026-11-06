"""Aplicación principal Tribuna Global en Streamlit."""
import os
import json
import pandas as pd
import streamlit as st
import gestor_datos
import motor_ia

# Configuración inicial de la página
st.set_page_config(
    page_title="Tribuna Global",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados para emular fielmente la interfaz de Tribuna Global
st.markdown("""
<style>
    /* Estilos globales */
    .stApp {
        background-color: #0d1117;
        color: #f0f2f6;
    }
    
    /* Encabezado principal */
    .main-title {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 2px;
        color: #ffffff;
    }
    .subtitle {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 22px;
    }
    .section-header {
        font-size: 1.45rem;
        font-weight: 600;
        margin-top: 8px;
        margin-bottom: 4px;
        color: #ffffff;
    }
    .section-caption {
        color: #8b949e;
        font-size: 0.88rem;
        margin-bottom: 24px;
    }
    
    /* Tarjeta de mensaje del aficionado (Réplica Captura 2) */
    .chat-card-user {
        background-color: #161b22;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border: 1px solid #30363d;
    }
    .badge-user-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 12px;
    }
    .icon-circle-user {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #e02424;
        color: #ffffff;
        font-size: 14px;
    }
    .badge-user-name {
        font-weight: 600;
        color: #f0f2f6;
        font-size: 0.92rem;
    }

    /* Tarjeta de mensaje de la IA (Réplica Captura 2 con Semáforo) */
    .chat-card-assistant {
        background-color: #161b22;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 24px;
        border: 1px solid #30363d;
        border-left: 5px solid #3b82f6;
    }
    .chat-card-assistant.border-verde {
        border-left: 5px solid #238636 !important;
    }
    .chat-card-assistant.border-amarillo {
        border-left: 5px solid #d29922 !important;
    }
    .chat-card-assistant.border-rojo {
        border-left: 5px solid #da3633 !important;
    }
    
    .badge-bot-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .badge-bot-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .icon-circle-bot {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #d97706;
        color: #ffffff;
        font-size: 14px;
    }
    .badge-bot-name {
        font-weight: 600;
        color: #f0f2f6;
        font-size: 0.92rem;
    }
    
    /* Semáforo Tags */
    .semaforo-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .semaforo-verde {
        background-color: rgba(35, 134, 54, 0.2);
        color: #3fb950;
        border: 1px solid #238636;
    }
    .semaforo-amarillo {
        background-color: rgba(210, 153, 34, 0.2);
        color: #e3b341;
        border: 1px solid #d29922;
    }
    .semaforo-rojo {
        background-color: rgba(218, 54, 51, 0.2);
        color: #f85149;
        border: 1px solid #da3633;
    }
    
    .opinion-saved-header {
        color: #e6edf3;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    .analysis-text {
        color: #c9d1d9;
        font-size: 0.94rem;
        line-height: 1.55;
        margin-bottom: 14px;
    }
    .trophy-badge {
        display: inline-block;
        background-color: #21262d;
        color: #79c0ff;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 0.78rem;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #30363d;
    }
    .record-id {
        font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace;
        font-size: 0.82rem;
        color: #8b949e;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Cargar catálogo de futbolistas
catalogo = gestor_datos.cargar_catalogo_jugadores()
