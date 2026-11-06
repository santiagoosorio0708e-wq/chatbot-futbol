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
