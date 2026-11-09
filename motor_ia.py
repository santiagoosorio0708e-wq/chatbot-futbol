"""Motor de Inteligencia Artificial para análisis futbolístico y clasificación semafórica.
Soporta modelos de Google Gemini (SDK google-genai) y OpenAI con salida JSON estructurada y temperatura 0.
"""
import json
import os
import re
import unicodedata
import concurrent.futures
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Base de conocimiento enriquecida para los 20 jugadores oficiales
BASE_JUGADORES = {
    "j001": {
        "nombre": "Lionel Messi",
        "pais": "Argentina",
        "titulos": ["Copa del Mundo 2022", "8 Balones de Oro", "4 UEFA Champions League", "2 Copas América"],
        "rendimiento_historico": "Sobresaliente / Leyenda Absoluta",
        "color_default": "verde"
    },
    "j002": {
        "nombre": "Cristiano Ronaldo",
        "pais": "Portugal",
        "titulos": ["5 UEFA Champions League", "5 Balones de Oro", "Eurocopa 2016", "Máximo goleador histórico del fútbol profesional"],
        "rendimiento_historico": "Sobresaliente / Goleador Histórico",
        "color_default": "verde"
    },
    "j003": {
        "nombre": "Neymar",
        "pais": "Brasil",
        "titulos": ["Copa Libertadores con Santos", "UEFA Champions League con Barcelona", "Oro Olímpico Río 2016", "Máximo goleador con Brasil"],
        "rendimiento_historico": "Alto pero condicionado por lesiones recurrentes",
        "color_default": "amarillo"
    },
    "j004": {
        "nombre": "Kylian Mbappé",
        "pais": "Francia",
        "titulos": ["Copa del Mundo 2018", "Bota de Oro Mundial 2022", "Múltiples Ligue 1", "UEFA Nations League 2021"],
        "rendimiento_historico": "Élite mundial con velocidad y definición descomunales",
        "color_default": "verde"
    },
    "j005": {
        "nombre": "Erling Haaland",
        "pais": "Noruega",
        "titulos": ["UEFA Champions League (Triplete con Man City)", "Bota de Oro Europea", "Premier League"],
        "rendimiento_historico": "Goleador élite implacable en el área",
        "color_default": "verde"
    },
    "j006": {
        "nombre": "Vinícius Júnior",
        "pais": "Brasil",
        "titulos": ["2 UEFA Champions League (gol en final)", "LaLiga de España", "Mundial de Clubes de la FIFA"],
        "rendimiento_historico": "Extremo desequilibrante determinante en partidos grandes",
        "color_default": "verde"
    },
    "j007": {
        "nombre": "Mohamed Salah",
        "pais": "Egipto",
        "titulos": ["UEFA Champions League 2019", "Premier League", "3 Botas de Oro de Premier League"],
        "rendimiento_historico": "Constancia goleadora y asistencias de máximo nivel",
        "color_default": "verde"
    },
    "j008": {
        "nombre": "Robert Lewandowski",
        "pais": "Polonia",
        "titulos": ["UEFA Champions League 2020", "The Best FIFA (2 veces)", "Múltiples Bundesligas y LaLiga"],
        "rendimiento_historico": "Delantero centro de época y rematador letal",
        "color_default": "verde"
    },
    "j009": {
        "nombre": "Luka Modrić",
        "pais": "Croacia",
        "titulos": ["6 UEFA Champions League", "Balón de Oro 2018", "Subcampeón del Mundo 2018 y Bronce 2022"],
        "rendimiento_historico": "Director de orquesta insustituible y vigencia legendaria",
        "color_default": "verde"
    },
    "j010": {
        "nombre": "Kevin De Bruyne",
        "pais": "Bélgica",
        "titulos": ["UEFA Champions League (Triplete)", "Múltiples Premier League", "Máximo asistente europeo"],
        "rendimiento_historico": "Visión de juego y precisión de pase top del siglo XXI",
        "color_default": "verde"
    },
    "j011": {
        "nombre": "Luis Suárez",
        "pais": "Uruguay",
        "titulos": ["Copa América 2011", "UEFA Champions League 2015", "2 Botas de Oro europeas"],
        "rendimiento_historico": "Delantero centro feroz y letal",
        "color_default": "verde"
    },
    "j012": {
        "nombre": "James Rodríguez",
        "pais": "Colombia",
        "titulos": ["Bota de Oro Mundial 2014", "2 UEFA Champions League", "Mejor jugador Copa América 2024"],
        "rendimiento_historico": "Talento técnico exquisito, a veces intermitente a nivel de clubes",
        "color_default": "amarillo"
    },
    "j013": {
        "nombre": "Luis Díaz",
        "pais": "Colombia",
        "titulos": ["FA Cup", "Carabao Cup", "Goleador Copa América 2021", "Primeira Liga"],
        "rendimiento_historico": "Desborde vertical y sacrificio físico notable",
        "color_default": "verde"
    },
    "j014": {
        "nombre": "Son Heung-min",
        "pais": "Corea del Sur",
        "titulos": ["Bota de Oro Premier League 2021-22", "Juegos Asiáticos Oro"],
        "rendimiento_historico": "Atacante versátil con gran pegada ambidiestra pero pocos títulos colectivos",
        "color_default": "amarillo"
    },
    "j015": {
        "nombre": "Sadio Mané",
        "pais": "Senegal",
        "titulos": ["Copa Africana de Naciones 2021", "UEFA Champions League 2019", "Premier League"],
        "rendimiento_historico": "Líder ofensivo, potencia y títulos continentales",
        "color_default": "verde"
    },
    "j016": {
        "nombre": "Pelé",
        "pais": "Brasil",
        "titulos": ["3 Copas del Mundo (1958, 1962, 1970)", "2 Copas Libertadores e Intercontinentales", "Más de 1000 goles"],
        "rendimiento_historico": "Rey del fútbol y pionero indiscutible",
        "color_default": "verde"
    },
    "j017": {
        "nombre": "Diego Maradona",
        "pais": "Argentina",
        "titulos": ["Copa del Mundo 1986", "2 Scudettos históricos con Napoli", "Copa UEFA"],
        "rendimiento_historico": "Genio inmortal, trascendencia absoluta con su selección",
        "color_default": "verde"
    },
    "j018": {
        "nombre": "Zinedine Zidane",
        "pais": "Francia",
        "titulos": ["Copa del Mundo 1998", "Eurocopa 2000", "UEFA Champions League 2002 (gol icónico)", "Balón de Oro"],
        "rendimiento_historico": "Elegancia, pausa y determinación en las finales más trascendentes",
        "color_default": "verde"
    },
    "j019": {
        "nombre": "Ronaldinho",
        "pais": "Brasil",
        "titulos": ["Copa del Mundo 2002", "UEFA Champions League 2006", "Balón de Oro 2005", "Copa Libertadores 2013"],
        "rendimiento_historico": "Magia pura e inventiva que redefinió el fútbol mundial",
        "color_default": "verde"
    },
    "j020": {
        "nombre": "Ronaldo Nazário",
        "pais": "Brasil",
        "titulos": ["2 Copas del Mundo (1994, 2002)", "2 Balones de Oro", "Copa América (1997, 1999)"],
        "rendimiento_historico": "El Fenómeno, delantero más explosivo e imparable de su era",
        "color_default": "verde"
    }
}

