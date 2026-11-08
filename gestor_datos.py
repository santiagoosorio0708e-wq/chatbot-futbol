"""Módulo de gestión de datos para jugadores y persistencia de opiniones."""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_JUGADORES = os.path.join(RUTA_BASE, "datos", "jugadores.json")
RUTA_OPINIONES = os.path.join(RUTA_BASE, "datos", "opiniones.json")
RUTA_CONVERSACIONES = os.path.join(RUTA_BASE, "datos", "conversaciones.json")


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


# --- GESTIÓN DE HISTORIAL DE CONVERSACIONES ---

def cargar_conversaciones() -> List[Dict]:
    """Carga todas las conversaciones almacenadas localmente."""
    if not os.path.exists(RUTA_CONVERSACIONES):
        return []
    try:
        with open(RUTA_CONVERSACIONES, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("conversaciones", [])
    except Exception as e:
        print(f"Error al cargar conversaciones: {e}")
        return []


def obtener_conversacion_por_id(conv_id: str) -> Optional[Dict]:
    """Recupera una conversación específica por su identificador único."""
    todas = cargar_conversaciones()
    for c in todas:
        if c.get("id") == conv_id:
            return c
    return None


def guardar_conversacion(
    conv_id: str,
    titulo: str,
    jugador_id: str,
    jugador_nombre: str,
    mensajes: List[Dict]
) -> Dict:
    """
    Crea o actualiza una conversación en datos/conversaciones.json.
    """
    conversaciones = cargar_conversaciones()
    
    # Buscar si ya existe para actualizarla
    encontrada = False
    registro_actualizado = None
    for i, c in enumerate(conversaciones):
        if c.get("id") == conv_id:
            c["titulo"] = titulo
            c["jugador_id"] = jugador_id
            c["jugador_nombre"] = jugador_nombre
            c["mensajes"] = mensajes
            c["fecha_actualizacion"] = datetime.now().isoformat()
            conversaciones[i] = c
            registro_actualizado = c
            encontrada = True
            break
            
    if not encontrada:
        nuevo = {
            "id": conv_id,
            "titulo": titulo,
            "fecha": datetime.now().isoformat(),
            "jugador_id": jugador_id,
            "jugador_nombre": jugador_nombre,
            "mensajes": mensajes
        }
        conversaciones.insert(0, nuevo)
        registro_actualizado = nuevo
        
    os.makedirs(os.path.dirname(RUTA_CONVERSACIONES), exist_ok=True)
    with open(RUTA_CONVERSACIONES, "w", encoding="utf-8") as f:
        json.dump({"conversaciones": conversaciones}, f, ensure_ascii=False, indent=2)
        
    return registro_actualizado


def eliminar_conversacion(conv_id: str) -> bool:
    """Elimina una conversación del archivo local."""
    conversaciones = cargar_conversaciones()
    nuevas = [c for c in conversaciones if c.get("id") != conv_id]
    if len(nuevas) != len(conversaciones):
        with open(RUTA_CONVERSACIONES, "w", encoding="utf-8") as f:
            json.dump({"conversaciones": nuevas}, f, ensure_ascii=False, indent=2)
        return True
    return False


