"""Módulo de gestión de datos para jugadores y persistencia de opiniones."""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_JUGADORES = os.path.join(RUTA_BASE, "datos", "jugadores.json")
RUTA_OPINIONES = os.path.join(RUTA_BASE, "datos", "opiniones.json")


def cargar_catalogo_jugadores() -> List[Dict[str, str]]:
    """Carga la lista de jugadores desde el archivo JSON oficial."""
    if not os.path.exists(RUTA_JUGADORES):
        return []
    try:
        with open(RUTA_JUGADORES, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("jugadores", [])
    except Exception as e:
        print(f"Error al cargar jugadores: {e}")
        return []


def buscar_jugador_por_id(jugador_id: str) -> Optional[Dict[str, str]]:
    """Busca y retorna un jugador por su identificador único."""
    jugadores = cargar_catalogo_jugadores()
    for j in jugadores:
        if j.get("id") == jugador_id:
            return j
    return None


def cargar_opiniones() -> List[Dict]:
    """Carga todas las opiniones almacenadas."""
