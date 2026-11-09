"""Recursos visuales de Tribuna Global: fotos, escudos, metadatos de ligas/clubes y estilos CSS.

Las imágenes se leen de la carpeta local `fotos/` (jugadores) y `fotos/ligas/` (escudos),
por lo que la aplicación funciona sin conexión a internet.
"""
import base64
import html
import os
from functools import lru_cache
from typing import Dict, List

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_FOTOS = os.path.join(RUTA_BASE, "fotos")
RUTA_ESCUDOS = os.path.join(RUTA_FOTOS, "ligas")

# ---------------------------------------------------------------------------
# Ligas y clubes
# ---------------------------------------------------------------------------
LIGAS: Dict[str, Dict[str, str]] = {
    "premier": {"nombre": "Premier League", "emoji": "🏴󠁧󠁢󠁥󠁮󠁧󠁿"},
    "laliga": {"nombre": "LaLiga EA Sports", "emoji": "🇪🇸"},
    "seriea": {"nombre": "Serie A TIM", "emoji": "🇮🇹"},
    "bundesliga": {"nombre": "Bundesliga", "emoji": "🇩🇪"},
}

CLUBES: Dict[str, str] = {
    "real_madrid": "Real Madrid",
    "barcelona": "FC Barcelona",
    "man_city": "Manchester City",
    "man_united": "Manchester United",
    "liverpool": "Liverpool",
    "bayern": "Bayern München",
    "juventus": "Juventus",
    "napoli": "Napoli",
    "inter": "Inter de Milán",
    "milan": "AC Milan",
    "tottenham": "Tottenham",
}

# Ligas y clubes por los que ha pasado cada futbolista del catálogo oficial
META_JUGADORES: Dict[str, Dict[str, List[str]]] = {
    "j001": {"ligas": ["laliga"], "clubes": ["barcelona"]},
    "j002": {"ligas": ["premier", "laliga", "seriea"], "clubes": ["man_united", "real_madrid", "juventus"]},
    "j003": {"ligas": ["laliga"], "clubes": ["barcelona"]},
    "j004": {"ligas": ["laliga"], "clubes": ["real_madrid"]},
    "j005": {"ligas": ["premier", "bundesliga"], "clubes": ["man_city"]},
    "j006": {"ligas": ["laliga"], "clubes": ["real_madrid"]},
    "j007": {"ligas": ["premier", "seriea"], "clubes": ["liverpool"]},
    "j008": {"ligas": ["laliga", "bundesliga"], "clubes": ["barcelona", "bayern"]},
    "j009": {"ligas": ["laliga", "premier"], "clubes": ["real_madrid", "tottenham"]},
    "j010": {"ligas": ["premier", "bundesliga"], "clubes": ["man_city"]},
    "j011": {"ligas": ["laliga", "premier"], "clubes": ["barcelona", "liverpool"]},
    "j012": {"ligas": ["laliga", "bundesliga", "premier"], "clubes": ["real_madrid", "bayern"]},
    "j013": {"ligas": ["premier", "bundesliga"], "clubes": ["liverpool", "bayern"]},
    "j014": {"ligas": ["premier", "bundesliga"], "clubes": ["tottenham"]},
    "j015": {"ligas": ["premier", "bundesliga"], "clubes": ["liverpool", "bayern"]},
    "j016": {"ligas": [], "clubes": []},
    "j017": {"ligas": ["seriea", "laliga"], "clubes": ["napoli", "barcelona"]},
    "j018": {"ligas": ["seriea", "laliga"], "clubes": ["juventus", "real_madrid"]},
    "j019": {"ligas": ["laliga", "seriea"], "clubes": ["barcelona", "milan"]},
    "j020": {"ligas": ["laliga", "seriea"], "clubes": ["barcelona", "inter", "real_madrid", "milan"]},
}


def ligas_de(jugador_id: str) -> List[str]:
    return META_JUGADORES.get(jugador_id, {}).get("ligas", [])


def clubes_de(jugador_id: str) -> List[str]:
    return META_JUGADORES.get(jugador_id, {}).get("clubes", [])


def etiqueta_ligas(jugador_id: str) -> str:
    """Texto corto con las ligas del jugador, p. ej. 'LaLiga · Premier League'."""
    ligas = ligas_de(jugador_id)
    if not ligas:
        return "Leyenda histórica"
    return " · ".join(LIGAS[k]["nombre"] for k in ligas)