ESQUEMA_JSON_DICT = {
    "type": "object",
    "properties": {
        "sentimiento": {
            "type": "string",
            "enum": ["positivo", "neutral", "negativo"],
            "description": "Sentimiento estimado de la opinión del usuario hacia el jugador."
        },
        "color_rendimiento": {
            "type": "string",
            "enum": ["verde", "amarillo", "rojo"],
            "description": "Semáforo objetivo de rendimiento y títulos (verde = alto/consagrado, amarillo = regular/en desarrollo/irregular, rojo = bajo/crítico)."
        },
        "analisis_objetivo": {
            "type": "string",
            "description": "Opinión futbolística objetiva e independiente que sintetiza el rendimiento real en cancha y títulos del jugador frente a lo expresado por el aficionado."
        },
        "evaluacion_rendimiento": {
            "type": "string",
            "description": "Síntesis del rendimiento y momento futbolístico del jugador."
        },
        "titulos_relevantes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lista de títulos clave ganados con club o selección."
        }
    },
    "required": ["sentimiento", "color_rendimiento", "analisis_objetivo", "evaluacion_rendimiento", "titulos_relevantes"]
}


def _normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar nombres de forma tolerante."""
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


# Palabras que aparecen en el nombre de más de un futbolista: se resuelven hacia el más conocido
_ALIAS_AMBIGUOS = {"ronaldo": "j002"}


def detectar_jugador_comparado(texto: str, jugador_actual_id: str) -> Optional[Dict[str, Any]]:
    """Detecta si en la consulta se menciona a otro futbolista para realizar una comparativa.

    1) Busca primero el nombre completo (p. ej. 'Ronaldo Nazário' o 'Cristiano Ronaldo').
    2) Luego busca palabras características del nombre (p. ej. 'Cristiano', 'Mbappé', 'Messi'),
       ignorando las ambiguas que comparten varios jugadores (p. ej. 'Luis').
    """
    texto_n = _normalizar(texto)
    palabras_texto = set(re.findall(r"[a-z0-9]+", texto_n))
    otros = {j_id: info for j_id, info in BASE_JUGADORES.items() if j_id != jugador_actual_id}

    # Pasada 1: nombre completo
    for info in otros.values():
        if _normalizar(info["nombre"]) in texto_n:
            return info

    # Palabras del jugador actual (no cuentan como mención de otro jugador)
    propias = set(_normalizar(BASE_JUGADORES.get(jugador_actual_id, {}).get("nombre", "")).split())

    # Conteo de en cuántos nombres aparece cada palabra
    frecuencia: Dict[str, int] = {}
    for info in BASE_JUGADORES.values():
        for p in set(_normalizar(info["nombre"]).split()):
            frecuencia[p] = frecuencia.get(p, 0) + 1

    # Pasada 2: palabra característica
    for j_id, info in otros.items():
        for p in _normalizar(info["nombre"]).split():
            if len(p) < 4 or p in propias or p not in palabras_texto:
                continue
            if frecuencia.get(p, 0) > 1:
                alias = _ALIAS_AMBIGUOS.get(p)
                if alias and alias in otros:
                    return otros[alias]
                continue
            return info
    return None


def analizar_con_gemini(
    jugador: Dict[str, str],
    opinion_usuario: str,
    modelo: str = "gemini-3.1-flash-lite"
) -> Dict[str, Any]:
    """Ejecuta el análisis llamando a Google Gemini con temperatura 0 y JSON Schema."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Clave GEMINI_API_KEY no encontrada")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    
    info_jugador = BASE_JUGADORES.get(jugador.get("id"), {})
    titulos_ref = ", ".join(info_jugador.get("titulos", []))

    # Detectar si hay un futbolista de comparación
    jugador_comp = detectar_jugador_comparado(opinion_usuario, jugador.get("id"))
    prompt_comparativo = ""
    if jugador_comp:
        titulos_comp = ", ".join(jugador_comp.get("titulos", []))
        prompt_comparativo = (
            f"\nFutbolista secundario detectado para comparación: {jugador_comp['nombre']} ({jugador_comp['pais']})\n"
            f"Títulos de referencia de {jugador_comp['nombre']}: {titulos_comp}\n"
            f"INSTRUCCIÓN DE COMPARACIÓN: El aficionado solicita contrastar a {jugador.get('nombre')} con {jugador_comp['nombre']}. "
            f"Tu análisis objetivo DEBE comparar el estilo, rendimiento en cancha y los títulos de ambos futbolistas.\n"
        )

    system_instruction = (
        "Eres el asistente y analista futbolístico experto del sistema 'Tribuna Global'. "
        "Tu misión es analizar la opinión o pregunta de un aficionado sobre un futbolista específico y generar "
        "una opinión 100% objetiva e imparcial sobre el jugador, basándote en su rendimiento en cancha "
        "y sus títulos obtenidos a nivel de clubes y selecciones. Si se pide una comparación con otro futbolista, "
        "debes contrastar objetivamente a ambos futbolistas destacando sus méritos deportivos.\n"
        "Reglas de semáforo (color_rendimiento):\n"
        "- verde: Jugador de alto rendimiento, palmarés exitoso o impacto sobresaliente en el campo.\n"
        "- amarillo: Jugador de rendimiento intermedio, intermitente o palmarés moderado.\n"
        "- rojo: Jugador con bajo rendimiento sostenido, críticas profundas o deficiencias tácticas.\n"
        "Reglas de sentimiento:\n"
        "- positivo: El aficionado elogia o destaca al jugador.\n"
        "- neutral: Opinión descriptiva, pregunta futbolística o comparativa equilibrada.\n"
        "- negativo: El aficionado critica, desmerece o ataca al jugador.\n"
        "Responde estrictamente en formato JSON."
    )

    prompt = (
        f"Futbolista principal: {jugador.get('nombre')} ({jugador.get('pais')})\n"
        f"Títulos de referencia: {titulos_ref}\n"
        f"{prompt_comparativo}"
        f"Consulta/Opinión del aficionado: \"{opinion_usuario}\"\n"
        f"Genera el análisis objetivo estructurado."
    )

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.0,
        response_mime_type="application/json",
        response_schema=ESQUEMA_JSON_DICT
    )

    # Intentar con el modelo especificado o fallback rápido dentro de Gemini
    modelos_a_probar = [modelo, "gemini-3.1-flash-lite", "gemini-3.5-flash-lite"]
    ultimo_error = None
    for m in modelos_a_probar:
        try:
            nombre_m = m.replace("models/", "")
            response = client.models.generate_content(
                model=nombre_m,
                contents=prompt,
                config=config
            )
            return json.loads(response.text)
        except Exception as e:
            ultimo_error = e
            continue
            
    raise ultimo_error or RuntimeError("No se pudo completar la llamada con Gemini")


