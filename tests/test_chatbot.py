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

