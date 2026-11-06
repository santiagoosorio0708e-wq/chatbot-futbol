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
            """, unsafe_allow_html=True)
        elif msg["tipo"] == "asistente":
            color = msg.get("color_rendimiento", "verde")
            sentimiento = msg.get("sentimiento", "neutral")
            registro_id = msg.get("id_registro", "")
            analisis = msg.get("analisis", "")
            rendimiento = msg.get("rendimiento", "")
            titulos = msg.get("titulos", [])
            
            icono_semaforo = "🟢" if color == "verde" else ("🟡" if color == "amarillo" else "🔴")
            
            titulos_html = "".join([f'<span class="trophy-badge">🏆 {t}</span>' for t in titulos])
            
            st.markdown(f"""
            <div class="chat-card-assistant border-{color}">
                <div class="badge-bot-container">
                    <div class="badge-bot-left">
                        <span class="icon-circle-bot">🤖</span>
                        <span class="badge-bot-name">{msg['jugador_nombre']}</span>
                    </div>
                    <span class="semaforo-pill semaforo-{color}">{icono_semaforo} Rendimiento: {color.capitalize()}</span>
                </div>
                <div class="opinion-saved-header">
                    Opinión guardada. Sentimiento estimado: <strong>{sentimiento}</strong>.
                </div>
                <div class="analysis-text">{analisis}</div>
                {f'<div style="margin-bottom: 8px; color: #8b949e; font-size: 0.88rem;"><strong>Evaluación deportiva:</strong> {rendimiento}</div>' if rendimiento else ''}
                {f'<div style="margin-bottom: 10px;">{titulos_html}</div>' if titulos_html else ''}
                <div class="record-id">Registro: {registro_id}</div>
            </div>
            """, unsafe_allow_html=True)

    # Input para enviar opinión con validación entre 5 y 1000 caracteres
    opinion_input = st.chat_input("Opinión sobre el jugador seleccionado (5 a 1000 caracteres)")

    if opinion_input:
        texto = opinion_input.strip()
        if len(texto) < 5:
            st.warning("⚠️ La opinión es demasiado corta. Debe tener al menos 5 caracteres.")
        elif len(texto) > 1000:
            st.warning("⚠️ La opinión es demasiado larga. No puede superar los 1000 caracteres.")
        else:
            with st.spinner("Analizando objetivamente con IA..."):
                # Procesar análisis con IA
                resultado = motor_ia.procesar_opinion(
                    jugador=jugador_actual,
                    opinion_usuario=texto,
                    modelo=modelo
                )
                
                # Persistir en JSON
                registro = gestor_datos.guardar_opinion(
                    jugador_id=jugador_actual["id"],
                    jugador_nombre=jugador_actual["nombre"],
                    opinion_usuario=texto,
                    sentimiento=resultado.get("sentimiento", "neutral"),
                    analisis_objetivo=resultado.get("analisis_objetivo", ""),
                    color_rendimiento=resultado.get("color_rendimiento", "verde"),
                    titulos_relevantes=resultado.get("titulos_relevantes", []),
                    evaluacion_rendimiento=resultado.get("evaluacion_rendimiento", "")
                )
                
                # Agregar al historial de la sesión
                st.session_state.mensajes.append({
                    "tipo": "usuario",
                    "jugador_id": jugador_actual["id"],
                    "jugador_nombre": jugador_actual["nombre"],
                    "contenido": texto
                })
                
                st.session_state.mensajes.append({
                    "tipo": "asistente",
                    "jugador_id": jugador_actual["id"],
                    "jugador_nombre": jugador_actual["nombre"],
                    "sentimiento": resultado.get("sentimiento", "neutral"),
                    "color_rendimiento": resultado.get("color_rendimiento", "verde"),
                    "analisis": resultado.get("analisis_objetivo", ""),
                    "rendimiento": resultado.get("evaluacion_rendimiento", ""),
                    "titulos": resultado.get("titulos_relevantes", []),
                    "id_registro": registro["id"]
                })
                
                st.rerun()

elif seccion == "Consultar opiniones":
    st.markdown('<div class="section-header">Base de Datos de Opiniones y Evaluaciones</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Consulta el registro histórico de opiniones almacenadas y su evaluación objetiva.</div>', unsafe_allow_html=True)
    
    todas_opiniones = gestor_datos.cargar_opiniones()
    
    # Filtros superiores
    col1, col2, col3 = st.columns([2, 1.5, 1.5])
    with col1:
        filtro_jugador = st.selectbox(
            "Filtrar por futbolista:",
            ["Todos los futbolistas"] + [f"{j['nombre']} ({j['pais']})" for j in catalogo]
        )
    with col2:
        filtro_sentimiento = st.selectbox(
            "Filtrar por sentimiento:",
            ["Todos", "positivo", "neutral", "negativo"]
        )
    with col3:
        filtro_color = st.selectbox(
            "Semáforo de rendimiento:",
            ["Todos", "verde", "amarillo", "rojo"]
        )
        
    # Aplicar filtros
    opiniones_filtradas = todas_opiniones
    if filtro_jugador != "Todos los futbolistas":
        nombre_filtro = filtro_jugador.split(" (")[0]
        opiniones_filtradas = [op for op in opiniones_filtradas if op.get("jugador_nombre") == nombre_filtro]
        
    if filtro_sentimiento != "Todos":
        opiniones_filtradas = [op for op in opiniones_filtradas if op.get("sentimiento") == filtro_sentimiento]
        
    if filtro_color != "Todos":
        opiniones_filtradas = [op for op in opiniones_filtradas if op.get("color_rendimiento") == filtro_color]

    # Métricas de resumen
    st.markdown("### Métricas Generales")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Opiniones", len(todas_opiniones))
    with m2:
        verde_count = sum(1 for op in todas_opiniones if op.get("color_rendimiento") == "verde")
        st.metric("🟢 Rendimiento Alto", verde_count)
    with m3:
        amarillo_count = sum(1 for op in todas_opiniones if op.get("color_rendimiento") == "amarillo")
        st.metric("🟡 Rendimiento Regular", amarillo_count)
    with m4:
        rojo_count = sum(1 for op in todas_opiniones if op.get("color_rendimiento") == "rojo")
        st.metric("🔴 Rendimiento Crítico", rojo_count)

    # Gráficos analíticos de distribución si hay registros
    if todas_opiniones:
        st.markdown("### Análisis Estadístico de la Tribuna")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            st.caption("Distribución por Semáforo de Rendimiento")
            df_colores = pd.DataFrame({
                "Categoría": ["🟢 Alto (Verde)", "🟡 Regular (Amarillo)", "🔴 Crítico (Rojo)"],
                "Total": [verde_count, amarillo_count, rojo_count]
            }).set_index("Categoría")
            st.bar_chart(df_colores, color="#238636")
            
        with g_col2:
            st.caption("Distribución por Sentimiento de Aficionados")
            pos_count = sum(1 for op in todas_opiniones if op.get("sentimiento") == "positivo")
            neu_count = sum(1 for op in todas_opiniones if op.get("sentimiento") == "neutral")
            neg_count = sum(1 for op in todas_opiniones if op.get("sentimiento") == "negativo")
            df_sentimientos = pd.DataFrame({
                "Sentimiento": ["👍 Positivo", "⚖️ Neutral", "👎 Negativo"],
                "Total": [pos_count, neu_count, neg_count]
            }).set_index("Sentimiento")
            st.bar_chart(df_sentimientos, color="#1f6feb")

    # Botones de exportación
    if todas_opiniones:
