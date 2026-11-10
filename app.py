"""Aplicación principal Tribuna Global (Streamlit) con interfaz estilo 'Soccer AI Agent'.

Distribución de tres paneles:
  · Izquierda : historial de chats guardados localmente (agrupados por fecha).
  · Centro    : conversación con el agente, opiniones guardadas y ranking.
  · Derecha   : configuración del agente, ligas, filtros, jugador y accesos rápidos.
"""
import os
import json
import uuid
import importlib
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import gestor_datos
import motor_ia
import visual
from visual import esc, limpiar_html

# Forzar recarga en caliente de módulos de datos/IA para evitar errores de caché en Streamlit
importlib.reload(gestor_datos)
importlib.reload(motor_ia)

st.set_page_config(
    page_title="Tribuna Global · Soccer AI Agent",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(visual.CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Datos base
# ---------------------------------------------------------------------------
catalogo = gestor_datos.cargar_catalogo_jugadores()
if not catalogo:
    st.error("No se pudo cargar el archivo datos/jugadores.json. Verifica la ruta.")
    st.stop()

JUG = {j["id"]: j for j in catalogo}
IDS = [j["id"] for j in catalogo]

SECCIONES = ["💬 Chat", "📊 Opiniones", "🏅 Ranking"]
MODELOS = {
    "Gemini Pro Soccer (Active)": "gemini-3.1-flash-lite",
    "GPT-4 Football (OpenAI)": "gpt-4o-mini",
    "SoccerLLM 7B (Local)": "__local__",
    "Llama 3 Sport (Offline)": "__local__",
}
COLORES = ("verde", "amarillo", "rojo")
ICONO_COLOR = {"verde": "🟢", "amarillo": "🟡", "rojo": "🔴"}
TEXTO_COLOR = {"verde": "Alto", "amarillo": "Regular", "rojo": "Crítico"}


def nombre_de(jid):
    return JUG[jid]["nombre"] if jid in JUG else (jid or "Futbolista")


def foto(jid):
    return visual.foto_jugador(jid or "", nombre_de(jid))


def id_por_nombre(nombre):
    return next((j["id"] for j in catalogo if j["nombre"] == nombre), None)


def nuevo_id_chat():
    return f"conv_{uuid.uuid4().hex[:8]}"


def fecha_de(registro):
    for clave in ("fecha_actualizacion", "fecha", "timestamp"):
        valor = registro.get(clave)
        if valor:
            try:
                return datetime.fromisoformat(valor)
            except ValueError:
                continue
    return datetime.min


# ---------------------------------------------------------------------------
# Estado de sesión y callbacks (se ejecutan ANTES de crear los widgets)
# ---------------------------------------------------------------------------
def cargar_chat_en_sesion(conv_id):
    """Carga mensajes y futbolista de una conversación guardada en el estado de sesión."""
    st.session_state.conv_activa_id = conv_id
    data = gestor_datos.obtener_conversacion_por_id(conv_id)
    if data:
        st.session_state.mensajes = list(data.get("mensajes", []))
        if data.get("jugador_id") in JUG:
            st.session_state.sel_jugador = data["jugador_id"]
    else:
        st.session_state.mensajes = []


def cb_nuevo_chat():
    st.session_state.conv_activa_id = nuevo_id_chat()
    st.session_state.mensajes = []
    st.session_state.seccion = SECCIONES[0]


def cb_abrir_chat(conv_id):
    cargar_chat_en_sesion(conv_id)
    st.session_state.seccion = SECCIONES[0]


def cb_eliminar_chat(conv_id):
    gestor_datos.eliminar_conversacion(conv_id)
    if st.session_state.get("conv_activa_id") == conv_id:
        restantes = gestor_datos.cargar_conversaciones()
        if restantes:
            cargar_chat_en_sesion(restantes[0]["id"])
        else:
            cb_nuevo_chat()


def cb_prompt(texto):
    st.session_state.prompt_rapido = texto
    st.session_state.seccion = SECCIONES[0]


def cb_ir_opiniones(jid):
    st.session_state.op_jugador = jid
    st.session_state.seccion = SECCIONES[1]


def cb_ir_ranking():
    st.session_state.seccion = SECCIONES[2]


def cb_mas_opiniones():
    st.session_state.op_limite = st.session_state.get("op_limite", 30) + 30


if "conv_activa_id" not in st.session_state:
    st.session_state.mensajes = []
    st.session_state.sel_jugador = IDS[0]
    _previas = gestor_datos.cargar_conversaciones()
    if _previas:
        cargar_chat_en_sesion(_previas[0]["id"])
    else:
        st.session_state.conv_activa_id = nuevo_id_chat()
st.session_state.setdefault("seccion", SECCIONES[0])
st.session_state.setdefault("op_jugador", "todos")
st.session_state.setdefault("op_limite", 30)

# ---------------------------------------------------------------------------
# PANEL IZQUIERDO · Historial de chats
# ---------------------------------------------------------------------------
convs_guardadas = gestor_datos.cargar_conversaciones()
chat_activo = st.session_state.conv_activa_id

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-logo">⚽</div>'
        '<div class="brand-text">SOCCER<br><span>AI AGENT</span></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="panel-title">HISTORIALES DE CHAT</div>', unsafe_allow_html=True)
    st.button("➕ Nuevo chat", type="primary", width="stretch", on_click=cb_nuevo_chat, key="btn_nuevo_chat")
    busqueda = st.text_input(
        "Buscar chats", placeholder="🔍 Buscar en el historial…", label_visibility="collapsed", key="buscar_chat"
    ).strip().lower()

    items = []
    if chat_activo not in {c["id"] for c in convs_guardadas}:
        items.append({
            "id": chat_activo, "titulo": "✨ Nuevo chat", "pendiente": True,
            "jugador_id": st.session_state.get("sel_jugador"), "fecha": datetime.now().isoformat(),
        })
    items += convs_guardadas
    if busqueda:
        items = [c for c in items if busqueda in c.get("titulo", "").lower() or busqueda in c.get("jugador_nombre", "").lower()]
    items.sort(key=fecha_de, reverse=True)

    hoy = datetime.now().date()
    grupos = {"RECENT CHATS": [], "ÚLTIMOS 7 DÍAS": [], "HISTÓRICO": []}
    for c in items:
        dias = (hoy - fecha_de(c).date()).days if fecha_de(c) != datetime.min else 999
        clave = "RECENT CHATS" if dias <= 0 else "ÚLTIMOS 7 DÍAS" if dias < 7 else "HISTÓRICO"
        grupos[clave].append(c)

    if not items:
        st.caption("No hay chats que coincidan con la búsqueda.")
    for etiqueta, lista in grupos.items():
        if not lista:
            continue
        st.markdown(f'<div class="group-label">{etiqueta}</div>', unsafe_allow_html=True)
        for c in lista:
            cid = c["id"]
            titulo = c.get("titulo", "Chat")
            corto = titulo if len(titulo) <= 27 else titulo[:26] + "…"
            col_a, col_b, col_c = st.columns([1, 4.3, 1])
            with col_a:
                st.markdown(f'<img class="mini-avatar" src="{foto(c.get("jugador_id"))}">', unsafe_allow_html=True)
            with col_b:
                st.button(
                    corto, key=f"chat_{cid}", on_click=cb_abrir_chat, args=(cid,), help=titulo,
                    type="primary" if cid == chat_activo else "secondary", width="stretch",
                )
            with col_c:
                if not c.get("pendiente"):
                    st.button("🗑", key=f"del_{cid}", on_click=cb_eliminar_chat, args=(cid,), help="Eliminar este chat")

    st.caption("💾 Los chats se guardan en `datos/conversaciones.json`.")

# ---------------------------------------------------------------------------
# NAVEGACIÓN + DISTRIBUCIÓN CENTRAL / DERECHA
# ---------------------------------------------------------------------------
with st.container(key="nav_secciones"):
    seccion = st.radio("Sección", SECCIONES, horizontal=True, key="seccion", label_visibility="collapsed")

col_centro, col_der = st.columns([3.15, 1.25], gap="medium")

# ---------------------------------------------------------------------------
# PANEL DERECHO · Configuración del agente
# ---------------------------------------------------------------------------
with col_der:
    with st.container(key="panel_der"):
        st.markdown('<div class="panel-title">CONFIGURACIÓN DEL AGENTE</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-label">Selección de modelo</div>', unsafe_allow_html=True)
        modelo_defecto = os.getenv("DEFAULT_MODEL", "gemini-3.1-flash-lite")
        etiquetas_modelo = list(MODELOS.keys())
        idx_modelo = next((i for i, v in enumerate(MODELOS.values()) if v == modelo_defecto), 0)
        etiqueta_modelo = st.selectbox(
            "Modelo", etiquetas_modelo, index=idx_modelo, key="modelo_sel", label_visibility="collapsed"
        )
        modelo = MODELOS[etiqueta_modelo]

        with st.expander("🔑 Credenciales de API (opcional)"):
            api_key_input = st.text_input("API Key (Gemini / OpenAI)", type="password", placeholder="AQ… / AIza… / sk-…")
            if api_key_input:
                if api_key_input.startswith("AQ.") or api_key_input.startswith("AIza"):
                    os.environ["GEMINI_API_KEY"] = api_key_input
                    os.environ["GOOGLE_API_KEY"] = api_key_input
                    st.caption("✅ Clave Gemini configurada en la sesión.")
                else:
                    os.environ["OPENAI_API_KEY"] = api_key_input
                    st.caption("✅ Clave OpenAI configurada en la sesión.")
            else:
                st.caption("✅ Clave cargada desde variable de entorno (.env).")

        st.markdown('<div class="panel-label">4 ligas principales</div>', unsafe_allow_html=True)
        ligas_activas = []
        for clave, info in visual.LIGAS.items():
            c1, c2, c3 = st.columns([1, 4, 1.2])
            with c1:
                st.markdown(visual.img_escudo(clave, "crest lg"), unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="liga-row-name">{esc(info["nombre"])}</div>', unsafe_allow_html=True)
            with c3:
                if st.checkbox(info["nombre"], value=True, key=f"liga_{clave}", label_visibility="collapsed"):
                    ligas_activas.append(clave)

        st.markdown('<div class="panel-label">Filtros activos</div>', unsafe_allow_html=True)
        clubes_sel = st.multiselect(
            "Clubes", list(visual.CLUBES.keys()), format_func=lambda k: visual.CLUBES[k],
            key="filtro_clubes", placeholder="Todos los clubes", label_visibility="collapsed",
        )
        if clubes_sel:
            st.markdown(
                "".join(f'<span class="chip-club">{visual.img_escudo(k)} {esc(visual.CLUBES[k])}</span>' for k in clubes_sel),
                unsafe_allow_html=True,
            )

        def jugador_visible(jid):
            ligas_j = set(visual.ligas_de(jid))
            clubes_j = set(visual.clubes_de(jid))
            if len(ligas_activas) < len(visual.LIGAS) and not (ligas_j & set(ligas_activas)):
                return False
            if clubes_sel and not (clubes_j & set(clubes_sel)):
                return False
            return True

        visibles = [jid for jid in IDS if jugador_visible(jid)]
        actual = st.session_state.get("sel_jugador", IDS[0])
        opciones_jug = visibles if actual in visibles else [actual] + visibles

        st.markdown('<div class="panel-label">Futbolista</div>', unsafe_allow_html=True)
        jugador_id = st.selectbox(
            "Futbolista", opciones_jug, key="sel_jugador",
            format_func=lambda j: f"{nombre_de(j)} · {JUG[j]['pais']}", label_visibility="collapsed",
        )
        st.caption(f"{len(visibles)} de {len(IDS)} futbolistas con los filtros actuales")
        jugador_actual = JUG[jugador_id]

        escudos_liga = "".join(visual.img_escudo(k) for k in visual.ligas_de(jugador_id))
        st.markdown(
            limpiar_html(f"""
            <div class="player-card">
                <img class="pc-photo" src="{foto(jugador_id)}" alt="{esc(jugador_actual['nombre'])}">
                <div>
                    <div class="pc-name">{esc(jugador_actual['nombre'])}</div>
                    <div class="pc-meta">🌍 {esc(jugador_actual['pais'])}</div>
                    <div class="pc-meta">{escudos_liga} {esc(visual.etiqueta_ligas(jugador_id))}</div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        st.markdown('<div class="panel-label">Accesos rápidos</div>', unsafe_allow_html=True)
        col_qa1, col_qa2 = st.columns(2)
        with col_qa1:
            st.button(
                "📊 Standings",
                on_click=cb_prompt,
                args=(f"Muestra la tabla de posiciones y balance competitivo de las ligas donde juega {jugador_actual['nombre']}",),
                width="stretch", key="qa_standings",
            )
            st.button(
                "⭐ Top Scorers",
                on_click=cb_prompt,
                args=(f"¿Cuáles son los máximos goleadores históricos y el promedio anotador de {jugador_actual['nombre']}?",),
                width="stretch", key="qa_scorers",
            )
        with col_qa2:
            st.button(
                "📅 Fixtures",
                on_click=cb_prompt,
                args=(f"¿Cuáles son los próximos retos decisivos y fixture de temporada para {jugador_actual['nombre']}?",),
                width="stretch", key="qa_fixtures",
            )
            st.button(
                "🔄 Transfers",
                on_click=cb_prompt,
                args=(f"¿Cuáles han sido los fichajes y transferencias más costosas e influyentes en la trayectoria de {jugador_actual['nombre']}?",),
                width="stretch", key="qa_transfers",
            )

        st.button("📊 Ver opiniones guardadas", on_click=cb_ir_opiniones, args=(jugador_id,),
                  width="stretch", key="qa_ops")
        st.button("🏅 Ranking de futbolistas", on_click=cb_ir_ranking, width="stretch", key="qa_rank")
        _todas_ops = gestor_datos.cargar_opiniones()
        if _todas_ops:
            st.download_button(
                "⬇️ Exportar opiniones (CSV)",
                data=pd.DataFrame(_todas_ops).to_csv(index=False).encode("utf-8-sig"),
                file_name="opiniones_tribuna_global.csv", mime="text/csv",
                width="stretch", key="qa_csv",
            )


# ---------------------------------------------------------------------------
# Componentes de renderizado
# ---------------------------------------------------------------------------
def bullet_puntos_jugador(jid_target):
    base = motor_ia.BASE_JUGADORES.get(jid_target, {})
    rend = base.get("rendimiento_historico", "Rendimiento destacado en competencias de élite.")
    trofeos = base.get("titulos", [])
    t_str = ", ".join(trofeos[:2]) if trofeos else "Palmarés internacional destacado"
    ligas_str = visual.etiqueta_ligas(jid_target)
    return [
        f"<strong>Perfil táctico:</strong> {esc(rend)}.",
        f"<strong>Palmarés:</strong> {esc(t_str)}.",
        f"<strong>Competiciones:</strong> {esc(ligas_str)}.",
    ]


def render_mensaje(msg):
    jid = msg.get("jugador_id")
    nombre = msg.get("jugador_nombre") or nombre_de(jid)

    if msg.get("tipo") == "usuario":
        clubes_j = visual.clubes_de(jid)
        escudo_user = visual.img_escudo(clubes_j[0], "avatar-user") if clubes_j else f'<img class="avatar-user" src="{foto(jid)}" alt="{esc(nombre)}">'
        st.markdown(
            limpiar_html(
                f'<div class="msg-user-row"><div class="bubble-user">{esc(msg.get("contenido", ""))}</div>'
                f'{escudo_user}</div>'
            ),
            unsafe_allow_html=True,
        )
        return

    analisis_texto = msg.get("analisis", "")
    rendimiento_texto = msg.get("rendimiento", "")
    es_fuera_de_dominio = (
        msg.get("fuera_de_dominio")
        or "fuera del ámbito futbolístico" in rendimiento_texto.lower()
        or "exclusivamente para análisis futbolísticos" in analisis_texto.lower()
    )

    if es_fuera_de_dominio:
        st.markdown(
            limpiar_html(f"""
            <div class="msg-bot-row">
                <div class="bot-head">
                    <span class="bot-icon-glow">🤖</span>
                    <span class="bot-name">SOCCER AGENT</span>
                    <span class="pill pill-amarillo">⚠️ Solo Análisis Futbolístico</span>
                </div>
                <div class="bot-card border-amarillo">
                    <div class="analysis-text" style="font-size:.95rem;color:#fde047;line-height:1.6">
                        ⚽ {esc(analisis_texto)}
                    </div>
                    <div class="bot-foot">
                        <span>Ámbito del agente: <strong>Fútbol profesional</strong></span> ·
                        <span>Semáforo: <span class="pill pill-amarillo">🟡 Restringido</span></span>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        return

    color = msg.get("color_rendimiento", "verde")
    color = color if color in COLORES else "verde"
    comp_id = msg.get("jugador_comp_id")
    if not comp_id:
        texto_busqueda = f"{msg.get('analisis', '')} {msg.get('rendimiento', '')}"
        rival = motor_ia.detectar_jugador_comparado(texto_busqueda, jid)
        if rival:
            comp_id = id_por_nombre(rival.get("nombre", ""))

    escudos_liga = "".join(visual.img_escudo(k) for k in visual.ligas_de(jid))
    pill_liga = f'<span class="pill pill-liga">{escudos_liga} {esc(visual.etiqueta_ligas(jid))}</span>'
    rendimiento = msg.get("rendimiento", "")

    b1 = "".join(f"<li>{b}</li>" for b in bullet_puntos_jugador(jid))
    card_j1 = f"""
    <div class="player-card-split">
        <img class="pc-split-photo" src="{foto(jid)}" alt="{esc(nombre)}">
        <div class="pc-split-body">
            <div class="pc-split-name">{esc(nombre)}</div>
            <ul class="pc-split-bullets">{b1}</ul>
        </div>
    </div>
    """

    if comp_id and comp_id in JUG:
        nombre_2 = nombre_de(comp_id)
        b2 = "".join(f"<li>{b}</li>" for b in bullet_puntos_jugador(comp_id))
        card_j2 = f"""
        <div class="player-card-split">
            <img class="pc-split-photo" src="{foto(comp_id)}" alt="{esc(nombre_2)}">
            <div class="pc-split-body">
                <div class="pc-split-name">{esc(nombre_2)}</div>
                <ul class="pc-split-bullets">{b2}</ul>
            </div>
        </div>
        """
        cards_html = f'<div class="player-split-block">{card_j1}{card_j2}</div>'
        stats_widget = visual.generar_widget_stats(jid, comp_id, nombre, nombre_2)
    else:
        extra = f"<li><strong>Evaluación deportiva:</strong> {esc(rendimiento)}</li>" if rendimiento else ""
        card_j1_full = f"""
        <div class="player-card-split">
            <img class="pc-split-photo" src="{foto(jid)}" alt="{esc(nombre)}">
            <div class="pc-split-body">
                <div class="pc-split-name">{esc(nombre)}</div>
                <ul class="pc-split-bullets">{b1}{extra}</ul>
            </div>
        </div>
        """
        cards_html = f'<div class="player-split-block">{card_j1_full}</div>'
        stats_widget = visual.generar_widget_stats(jid, None, nombre, "")

    tipo_op = msg.get("tipo_opinion")
    if not tipo_op:
        s_base = msg.get("sentimiento", "neutral").lower()
        tipo_op = "buena" if s_base == "positivo" else ("mala" if s_base == "negativo" else "intermedia")

    TIPO_MAPA = {
        "buena": ("👍 Opinión: Buena", "pill-verde"),
        "mala": ("👎 Opinión: Mala", "pill-rojo"),
        "intermedia": ("⚖️ Opinión: Intermedia", "pill-amarillo")
    }
    etq_tipo, clase_tipo = TIPO_MAPA.get(tipo_op.lower(), ("⚖️ Opinión: Intermedia", "pill-amarillo"))
    pill_tipo = f'<span class="pill {clase_tipo}">{etq_tipo}</span>'

    contra = msg.get("contraargumento", "")
    contra_html = ""
    if contra and contra.strip():
        contra_html = f"""
        <div class="contra-box">
            <div class="contra-title">⚖️ Contraargumento de objetividad deportiva</div>
            <div class="contra-text">{esc(contra)}</div>
        </div>
        """

    st.markdown(
        limpiar_html(f"""
        <div class="msg-bot-row">
            <div class="bot-head">
                <span class="bot-icon-glow">🤖</span>
                <span class="bot-name">SOCCER AGENT</span>
                {pill_liga}
                {pill_tipo}
                <span class="pill pill-{color}">{ICONO_COLOR[color]} Rendimiento: {TEXTO_COLOR[color]}</span>
            </div>
            <div class="bot-card border-{color}">
                <div class="analysis-text">{esc(msg.get("analisis", ""))}</div>
                {contra_html}
                <div style="display:flex;gap:14px;align-items:stretch;flex-wrap:nowrap">
                    {cards_html}
                    {stats_widget}
                </div>
                <div class="bot-foot">
                    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                        {pill_tipo}
                        <span>Sentimiento: <strong>{esc(msg.get("sentimiento", "neutral"))}</strong></span> ·
                        <span class="pill pill-{color}">{ICONO_COLOR[color]} {TEXTO_COLOR[color]}</span>
                    </div>
                    <span>Registro <code>{esc(msg.get("id_registro", ""))}</code> · <span class="chat-action-link">Ver análisis completo ›</span></span>
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def procesar_mensaje(texto):
    """Analiza un mensaje del usuario con el motor de IA y lo guarda en el historial local."""
    if len(texto) < 5:
        st.warning("⚠️ La opinión es demasiado corta. Debe tener al menos 5 caracteres.")
        return
    if len(texto) > 1000:
        st.warning("⚠️ La opinión es demasiado larga. No puede superar los 1000 caracteres.")
        return

    with st.spinner("⚽ Analizando objetivamente con IA…"):
        if modelo == "__local__":
            resultado = motor_ia.analizar_heuristica_rapida(jugador_actual, texto)
        else:
            resultado = motor_ia.procesar_opinion(jugador=jugador_actual, opinion_usuario=texto, modelo=modelo)

    tipo_op = resultado.get("tipo_opinion")
    if not tipo_op:
        sent_calc = resultado.get("sentimiento", "neutral")
        tipo_op = "buena" if sent_calc == "positivo" else ("mala" if sent_calc == "negativo" else "intermedia")

    contra_calc = resultado.get("contraargumento", "")

    registro = gestor_datos.guardar_opinion(
        jugador_id=jugador_actual["id"],
        jugador_nombre=jugador_actual["nombre"],
        opinion_usuario=texto,
        sentimiento=resultado.get("sentimiento", "neutral"),
        analisis_objetivo=resultado.get("analisis_objetivo", ""),
        color_rendimiento=resultado.get("color_rendimiento", "verde"),
        titulos_relevantes=resultado.get("titulos_relevantes", []),
        evaluacion_rendimiento=resultado.get("evaluacion_rendimiento", ""),
        contraargumento=contra_calc,
        tipo_opinion=tipo_op
    )

    jugador_comp = motor_ia.detectar_jugador_comparado(texto, jugador_actual["id"])
    comp_id = id_por_nombre(jugador_comp["nombre"]) if jugador_comp else None

    st.session_state.mensajes.append({
        "tipo": "usuario", "jugador_id": jugador_actual["id"],
        "jugador_nombre": jugador_actual["nombre"], "contenido": texto,
    })
    mensaje_ia = {
        "tipo": "asistente", "jugador_id": jugador_actual["id"],
        "jugador_nombre": jugador_actual["nombre"],
        "sentimiento": resultado.get("sentimiento", "neutral"),
        "tipo_opinion": tipo_op,
        "color_rendimiento": resultado.get("color_rendimiento", "verde"),
        "analisis": resultado.get("analisis_objetivo", ""),
        "contraargumento": contra_calc,
        "rendimiento": resultado.get("evaluacion_rendimiento", ""),
        "titulos": resultado.get("titulos_relevantes", []),
        "id_registro": registro["id"],
    }
    if comp_id:
        mensaje_ia["jugador_comp_id"] = comp_id
    st.session_state.mensajes.append(mensaje_ia)

    previa = gestor_datos.obtener_conversacion_por_id(st.session_state.conv_activa_id)
    if previa and previa.get("titulo"):
        titulo_final = previa["titulo"]
    elif jugador_comp:
        titulo_final = f"{jugador_actual['nombre']} vs {jugador_comp['nombre']}"
    else:
        resumen = texto[:38] + ("…" if len(texto) > 38 else "")
        titulo_final = f"{jugador_actual['nombre']} · {resumen}"

    gestor_datos.guardar_conversacion(
        conv_id=st.session_state.conv_activa_id, titulo=titulo_final,
        jugador_id=jugador_actual["id"], jugador_nombre=jugador_actual["nombre"],
        mensajes=st.session_state.mensajes,
    )
    st.session_state.scroll_fin = True
    st.rerun()


def render_chat():
    conv = gestor_datos.obtener_conversacion_por_id(st.session_state.conv_activa_id)
    titulo = conv["titulo"] if conv and conv.get("titulo") else "Nueva conversación"
    st.markdown(
        limpiar_html(f"""
        <div class="chat-top">
            <div class="chat-top-left">
                <div class="bot-icon-glow">⚽</div>
                <div><div class="chat-title">SOCCER AGENT</div><div class="chat-sub">{esc(titulo)}</div></div>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
                <span class="pill pill-liga">● {esc(etiqueta_modelo)}</span>
                <span class="top-action-btn" title="Historial activo">⟳</span>
                <span class="top-action-btn" title="Exportar">↗</span>
                <span class="top-action-btn" title="Configuración">⚙</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    if not st.session_state.mensajes:
        nombre = jugador_actual["nombre"]
        st.markdown(
            limpiar_html(f"""
            <div class="empty-box">
                <img class="avatar-user" style="width:74px;height:74px;margin-bottom:8px" src="{foto(jugador_id)}" alt="{esc(nombre)}">
                <div style="font-size:1.05rem;font-weight:700;color:#fff">Nueva conversación sobre {esc(nombre)}</div>
                <div style="color:#8b98b3;font-size:.9rem;max-width:560px;margin:6px auto 0">
                    Escribe tu opinión, crítica o pregunta sobre <strong>{esc(nombre)}</strong>, o solicita
                    una comparativa indicando libremente con qué futbolistas deseas contrastarlo.
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        sugerencias = [
            f"¿Qué opinas del rendimiento de {nombre}?",
            f"¿Cuáles son los títulos y récords de {nombre}?",
            f"¿Cuáles son las fortalezas tácticas de {nombre}?",
        ]
        cols = st.columns(len(sugerencias))
        for i, (col, s) in enumerate(zip(cols, sugerencias)):
            with col:
                st.button(f"💡 {s}", key=f"sug_{i}", on_click=cb_prompt, args=(s,), width="stretch")

    for m in st.session_state.mensajes:
        render_mensaje(m)

    if st.session_state.pop("scroll_fin", False):
        script = (
            "<script>const d=window.parent.document;"
            "const el=d.querySelector('[data-testid=\"stMain\"]')||d.querySelector('section.main');"
            "if(el){el.scrollTo({top:el.scrollHeight,behavior:'smooth'});}</script>"
        )
        try:
            st.iframe(script, height=1)
        except Exception:
            components.html(script, height=0)


def render_opiniones():
    todas = gestor_datos.cargar_opiniones()
    tab_ops, tab_convs = st.tabs(["📊 Opiniones por futbolista", "💬 Conversaciones guardadas"])

    with tab_ops:
        f1, f2, f3, f4 = st.columns([1.6, 2.2, 1.2, 1.2])
        with f1:
            filtro_liga = st.selectbox(
                "🏆 Liga", ["todas"] + list(visual.LIGAS.keys()),
                format_func=lambda k: "Todas las ligas" if k == "todas" else visual.LIGAS[k]["nombre"],
            )
        ids_filtrables = [j for j in IDS if filtro_liga == "todas" or filtro_liga in visual.ligas_de(j)]
        if st.session_state.op_jugador not in ["todos"] + ids_filtrables:
            st.session_state.op_jugador = "todos"
        with f2:
            filtro_jugador = st.selectbox(
                "👤 Futbolista", ["todos"] + ids_filtrables, key="op_jugador",
                format_func=lambda j: "Todos los futbolistas" if j == "todos" else f"{nombre_de(j)} ({JUG[j]['pais']})",
            )
        with f3:
            filtro_tipo = st.selectbox("💬 Tipo de opinión", ["Todos", "Buena (elogio)", "Intermedia (balanceada)", "Mala (crítica)"])
        with f4:
            filtro_color = st.selectbox("🚦 Semáforo", ["Todos", *COLORES])

        filtradas = todas
        if filtro_liga != "todas":
            ids_set = set(ids_filtrables)
            filtradas = [o for o in filtradas if o.get("jugador_id") in ids_set]
        if filtro_jugador != "todos":
            filtradas = [o for o in filtradas if o.get("jugador_id") == filtro_jugador]
        if filtro_tipo != "Todos":
            if "Buena" in filtro_tipo:
                filtradas = [o for o in filtradas if o.get("tipo_opinion") == "buena" or o.get("sentimiento") == "positivo"]
            elif "Mala" in filtro_tipo:
                filtradas = [o for o in filtradas if o.get("tipo_opinion") == "mala" or o.get("sentimiento") == "negativo"]
            elif "Intermedia" in filtro_tipo:
                filtradas = [o for o in filtradas if o.get("tipo_opinion") == "intermedia" or o.get("sentimiento") == "neutral"]
        if filtro_color != "Todos":
            filtradas = [o for o in filtradas if o.get("color_rendimiento") == filtro_color]

        n_v = sum(1 for o in filtradas if o.get("color_rendimiento") == "verde")
        n_a = sum(1 for o in filtradas if o.get("color_rendimiento") == "amarillo")
        n_r = sum(1 for o in filtradas if o.get("color_rendimiento") == "rojo")
        metricas = [("Total de opiniones", len(filtradas)), ("🟢 Rendimiento alto", n_v),
                    ("🟡 Rendimiento regular", n_a), ("🔴 Rendimiento crítico", n_r)]
        for col, (etq, val) in zip(st.columns(4), metricas):
            with col:
                st.markdown(f'<div class="metric-card"><div class="mv">{val}</div><div class="ml">{etq}</div></div>',
                            unsafe_allow_html=True)

        if filtradas:
            g1, g2 = st.columns(2)
            with g1:
                st.caption("Distribución por semáforo (filtro activo)")
                st.bar_chart(pd.DataFrame({"Total": [n_v, n_a, n_r]}, index=["🟢 Verde", "🟡 Amarillo", "🔴 Rojo"]),
                             color="#238636")
            with g2:
                st.caption("Distribución por sentimiento (filtro activo)")
                cuentas = [sum(1 for o in filtradas if o.get("sentimiento") == s) for s in ("positivo", "neutral", "negativo")]
                st.bar_chart(pd.DataFrame({"Total": cuentas}, index=["👍 Positivo", "⚖️ Neutral", "👎 Negativo"]),
                             color="#1f6feb")

            e1, e2 = st.columns(2)
            with e1:
                st.download_button("📥 Descargar CSV", pd.DataFrame(filtradas).to_csv(index=False).encode("utf-8-sig"),
                                   "opiniones_filtradas.csv", "text/csv", width="stretch")
            with e2:
                st.download_button("📥 Descargar JSON",
                                   json.dumps({"opiniones": filtradas}, ensure_ascii=False, indent=2).encode("utf-8"),
                                   "opiniones_filtradas.json", "application/json", width="stretch")

        st.markdown("---")
        if not filtradas:
            st.info("No se encontraron opiniones con los filtros seleccionados.")
        else:
            limite = st.session_state.op_limite
            st.markdown(f"**Mostrando {min(limite, len(filtradas))} de {len(filtradas)} opiniones**")
            for o in filtradas[:limite]:
                color = o.get("color_rendimiento", "verde")
                color = color if color in COLORES else "verde"
                jid = o.get("jugador_id")
                escudos = "".join(visual.img_escudo(k) for k in visual.ligas_de(jid))
                titulos = "".join(f'<span class="trophy-badge">🏆 {esc(t)}</span>' for t in o.get("titulos_relevantes", [])[:3])
                
                top = o.get("tipo_opinion")
                if not top:
                    s_val = o.get("sentimiento", "neutral").lower()
                    top = "buena" if s_val == "positivo" else ("mala" if s_val == "negativo" else "intermedia")
                pill_clase = "pill-verde" if top == "buena" else ("pill-rojo" if top == "mala" else "pill-amarillo")
                pill_icono = "👍" if top == "buena" else ("👎" if top == "mala" else "⚖️")
                pill_tipo_op = f'<span class="pill {pill_clase}">{pill_icono} {top.upper()}</span>'

                contra_text = o.get("contraargumento", "")
                contra_markup = f'<div class="contra-box" style="margin:8px 0 6px;padding:8px 12px"><div class="contra-title" style="font-size:0.72rem">⚖️ Contraargumento de objetividad</div><div class="contra-text" style="font-size:0.83rem">{esc(contra_text)}</div></div>' if contra_text else ""

                st.markdown(
                    limpiar_html(f"""
                    <div class="op-card border-{color}">
                        <img class="op-photo" src="{foto(jid)}" alt="{esc(o.get('jugador_nombre'))}">
                        <div style="flex:1;min-width:0">
                            <div class="op-head">
                                <span class="op-name">{esc(o.get('jugador_nombre'))}</span>
                                {pill_tipo_op}
                                <span class="pill pill-{color}">{ICONO_COLOR[color]} {TEXTO_COLOR[color]}</span>
                                <span class="pill pill-liga">{escudos} {esc(o.get('sentimiento', '').upper())}</span>
                            </div>
                            <div class="op-quote">“{esc(o.get('opinion_usuario'))}”</div>
                            <div class="op-text">{esc(o.get('analisis_objetivo'))}</div>
                            {contra_markup}
                            <div style="margin-top:6px">{titulos}</div>
                            <div class="op-meta">{esc(o.get('timestamp', '')[:16].replace('T', ' '))} · ID {esc(o.get('id', '')[:8])}</div>
                        </div>
                    </div>
                    """),
                    unsafe_allow_html=True,
                )
            if len(filtradas) > limite:
                st.button("Cargar más opiniones", on_click=cb_mas_opiniones, key="btn_mas_ops")

    with tab_convs:
        convs = gestor_datos.cargar_conversaciones()
        if not convs:
            st.info("No hay conversaciones guardadas todavía.")
        for c in convs:
            with st.expander(f"💬 {c.get('titulo', 'Conversación')} ({len(c.get('mensajes', []))} mensajes)"):
                a, b = st.columns([3.6, 1.4])
                with a:
                    st.caption(f"ID: {c.get('id')} · Futbolista: {c.get('jugador_nombre')} · "
                               f"{fecha_de(c).strftime('%Y-%m-%d %H:%M')}")
                with b:
                    st.button("📂 Abrir este chat", key=f"abrir_{c['id']}", on_click=cb_abrir_chat,
                              args=(c["id"],), width="stretch")
                for m in c.get("mensajes", []):
                    if m.get("tipo") == "usuario":
                        st.markdown(f"**👤 Aficionado:** {m.get('contenido')}")
                    else:
                        st.markdown(f"**🤖 IA ({m.get('color_rendimiento', '').upper()}):** {m.get('analisis')}")


def render_ranking():
    todas = gestor_datos.cargar_opiniones()
    filas = []
    for j in catalogo:
        ops = [o for o in todas if o.get("jugador_id") == j["id"]]
        v = sum(1 for o in ops if o.get("color_rendimiento") == "verde")
        a = sum(1 for o in ops if o.get("color_rendimiento") == "amarillo")
        r = sum(1 for o in ops if o.get("color_rendimiento") == "rojo")
        total = len(ops)
        indice = round((v * 100 + a * 50) / total) if total else 0
        filas.append({"id": j["id"], "nombre": j["nombre"], "pais": j["pais"], "total": total,
                      "v": v, "a": a, "r": r, "indice": indice})
    filas.sort(key=lambda f: (-f["indice"], -f["total"], f["nombre"]))

    st.markdown('<div class="chat-title" style="margin-bottom:2px">🏅 RANKING DE FUTBOLISTAS</div>'
                '<div class="chat-sub" style="margin-bottom:10px">Índice semafórico = (🟢×100 + 🟡×50 + 🔴×0) / total de opiniones</div>',
                unsafe_allow_html=True)

    medallas = ["🥇", "🥈", "🥉"]
    podio = "".join(
        f'<div class="podium-item {"p1" if i == 0 else ""}"><div class="podium-pos">{medallas[i]}</div>'
        f'<img src="{foto(f["id"])}" alt="{esc(f["nombre"])}"><div class="podium-name">{esc(f["nombre"])}</div>'
        f'<div class="pc-meta">{esc(f["pais"])}</div><div class="podium-score">{f["indice"]}%</div></div>'
        for i, f in enumerate(filas[:3])
    )
    st.markdown(f'<div class="podium">{podio}</div>', unsafe_allow_html=True)

    df = pd.DataFrame([{
        "Foto": foto(f["id"]), "Futbolista": f["nombre"], "País": f["pais"],
        "Ligas": visual.etiqueta_ligas(f["id"]), "Opiniones": f["total"],
        "🟢": f["v"], "🟡": f["a"], "🔴": f["r"], "Índice": f["indice"],
    } for f in filas])
    st.dataframe(
        df, hide_index=True, width="stretch", row_height=58,
        column_config={
            "Foto": st.column_config.ImageColumn("Foto", width="small"),
            "Índice": st.column_config.ProgressColumn("Índice semafórico", min_value=0, max_value=100, format="%d%%"),
        },
    )


# ---------------------------------------------------------------------------
# PANEL CENTRAL
# ---------------------------------------------------------------------------
with col_centro:
    with st.container(key="panel_centro"):
        if seccion == SECCIONES[0]:
            render_chat()
        elif seccion == SECCIONES[1]:
            render_opiniones()
        else:
            render_ranking()

# Entrada de chat fija en la parte inferior (solo en la sección Chat)
if seccion == SECCIONES[0]:
    entrada = st.chat_input("Escribe tu opinión o pregunta sobre el jugador (5 a 1000 caracteres)…")
    texto_usuario = entrada or st.session_state.pop("prompt_rapido", None)
    if texto_usuario:
        procesar_mensaje(texto_usuario.strip())

