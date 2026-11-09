"""Pruebas unitarias automatizadas para Tribuna Global."""
import os
import json
import pytest
import gestor_datos
import motor_ia

def test_cargar_catalogo_jugadores():
    """Verifica que el catálogo oficial contenga 20 jugadores y formato válido."""
    jugadores = gestor_datos.cargar_catalogo_jugadores()
    assert len(jugadores) == 20, f"Se esperaban 20 jugadores, se obtuvieron {len(jugadores)}"
    
    # Comprobar estructura de cada registro
    for j in jugadores:
        assert "id" in j and j["id"].startswith("j")
        assert "nombre" in j and len(j["nombre"]) > 0
        assert "pais" in j and len(j["pais"]) > 0

def test_buscar_jugador_por_id():
    """Verifica la búsqueda por identificador estable."""
    messi = gestor_datos.buscar_jugador_por_id("j001")
    assert messi is not None
    assert messi["nombre"] == "Lionel Messi"
    assert messi["pais"] == "Argentina"

    vini = gestor_datos.buscar_jugador_por_id("j006")
    assert vini is not None
    assert vini["nombre"] == "Vinícius Júnior"
    assert vini["pais"] == "Brasil"

def test_analisis_heuristico_negativo():
    """Verifica la detección de opiniones críticas y el semáforo correspondiente."""
    vini = gestor_datos.buscar_jugador_por_id("j006")
    opinion = "Me parece que no es tan bueno porque es de brasil"
    resultado = motor_ia.analizar_heuristica_rapida(vini, opinion)
    
    assert resultado["sentimiento"] == "negativo"
    assert "Vinícius Júnior" in resultado["analisis_objetivo"]
    assert "titulos_relevantes" in resultado
    assert len(resultado["titulos_relevantes"]) > 0

def test_analisis_heuristico_positivo():
    """Verifica la detección de opiniones positivas."""
    messi = gestor_datos.buscar_jugador_por_id("j001")
    opinion = "Es el mejor de la historia, una leyenda indiscutible y crack total"
    resultado = motor_ia.analizar_heuristica_rapida(messi, opinion)
    
    assert resultado["sentimiento"] == "positivo"
    assert resultado["color_rendimiento"] == "verde"

def test_persistencia_opinion(monkeypatch, tmp_path):
    """Verifica que las opiniones se guarden y recuperen con UUID (en archivo temporal)."""
    monkeypatch.setattr(gestor_datos, "RUTA_OPINIONES", str(tmp_path / "opiniones.json"))
    vini = gestor_datos.buscar_jugador_por_id("j006")
    opinion_texto = "Prueba automatizada de opinión objetiva"
    
    registro = gestor_datos.guardar_opinion(
        jugador_id=vini["id"],
        jugador_nombre=vini["nombre"],
        opinion_usuario=opinion_texto,
        sentimiento="positivo",
        analisis_objetivo="Prueba de análisis objetivo",
        color_rendimiento="verde",
        titulos_relevantes=["Champions League"],
        evaluacion_rendimiento="Élite mundial"
    )
    
    assert "id" in registro
    assert len(registro["id"]) == 36  # Longitud estándar UUID4
    assert registro["jugador_id"] == "j006"
    assert registro["opinion_usuario"] == opinion_texto
    
    # Comprobar que aparece en la lista de opiniones filtradas
    opiniones_vini = gestor_datos.filtrar_opiniones_por_jugador("j006")
    encontrado = any(op["id"] == registro["id"] for op in opiniones_vini)
    assert encontrado, "El registro guardado no fue encontrado en la persistencia."


