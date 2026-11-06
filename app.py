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
if not catalogo:
    st.error("No se pudo cargar el archivo datos/jugadores.json. Verifica la ruta.")
    st.stop()

# Mapeo de jugadores para selector
opciones_jugadores = {f"{j['nombre']} · {j['pais']}": j for j in catalogo}
lista_nombres = list(opciones_jugadores.keys())

# Inicializar estado de sesión
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "jugador_seleccionado" not in st.session_state:
    st.session_state.jugador_seleccionado = lista_nombres[0]

# --- BARRA LATERAL (CONFIGURACIÓN) ---
st.sidebar.markdown("## Configuración")

seccion = st.sidebar.radio(
    "Sección",
    ["Emitir opinión", "Consultar opiniones"],
    index=0
)

# Selector de jugador
seleccion_jugador = st.sidebar.selectbox(
    "Jugador",
    options=lista_nombres,
    index=lista_nombres.index(st.session_state.jugador_seleccionado) if st.session_state.jugador_seleccionado in lista_nombres else 0
)
st.session_state.jugador_seleccionado = seleccion_jugador
jugador_actual = opciones_jugadores[seleccion_jugador]

# Selector de Modelo
modelo_defecto = os.getenv("DEFAULT_MODEL", "gemini-3.1-flash-lite")
modelo = st.sidebar.text_input("Modelo", value=modelo_defecto)
st.sidebar.caption("El modelo configurado debe admitir temperatura 0 y salida JSON Schema.")

# Configuración opcional de API Key
with st.sidebar.expander("🔑 Credenciales de API (Opcional)", expanded=False):
    api_key_input = st.text_input("API Key (Gemini / OpenAI):", type="password", placeholder="AQ... o sk-...")
    if api_key_input:
        if api_key_input.startswith("AQ.") or api_key_input.startswith("AIza"):
            os.environ["GEMINI_API_KEY"] = api_key_input
            os.environ["GOOGLE_API_KEY"] = api_key_input
            st.caption("✅ Clave Gemini configurada en la sesión.")
        else:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.caption("✅ Clave OpenAI configurada en la sesión.")
    else:
        st.caption("✅ Clave cargada de forma segura desde variable de entorno (.env).")

st.sidebar.markdown("---")

# Botón Nueva conversación
if st.sidebar.button("Nueva conversación", use_container_width=True):
    st.session_state.mensajes = []
    st.rerun()

st.sidebar.caption(
    "La nueva conversación limpia el chat y los envíos pendientes; conserva los registros guardados."
)


# --- ÁREA PRINCIPAL ---
st.markdown('<div class="main-title">⚽ Tribuna Global</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Opiniones de aficionados sobre futbolistas. Las categorías son estimaciones de IA.</div>', unsafe_allow_html=True)

if seccion == "Emitir opinión":
    st.markdown(f'<div class="section-header">Opiniones sobre {jugador_actual["nombre"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Cada envío se analiza de forma independiente y se asocia al jugador seleccionado.</div>', unsafe_allow_html=True)

    # Filtrar mensajes asociados al jugador actual o mostrados en la sesión
    mensajes_jugador = [m for m in st.session_state.mensajes if m.get("jugador_id") == jugador_actual["id"]]

    for msg in mensajes_jugador:
        if msg["tipo"] == "usuario":
            st.markdown(f"""
            <div class="chat-card-user">
                <div class="badge-user-container">
                    <span class="icon-circle-user">👤</span>
                    <span class="badge-user-name">{msg['jugador_nombre']}</span>
                </div>
                <div style="font-size: 0.96rem; color: #f0f2f6;">{msg['contenido']}</div>
            </div>