def analizar_con_openai(
    jugador: Dict[str, str],
    opinion_usuario: str,
    modelo: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """Ejecuta el análisis llamando al modelo OpenAI con temperatura 0 y JSON Schema."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no encontrada")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    info_jugador = BASE_JUGADORES.get(jugador.get("id"), {})
    titulos_texto = ", ".join(info_jugador.get("titulos", []))

    system_prompt = (
        "Eres el asistente y analista futbolístico experto del sistema 'Tribuna Global'. "
        "Tu misión es analizar la opinión de un aficionado sobre un futbolista específico y generar "
        "una opinión 100% objetiva e imparcial sobre el jugador, basándote en su rendimiento en cancha "
        "y sus títulos obtenidos a nivel de clubes y selecciones.\n"
        "Reglas de semáforo (color_rendimiento):\n"
        "- verde: Jugador de alto rendimiento, palmarés exitoso o impacto sobresaliente en el campo.\n"
        "- amarillo: Jugador de rendimiento intermedio, intermitente o palmarés moderado.\n"
        "- rojo: Jugador con bajo rendimiento sostenido, críticas profundas o deficiencias tácticas.\n"
        "Reglas de sentimiento:\n"
        "- positivo: El aficionado elogia o destaca al jugador.\n"
        "- neutral: Opinión descriptiva, ambigua o equilibrada.\n"
        "- negativo: El aficionado critica, desmerece o ataca al jugador.\n"
        "Debes responder estrictamente en formato JSON según el esquema indicado."
    )

    user_prompt = (
        f"Futbolista: {jugador.get('nombre')} ({jugador.get('pais')})\n"
        f"Palmarés de referencia: {titulos_texto}\n"
        f"Opinión del aficionado: \"{opinion_usuario}\"\n"
        f"Por favor realiza el análisis estructurado objetivo."
    )

    esquema_openai = {
        "type": "json_schema",
        "json_schema": {
            "name": "analisis_opinion_futbol",
            "strict": True,
            "schema": {**ESQUEMA_JSON_DICT, "additionalProperties": False}
        }
    }

    response = client.chat.completions.create(
        model=modelo,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=esquema_openai
    )

    contenido = response.choices[0].message.content
    return json.loads(contenido)


def analizar_heuristica_rapida(
    jugador: Dict[str, str],
    opinion_usuario: str
) -> Dict[str, Any]:
    """
    Motor local de alta velocidad. Proporciona análisis futbolístico objetivo
    incluso si no hay conexión a internet o cuota de API.
    """
    texto = opinion_usuario.lower()
    
    frases_negativas = [
        "no es tan bueno", "no es bueno", "no me parece bueno", "no rinde", 
        "no sirve", "no me gusta", "pecho frio", "sobre valorado", "sobrevalorado",
        "muy malo", "bastante malo"
    ]
    palabras_negativas = [
        "malo", "pesimo", "pésimo", "tronco", "fracaso", "desastre", "paquete", "odio", 
        "horrible", "mediocre", "inflado", "limitado"
    ]
    
    score_neg = 0
    texto_limpio = texto
    for fn in frases_negativas:
        if fn in texto_limpio:
            score_neg += 2
            texto_limpio = texto_limpio.replace(fn, " ")

    palabras_positivas = [
        "excelente", "crack", "mejor", "bueno", "increible", "increíble", "genio", 
        "idolo", "ídolo", "goleador", "leyenda", "fenomenal", "top", "grande", 
        "capo", "magia", "espectacular", "determinante", "figura"
    ]
    
    score_pos = sum(1 for p in palabras_positivas if re.search(rf"\b{re.escape(p)}\b", texto_limpio))
    score_neg += sum(1 for n in palabras_negativas if re.search(rf"\b{re.escape(n)}\b", texto_limpio))
    
    if score_neg > score_pos:
        sentimiento = "negativo"
    elif score_pos > score_neg:
        sentimiento = "positivo"
    else:
        sentimiento = "neutral"

    info = BASE_JUGADORES.get(jugador.get("id"), {
        "titulos": ["Títulos nacionales e internacionales"],
        "rendimiento_historico": "Jugador profesional de alto rendimiento",
        "color_default": "verde"
    })

    nombre = jugador.get("nombre", "el jugador")
    pais = jugador.get("pais", "su país")
    titulos = info.get("titulos", [])
    titulos_str = ", ".join(titulos[:3])
    color = info.get("color_default", "verde")

    # Si se detecta un futbolista secundario para comparar
    jugador_comp = detectar_jugador_comparado(opinion_usuario, jugador.get("id"))
    if jugador_comp:
        nombre2 = jugador_comp["nombre"]
        pais2 = jugador_comp["pais"]
        info2 = jugador_comp
        titulos2_str = ", ".join(info2.get("titulos", [])[:2])
        analisis = (
            f"Análisis comparativo objetivo entre {nombre} y {nombre2}: "
            f"{nombre} ({pais}) se distingue por {info.get('rendimiento_historico', 'su rendimiento de élite')} "
            f"con títulos de referencia como {titulos_str}. Por su parte, {nombre2} ({pais2}) "
            f"destaca por {info2.get('rendimiento_historico', 'su gran nivel competitivo')} con trofeos destacados como {titulos2_str}. "
            f"Ambos futbolistas aportan perfiles contrastados y de máxima jerarquía en el fútbol mundial."
        )
        titulos_comb = titulos[:2] + [f"{nombre2}: {t}" for t in info2.get("titulos", [])[:2]]
        eval_rend = f"Comparativa de élite: {nombre} vs {nombre2}"
        color_comp = "verde" if (info.get("color_default") == "verde" or info2.get("color_default") == "verde") else "amarillo"
        return {
            "sentimiento": "neutral",
            "color_rendimiento": color_comp,
            "analisis_objetivo": analisis,
            "evaluacion_rendimiento": eval_rend,
            "titulos_relevantes": titulos_comb
        }
    
    if sentimiento == "negativo":
        analisis = (
            f"La opinión expresa una crítica o reparo hacia {nombre}. Sin embargo, desde una perspectiva objetiva, "
            f"el rendimiento de {nombre} en la cancha está respaldado por logros contundentes con {pais} y sus clubes, "
            f"incluyendo: {titulos_str}. Su impacto deportivo desmiente juicios infundados."
        )
    elif sentimiento == "positivo":
        analisis = (
            f"La opinión elogia con fundamento a {nombre}. Los datos avalan esta percepción: su rendimiento en la cancha "
            f"ha sido clave en la conquista de trofeos de máxima jerarquía como {titulos_str}, "
            f"consolidándose como un referente para {pais}."
        )
    else:
        analisis = (
            f"La opinión sobre {nombre} plantea una perspectiva balanceada. Objetivamente, el balance de su carrera "
            f"demuestra regularidad competitiva y un palmarés que incluye {titulos_str}, "
            f"marcando presencia destacada tanto en clubes como representando a {pais}."
        )

    return {
        "sentimiento": sentimiento,
        "color_rendimiento": color,
        "analisis_objetivo": analisis,
        "evaluacion_rendimiento": info.get("rendimiento_historico", "Alto rendimiento deportivo"),
        "titulos_relevantes": titulos
    }


def ejecutar_con_timeout(fn, timeout_segundos: float = 5.0):
    """Ejecuta una función en un hilo con tiempo límite para evitar bloqueos."""
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    try:
        future = executor.submit(fn)
        return future.result(timeout=timeout_segundos)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def procesar_opinion(
    jugador: Dict[str, str],
    opinion_usuario: str,
    modelo: str = "gemini-3.1-flash-lite"
) -> Dict[str, Any]:
    """
    Punto de entrada principal para el análisis.
    1. Si hay clave Gemini (AQ... o AIza...), usa Google Gemini con JSON Schema protegido por timeout.
    2. Si hay clave OpenAI (sk-...), usa OpenAI con JSON Schema protegido por timeout.
    3. Si falla la llamada externa o excede 7 segundos, utiliza el motor heurístico local ultra rápido.
    """
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Si la clave configurada es de Gemini (empieza con AQ. o AIza)
    if gemini_key and (gemini_key.startswith("AQ.") or gemini_key.startswith("AIza") or "gemini" in modelo.lower()):
        try:
            return ejecutar_con_timeout(lambda: analizar_con_gemini(jugador, opinion_usuario, modelo=modelo), timeout_segundos=7.0)
        except Exception as e:
            print(f"Aviso: Contingencia activada en Gemini ({e}), usando motor heurístico inmediato.")
            return analizar_heuristica_rapida(jugador, opinion_usuario)

    # Si la clave configurada es de OpenAI
    if openai_key and openai_key.startswith("sk-"):
        try:
            return ejecutar_con_timeout(lambda: analizar_con_openai(jugador, opinion_usuario, modelo=modelo), timeout_segundos=7.0)
        except Exception as e:
            print(f"Aviso: Contingencia activada en OpenAI ({e}), usando motor heurístico inmediato.")
            return analizar_heuristica_rapida(jugador, opinion_usuario)

    # Fallback si no hay clave externa válida o en pruebas
    return analizar_heuristica_rapida(jugador, opinion_usuario)
