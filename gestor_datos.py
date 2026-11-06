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
    if not os.path.exists(RUTA_OPINIONES):
        return []
    try:
        with open(RUTA_OPINIONES, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("opiniones", [])
    except Exception as e:
        print(f"Error al cargar opiniones: {e}")
        return []


def guardar_opinion(
    jugador_id: str,
    jugador_nombre: str,
    opinion_usuario: str,
    sentimiento: str,
    analisis_objetivo: str,
    color_rendimiento: str,
    titulos_relevantes: Optional[List[str]] = None,
    evaluacion_rendimiento: Optional[str] = None
) -> Dict:
    """
    Guarda una nueva opinión en datos/opiniones.json y retorna el registro creado con su UUID.
    """
    opiniones = cargar_opiniones()
    
    nuevo_registro = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "jugador_id": jugador_id,
        "jugador_nombre": jugador_nombre,
        "opinion_usuario": opinion_usuario,
        "sentimiento": sentimiento.lower(),  # positivo, neutral, negativo
        "color_rendimiento": color_rendimiento.lower(),  # verde, amarillo, rojo
        "analisis_objetivo": analisis_objetivo,
        "evaluacion_rendimiento": evaluacion_rendimiento or "",
        "titulos_relevantes": titulos_relevantes or []
    }
    
    opiniones.insert(0, nuevo_registro)
    
    os.makedirs(os.path.dirname(RUTA_OPINIONES), exist_ok=True)
    with open(RUTA_OPINIONES, "w", encoding="utf-8") as f:
        json.dump({"opiniones": opiniones}, f, ensure_ascii=False, indent=2)
        
    return nuevo_registro


def filtrar_opiniones_por_jugador(jugador_id: str) -> List[Dict]:
    """Filtra y devuelve opiniones correspondientes a un jugador específico."""
    todas = cargar_opiniones()
    return [op for op in todas if op.get("jugador_id") == jugador_id]