def esc(texto) -> str:
    """Escapa texto para incrustarlo de forma segura en HTML."""
    return html.escape(str(texto if texto is not None else ""), quote=True)


def limpiar_html(bloque: str) -> str:
    """Quita sangrías y líneas vacías para que Markdown no interprete el HTML como código."""
    return "\n".join(l.strip() for l in bloque.splitlines() if l.strip())


# ---------------------------------------------------------------------------
# Imágenes (data URI para incrustarlas directamente en el HTML)
# ---------------------------------------------------------------------------
def _mime(datos: bytes) -> str:
    if datos[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if datos[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if datos[:4] == b"RIFF":
        return "image/webp"
    if datos[:5] == b"<?xml" or datos[:4] == b"<svg":
        return "image/svg+xml"
    return "image/jpeg"


def _buscar(carpeta: str, clave: str):
    if not os.path.isdir(carpeta):
        return None
    for nombre in sorted(os.listdir(carpeta)):
        base, ext = os.path.splitext(nombre)
        if base == clave and ext.lower() in (".jpg", ".jpeg", ".png", ".webp", ".svg"):
            return os.path.join(carpeta, nombre)
    return None


def _a_data_uri(ruta: str) -> str:
    with open(ruta, "rb") as f:
        datos = f.read()
    return f"data:{_mime(datos)};base64,{base64.b64encode(datos).decode()}"


def _avatar_iniciales(nombre: str) -> str:
    """Avatar SVG con iniciales, usado si falta la foto del jugador."""
    partes = [p for p in nombre.replace("-", " ").split() if p]
    iniciales = "".join(p[0] for p in partes[:2]).upper() or "?"
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='200' height='240' viewBox='0 0 200 240'>"
        "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
        "<stop offset='0' stop-color='#1f6feb'/><stop offset='1' stop-color='#0b1a3d'/></linearGradient></defs>"
        "<rect width='200' height='240' fill='url(#g)'/>"
        f"<text x='100' y='140' font-family='Arial' font-size='72' font-weight='700' "
        f"fill='white' text-anchor='middle'>{html.escape(iniciales)}</text></svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@lru_cache(maxsize=64)
def foto_jugador(jugador_id: str, nombre: str = "") -> str:
    ruta = _buscar(RUTA_FOTOS, jugador_id)
    if ruta:
        try:
            return _a_data_uri(ruta)
        except OSError:
            pass
    return _avatar_iniciales(nombre or jugador_id)


@lru_cache(maxsize=64)
def escudo(clave: str) -> str:
    """Escudo de liga o club. Devuelve cadena vacía si no existe el archivo."""
    ruta = _buscar(RUTA_ESCUDOS, clave)
    if ruta:
        try:
            return _a_data_uri(ruta)
        except OSError:
            pass
    return ""


def img_escudo(clave: str, clase: str = "crest") -> str:
    src = escudo(clave)
    if src:
        return f'<img class="{clase}" src="{src}" alt="{esc(clave)}">'
    return f'<span class="{clase} crest-fallback">⚽</span>'


# Estadísticas oficiales y trayectoria para análisis comparativo de élite
STATS_JUGADORES: Dict[str, Dict[str, Any]] = {
    "j001": {"rating": 9.8, "goles": 845, "asistencias": 376, "partidos": 1070, "trofeos": 44, "forma": [9.4, 9.6, 9.5, 9.8, 9.7, 9.9]},
    "j002": {"rating": 9.7, "goles": 907, "asistencias": 254, "partidos": 1245, "trofeos": 35, "forma": [9.3, 9.5, 9.4, 9.7, 9.6, 9.8]},
    "j003": {"rating": 9.0, "goles": 439, "asistencias": 280, "partidos": 718, "trofeos": 28, "forma": [8.6, 8.8, 9.0, 8.9, 9.1, 9.2]},
    "j004": {"rating": 9.5, "goles": 332, "asistencias": 154, "partidos": 440, "trofeos": 19, "forma": [9.2, 9.4, 9.6, 9.5, 9.7, 9.8]},
    "j005": {"rating": 9.4, "goles": 260, "asistencias": 53, "partidos": 312, "trofeos": 12, "forma": [9.1, 9.3, 9.5, 9.4, 9.6, 9.7]},
    "j006": {"rating": 9.3, "goles": 115, "asistencias": 90, "partidos": 330, "trofeos": 13, "forma": [9.0, 9.2, 9.4, 9.3, 9.5, 9.6]},
    "j007": {"rating": 9.2, "goles": 350, "asistencias": 160, "partidos": 670, "trofeos": 10, "forma": [8.9, 9.1, 9.3, 9.2, 9.4, 9.5]},
    "j008": {"rating": 9.3, "goles": 650, "asistencias": 170, "partidos": 920, "trofeos": 29, "forma": [9.0, 9.2, 9.1, 9.4, 9.3, 9.5]},
    "j009": {"rating": 9.1, "goles": 110, "asistencias": 160, "partidos": 880, "trofeos": 30, "forma": [8.8, 9.0, 9.2, 9.1, 9.3, 9.4]},
    "j010": {"rating": 9.3, "goles": 170, "asistencias": 290, "partidos": 720, "trofeos": 22, "forma": [9.0, 9.2, 9.4, 9.3, 9.5, 9.6]},
    "j011": {"rating": 9.2, "goles": 560, "asistencias": 260, "partidos": 940, "trofeos": 25, "forma": [8.9, 9.1, 9.2, 9.1, 9.3, 9.4]},
    "j012": {"rating": 8.8, "goles": 150, "asistencias": 180, "partidos": 580, "trofeos": 24, "forma": [8.6, 8.8, 9.0, 8.8, 9.1, 9.2]},
    "j013": {"rating": 8.9, "goles": 110, "asistencias": 60, "partidos": 390, "trofeos": 9, "forma": [8.7, 8.9, 9.1, 9.0, 9.2, 9.3]},
    "j014": {"rating": 9.0, "goles": 240, "asistencias": 110, "partidos": 600, "trofeos": 4, "forma": [8.8, 8.9, 9.1, 9.0, 9.2, 9.3]},
    "j015": {"rating": 9.0, "goles": 230, "asistencias": 100, "partidos": 560, "trofeos": 11, "forma": [8.7, 8.9, 9.1, 9.0, 9.2, 9.3]},
    "j016": {"rating": 9.9, "goles": 1281, "asistencias": 360, "partidos": 1363, "trofeos": 37, "forma": [9.7, 9.8, 9.9, 9.9, 10.0, 10.0]},
    "j017": {"rating": 9.9, "goles": 357, "asistencias": 270, "partidos": 690, "trofeos": 12, "forma": [9.6, 9.8, 9.9, 9.9, 9.9, 10.0]},
    "j018": {"rating": 9.7, "goles": 156, "asistencias": 180, "partidos": 790, "trofeos": 16, "forma": [9.4, 9.6, 9.7, 9.7, 9.8, 9.9]},
    "j019": {"rating": 9.6, "goles": 320, "asistencias": 210, "partidos": 820, "trofeos": 14, "forma": [9.3, 9.5, 9.7, 9.6, 9.8, 9.9]},
    "j020": {"rating": 9.8, "goles": 414, "asistencias": 120, "partidos": 616, "trofeos": 19, "forma": [9.5, 9.7, 9.8, 9.8, 9.9, 10.0]},
}


def stats_de(jugador_id: str) -> Dict[str, Any]:
    return STATS_JUGADORES.get(
        jugador_id,
        {"rating": 9.0, "goles": 200, "asistencias": 80, "partidos": 400, "trofeos": 10, "forma": [8.8, 9.0, 9.1, 9.0, 9.2, 9.3]},
    )


def generar_sparkline_svg(valores: List[float], ancho: int = 240, alto: int = 56, color: str = "#22c55e") -> str:
    """Genera un gráfico SVG con área degradada y curva suave que replica el monitor táctico de la referencia."""
    if not valores or len(valores) < 2:
        return ""
    vmin = min(valores) - 0.2
    vmax = max(valores) + 0.2
    paso_x = ancho / (len(valores) - 1)
    puntos = []
    for i, v in enumerate(valores):
        x = i * paso_x
        y = alto - ((v - vmin) / (vmax - vmin) * (alto - 14) + 7)
        puntos.append((round(x, 1), round(y, 1)))

    d_line = "M " + " L ".join(f"{x},{y}" for x, y in puntos)
    d_area = f"{d_line} L {puntos[-1][0]},{alto} L {puntos[0][0]},{alto} Z"
    uid = color.replace("#", "")

    return (
        f'<svg width="100%" height="{alto}" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="none" '
        f'style="display:block;overflow:visible">'
        f'<defs><linearGradient id="sg_{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{color}" stop-opacity="0.45"/>'
        f'<stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>'
        f'</linearGradient></defs>'
        f'<path d="{d_area}" fill="url(#sg_{uid})"/>'
        f'<path d="{d_line}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="{puntos[-1][0]}" cy="{puntos[-1][1]}" r="4" fill="#ffffff" stroke="{color}" stroke-width="2"/>'
        f'</svg>'
    )


def generar_widget_stats(jid: str, comp_id: str = None, nombre_1: str = "", nombre_2: str = "") -> str:
    """Genera la tarjeta lateral con tabla de métricas y curva de rendimiento en vivo."""
    s1 = stats_de(jid)
    n1 = esc(nombre_1.split()[-1] if nombre_1 else jid)

    if comp_id and comp_id in STATS_JUGADORES:
        s2 = stats_de(comp_id)
        n2 = esc(nombre_2.split()[-1] if nombre_2 else comp_id)
        encabezado = f"<tr><th>Métrica</th><th>{n1}</th><th>{n2}</th></tr>"
        filas = f"""
        <tr><td class="st-lbl">Rating</td><td class="st-v hi">{s1['rating']}</td><td class="st-v hi">{s2['rating']}</td></tr>
        <tr><td class="st-lbl">Goles</td><td class="st-v">{s1['goles']}</td><td class="st-v">{s2['goles']}</td></tr>
        <tr><td class="st-lbl">Asistencias</td><td class="st-v">{s1['asistencias']}</td><td class="st-v">{s2['asistencias']}</td></tr>
        <tr><td class="st-lbl">Partidos</td><td class="st-v">{s1['partidos']}</td><td class="st-v">{s2['partidos']}</td></tr>
        <tr><td class="st-lbl">Trofeos</td><td class="st-v hi">🏆 {s1['trofeos']}</td><td class="st-v hi">🏆 {s2['trofeos']}</td></tr>
        """
        curva_label = f"{n1} vs {n2} · Forma reciente"
    else:
        encabezado = f"<tr><th>Métrica</th><th>{n1}</th></tr>"
        filas = f"""
        <tr><td class="st-lbl">Rating Global</td><td class="st-v hi">{s1['rating']} / 10</td></tr>
        <tr><td class="st-lbl">Goles Oficiales</td><td class="st-v">{s1['goles']}</td></tr>
        <tr><td class="st-lbl">Asistencias</td><td class="st-v">{s1['asistencias']}</td></tr>
        <tr><td class="st-lbl">Partidos</td><td class="st-v">{s1['partidos']}</td></tr>
        <tr><td class="st-lbl">Títulos Conquistados</td><td class="st-v hi">🏆 {s1['trofeos']}</td></tr>
        """
        curva_label = f"{n1} · Curva de Rendimiento"

    sparkline = generar_sparkline_svg(s1["forma"])

    return (
        f'<div class="stats-panel">'
        f'<table class="stats-table"><thead>{encabezado}</thead><tbody>{filas}</tbody></table>'
        f'<div class="stats-card-chart">'
        f'<div class="chart-header">'
        f'<span class="chart-title">{curva_label}</span>'
        f'<span class="chart-val">+{s1["rating"]} Élite</span>'
        f'</div>'
        f'{sparkline}'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Estilos CSS (réplica del estilo "Soccer AI Agent": oscuro, tarjetas y estadio)
# ---------------------------------------------------------------------------
CSS = """
<style>
/* ===== Fondo estilo estadio ===== */
.stApp {
    background:
        radial-gradient(1100px 420px at 50% 112%, rgba(34,139,69,.38), transparent 62%),
        radial-gradient(800px 360px at 88% -8%, rgba(31,111,235,.22), transparent 60%),
        radial-gradient(700px 300px at 8% 0%, rgba(20,184,166,.10), transparent 60%),
        #060a12;
    color: #e6edf3;
}
.stApp::before {
    content: "";
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px) 0 0 / 100% 120px,
        radial-gradient(circle at 50% 100%, transparent 140px, rgba(255,255,255,.03) 141px, transparent 143px);
    opacity: .6;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.1rem; padding-bottom: 5rem; max-width: 1500px; }

/* ===== Barra lateral izquierda (historial) ===== */
[data-testid="stSidebar"] {
    background: rgba(9,14,25,.92);
    border-right: 1px solid #172036;
}
[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { align-items: center; gap: .35rem; }
[data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left; justify-content: flex-start;
    background: #0f1729; border: 1px solid #1c2842; color: #d0d9e8;
    border-radius: 10px; padding: .45rem .7rem; font-size: .84rem;
}
[data-testid="stSidebar"] .stButton > button:hover { border-color: #2f6fe0; color: #fff; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1f6feb, #1553b8); border-color: #2f81f7; color: #fff; font-weight: 600;
}
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.brand-logo {
    width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 30% 30%, #fff, #c9d1d9 55%, #6e7681); font-size: 24px;
    box-shadow: 0 0 0 3px #1f6feb55;
}
.brand-text { line-height: 1.05; font-weight: 800; letter-spacing: .5px; color: #fff; font-size: 1.05rem; }
.brand-text span { color: #3fb950; }
.panel-title { font-size: .78rem; font-weight: 700; letter-spacing: 1.1px; color: #c9d1d9; margin: 6px 0 10px; }
.panel-label { font-size: .68rem; font-weight: 600; letter-spacing: 1px; color: #7d8aa5; margin: 14px 0 6px; text-transform: uppercase; }
.group-label { font-size: .68rem; font-weight: 600; letter-spacing: 1px; color: #6b7a99; margin: 14px 0 6px; text-transform: uppercase; }
.mini-avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; object-position: top; border: 1px solid #2a3a5c; display: block; }
.mini-avatar.square { border-radius: 8px; }

/* ===== Paneles (contenedores con key) ===== */
.st-key-panel_der, .st-key-panel_centro {
    background: rgba(12,19,34,.88); border: 1px solid #1a2744; border-radius: 16px; padding: 14px 16px;
    box-shadow: 0 10px 40px rgba(0,0,0,.35);
}
.st-key-panel_der .stButton > button, .st-key-panel_centro .stButton > button {
    background: #0f1729; border: 1px solid #1c2842; color: #d0d9e8; border-radius: 10px; font-size: .84rem;
}
.st-key-panel_der .stButton > button:hover, .st-key-panel_centro .stButton > button:hover { border-color: #2f6fe0; color: #fff; }
.st-key-panel_der [data-testid="stHorizontalBlock"] { align-items: center; gap: .4rem; }

/* ===== Navegación de secciones ===== */
.st-key-nav_secciones [role="radiogroup"] { gap: 6px; flex-wrap: wrap; }
.st-key-nav_secciones label {
    background: #0f1729; border: 1px solid #1c2842; border-radius: 999px; padding: 4px 16px; cursor: pointer;
}
.st-key-nav_secciones label:has(input:checked) { background: #1f6feb; border-color: #3b82f6; }
.st-key-nav_secciones label > div:first-child { display: none; }

/* ===== Cabecera del chat ===== */
.chat-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.chat-top-left { display: flex; align-items: center; gap: 10px; }
.bot-icon {
    width: 34px; height: 34px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 30% 30%, #fff, #c9d1d9 55%, #6e7681); font-size: 20px;
}
.bot-icon.blue { background: linear-gradient(135deg, #2f81f7, #1553b8); color: #fff; font-size: 17px; }
.chat-title { font-weight: 700; letter-spacing: .6px; color: #fff; font-size: .95rem; }
.chat-sub { font-size: .75rem; color: #7d8aa5; }

/* ===== Mensajes ===== */
.msg-user-row { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin: 14px 0; }
.bubble-user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; padding: 10px 16px;
    border-radius: 16px 16px 4px 16px; max-width: 72%; font-size: .93rem; line-height: 1.45;
    box-shadow: 0 4px 16px rgba(37,99,235,.35);
}
.avatar-user { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; object-position: top; border: 2px solid #2f81f7; }
.msg-bot-row { margin: 16px 0 22px; }
.bot-head { display: flex; align-items: center; gap: 9px; margin-bottom: 8px; flex-wrap: wrap; }
.bot-name { font-weight: 700; letter-spacing: .6px; font-size: .8rem; color: #e6edf3; }
.bot-card {
    background: linear-gradient(180deg, rgba(20,30,52,.95), rgba(14,22,40,.95));
    border: 1px solid #22304f; border-left: 4px solid #3b82f6; border-radius: 14px; padding: 16px;
    box-shadow: 0 8px 28px rgba(0,0,0,.35);
}
.bot-card.border-verde { border-left-color: #238636; }
.bot-card.border-amarillo { border-left-color: #d29922; }
.bot-card.border-rojo { border-left-color: #da3633; }
.bot-grid { display: flex; gap: 18px; align-items: flex-start; }
.bot-photos { display: flex; flex-direction: column; gap: 10px; flex: 0 0 auto; }
.player-photo { position: relative; width: 104px; }
.player-photo img {
    width: 104px; height: 126px; object-fit: cover; object-position: top; border-radius: 12px;
    border: 1px solid #2b3d66; display: block; background: #0b1326;
}
.player-photo .pp-name {
    font-size: .68rem; text-align: center; color: #b6c2db; margin-top: 4px; line-height: 1.15;
}
.bot-body { flex: 1 1 auto; min-width: 0; }
.analysis-text { color: #d5deed; font-size: .93rem; line-height: 1.6; margin-bottom: 12px; }
.eval-text { color: #8b98b3; font-size: .84rem; margin-bottom: 10px; }
.eval-text strong { color: #aebbd6; }
.trophy-badge {
    display: inline-block; background: #0f1a33; color: #79c0ff; padding: 3px 10px; border-radius: 999px;
    font-size: .74rem; margin: 0 6px 6px 0; border: 1px solid #243659;
}
.bot-foot { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 8px;
    border-top: 1px solid #1d2b49; font-size: .72rem; color: #6b7a99; }
.bot-foot code { color: #8b98b3; background: transparent; }

/* ===== Píldoras ===== */
.pill { display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 999px;
    font-size: .72rem; font-weight: 600; border: 1px solid transparent; }
.pill-verde { background: rgba(35,134,54,.18); color: #3fb950; border-color: #238636; }
.pill-amarillo { background: rgba(210,153,34,.18); color: #e3b341; border-color: #d29922; }
.pill-rojo { background: rgba(218,54,51,.18); color: #f85149; border-color: #da3633; }
.pill-liga { background: rgba(47,129,247,.14); color: #79b8ff; border-color: #1f4f9c; }
.crest { width: 18px; height: 18px; object-fit: contain; vertical-align: middle; }
.crest.lg { width: 26px; height: 26px; }
.crest-fallback { font-size: 14px; }

/* ===== Widget de estadísticas y curva táctica (estilo monitor táctico) ===== */
.stats-panel {
    background: #09101e; border: 1px solid #1a2744; border-radius: 12px; padding: 12px;
    flex: 0 0 250px; width: 250px; box-shadow: inset 0 0 20px rgba(0,0,0,.35);
}
.stats-table { width: 100%; border-collapse: collapse; font-size: .73rem; margin-bottom: 8px; }
.stats-table th { color: #79b8ff; text-align: left; padding: 3px 6px; font-weight: 700; border-bottom: 1px solid #1c2b4a; }
.stats-table td { padding: 4px 6px; border-bottom: 1px solid #142038; }
.stats-table td.st-lbl { color: #8b9bb4; font-weight: 500; }
.stats-table td.st-v { color: #fff; font-weight: 700; text-align: right; }
.stats-table td.st-v.hi { color: #3fb950; }
.stats-card-chart { background: #070c17; border: 1px solid #15223c; border-radius: 8px; padding: 8px; margin-top: 6px; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: .67rem; }
.chart-title { color: #7d8ea9; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
.chart-val { color: #3fb950; font-weight: 700; }

/* ===== Tarjetas de jugadores en el split del agente ===== */
.player-split-block { display: flex; flex-direction: column; gap: 10px; flex: 1 1 0; min-width: 0; }
.player-card-split {
    display: flex; gap: 14px; align-items: flex-start; background: rgba(13,22,40,.6);
    border: 1px solid #1c2b4a; border-radius: 12px; padding: 10px;
}
.pc-split-photo {
    width: 68px; height: 82px; object-fit: cover; object-position: top;
    border-radius: 10px; border: 1.5px solid #283e6b; flex: 0 0 68px;
}
.pc-split-body { flex: 1 1 auto; min-width: 0; }
.pc-split-name { font-size: .95rem; font-weight: 800; color: #fff; margin-bottom: 4px; }
.pc-split-bullets { margin: 0; padding-left: 16px; color: #cbd5e1; font-size: .83rem; line-height: 1.5; }
.pc-split-bullets li { margin-bottom: 3px; }

/* ===== Iconos de cabecera con brillo ===== */
.bot-icon-glow {
    width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    background: radial-gradient(circle at 35% 35%, #38bdf8, #1d4ed8 70%, #0c204d);
    box-shadow: 0 0 16px rgba(56,189,248,.65); font-size: 18px; color: #fff;
}
.top-action-btn {
    width: 32px; height: 32px; border-radius: 8px; display: inline-flex; align-items: center; justify-content: center;
    background: #0f182c; border: 1px solid #1e2c4d; color: #8fa3c7; font-size: 14px; cursor: pointer;
}
.check-circle-green {
    width: 20px; height: 20px; border-radius: 50%; background: #22c55e; color: #052e16;
    display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 900;
}
.chat-action-link {
    display: inline-block; color: #38bdf8; font-size: .78rem; font-weight: 600; text-decoration: none;
    margin-top: 10px; cursor: pointer;
}
.chat-action-link:hover { text-decoration: underline; color: #7dd3fc; }


/* ===== Panel derecho ===== */
.player-card { display: flex; gap: 12px; align-items: center; background: #0d1528; border: 1px solid #1c2a49;
    border-radius: 12px; padding: 10px; margin: 8px 0 12px; }
.player-card img.pc-photo { width: 64px; height: 76px; object-fit: cover; object-position: top; border-radius: 10px; border: 1px solid #2b3d66; }
.pc-name { font-weight: 700; color: #fff; font-size: .95rem; }
.pc-meta { font-size: .74rem; color: #8b98b3; margin-top: 2px; }
.liga-row-name { font-size: .86rem; color: #d0d9e8; }
.chip-club { display: inline-flex; align-items: center; gap: 6px; background: #0f1729; border: 1px solid #1c2842;
    border-radius: 999px; padding: 3px 10px 3px 6px; margin: 0 6px 6px 0; font-size: .78rem; color: #d0d9e8; }

/* ===== Tarjetas de opinión / ranking ===== */
.op-card { display: flex; gap: 14px; background: rgba(15,23,42,.9); border: 1px solid #1d2b49;
    border-left: 4px solid #3b82f6; border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }
.op-card.border-verde { border-left-color: #238636; }
.op-card.border-amarillo { border-left-color: #d29922; }
.op-card.border-rojo { border-left-color: #da3633; }
.op-card img.op-photo { width: 52px; height: 62px; object-fit: cover; object-position: top; border-radius: 9px; border: 1px solid #2b3d66; }
.op-head { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 4px; }
.op-name { font-weight: 700; color: #fff; font-size: .9rem; }
.op-quote { color: #e6edf3; font-style: italic; font-size: .88rem; margin: 2px 0 6px; }
.op-text { color: #9fb0cc; font-size: .82rem; line-height: 1.5; }
.op-meta { color: #5f6f8f; font-size: .7rem; margin-top: 6px; }
.metric-card { background: rgba(15,23,42,.9); border: 1px solid #1d2b49; border-radius: 12px; padding: 12px 14px; }
.metric-card .mv { font-size: 1.7rem; font-weight: 800; color: #fff; line-height: 1.1; }
.metric-card .ml { font-size: .74rem; color: #8b98b3; }
.podium { display: flex; gap: 14px; flex-wrap: wrap; margin: 6px 0 18px; }
.podium-item { flex: 1 1 180px; text-align: center; background: rgba(15,23,42,.9); border: 1px solid #1d2b49;
    border-radius: 14px; padding: 14px 10px; }
.podium-item.p1 { border-color: #d4a017; box-shadow: 0 0 24px rgba(212,160,23,.18); }
.podium-item img { width: 86px; height: 104px; object-fit: cover; object-position: top; border-radius: 12px; border: 2px solid #2b3d66; }
.podium-pos { font-size: 1.4rem; }
.podium-name { font-weight: 700; color: #fff; margin-top: 4px; }
.podium-score { color: #3fb950; font-weight: 700; font-size: .95rem; }
.empty-box { background: rgba(15,23,42,.7); border: 1px dashed #26365a; border-radius: 14px; padding: 26px; text-align: center; margin: 12px 0 18px; }

/* ===== Entrada de chat ===== */
[data-testid="stChatInput"] { background: #0c1322; border: 1px solid #22304f; border-radius: 14px; }
</style>
"""

