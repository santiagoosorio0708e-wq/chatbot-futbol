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

def test_persistencia_opinion():
    """Verifica que las opiniones se guarden y recuperen con UUID."""
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