def test_deteccion_jugador_comparado_y_analisis(monkeypatch):
    """Verifica que el sistema detecte comparaciones entre dos futbolistas y no se bloquee."""
    for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)  # fuerza el motor heurístico local (sin red)
    messi = gestor_datos.buscar_jugador_por_id("j001")
    texto_consulta = "Dame una opinión sobre Messi y compáralo con Cristiano Ronaldo"
    
    jugador_comp = motor_ia.detectar_jugador_comparado(texto_consulta, "j001")
    assert jugador_comp is not None
    assert "Cristiano" in jugador_comp["nombre"]
    
    resultado = motor_ia.procesar_opinion(messi, texto_consulta)
    assert "analisis_objetivo" in resultado
    assert "Cristiano" in resultado["analisis_objetivo"] or "Ronaldo" in resultado["analisis_objetivo"]
    assert resultado["color_rendimiento"] in ["verde", "amarillo", "rojo"]


def test_persistencia_conversaciones_locales(monkeypatch, tmp_path):
    """Verifica la persistencia completa del historial de conversaciones (en archivo temporal)."""
    monkeypatch.setattr(gestor_datos, "RUTA_CONVERSACIONES", str(tmp_path / "conversaciones.json"))
    id_conv_prueba = "test-conv-1234"
    mensajes_prueba = [
        {"tipo": "usuario", "jugador_nombre": "Lionel Messi", "contenido": "¿Cuántas Champions tiene?"},
        {"tipo": "asistente", "jugador_nombre": "Lionel Messi", "analisis": "Tiene 4 Champions League."}
    ]
    
    guardado = gestor_datos.guardar_conversacion(
        conv_id=id_conv_prueba,
        titulo="Test Chat Messi",
        jugador_id="j001",
        jugador_nombre="Lionel Messi",
        mensajes=mensajes_prueba
    )
    
    assert guardado["id"] == id_conv_prueba
    assert len(guardado["mensajes"]) == 2
    
    # Recuperar por ID
    recuperado = gestor_datos.obtener_conversacion_por_id(id_conv_prueba)
    assert recuperado is not None
    assert recuperado["titulo"] == "Test Chat Messi"
    
    # Limpiar después del test
    gestor_datos.eliminar_conversacion(id_conv_prueba)
    assert gestor_datos.obtener_conversacion_por_id(id_conv_prueba) is None




def test_todos_los_jugadores_tienen_foto():
    """Cada uno de los 20 futbolistas debe tener su foto local en fotos/jXXX.*"""
    import visual
    for j in gestor_datos.cargar_catalogo_jugadores():
        assert visual._buscar(visual.RUTA_FOTOS, j["id"]), f"Falta la foto de {j['nombre']} ({j['id']})"
        assert visual.foto_jugador(j["id"], j["nombre"]).startswith("data:image/")


def test_escudos_de_ligas_y_clubes():
    """Las 4 ligas y los clubes del filtro deben tener escudo local."""
    import visual
    for clave in list(visual.LIGAS) + list(visual.CLUBES):
        assert visual.escudo(clave), f"Falta el escudo de {clave}"


def test_metadatos_cubren_el_catalogo():
    """Todos los jugadores del catálogo tienen metadatos de ligas/clubes válidos."""
    import visual
    for j in gestor_datos.cargar_catalogo_jugadores():
        assert j["id"] in visual.META_JUGADORES
        assert all(k in visual.LIGAS for k in visual.ligas_de(j["id"]))
        assert all(k in visual.CLUBES for k in visual.clubes_de(j["id"]))


def test_deteccion_rivales_sin_ambiguedad():
    """Casos con nombres repetidos (Ronaldo/Ronaldinho, Luis) resuelven al jugador correcto."""
    d = motor_ia.detectar_jugador_comparado
    assert d("Compara a Ronaldinho con Ronaldo Nazário", "j019")["nombre"] == "Ronaldo Nazário"
    assert d("compara a messi con ronaldo", "j001")["nombre"] == "Cristiano Ronaldo"
    assert d("Compara a Luis Díaz con Son Heung-min", "j013")["nombre"] == "Son Heung-min"
    assert d("¿Qué opinas de este jugador?", "j001") is None
