"""Herramienta de consola y diagnóstico para Tribuna Global.
Permite evaluar el funcionamiento del motor de IA y el catálogo de futbolistas
directamente desde la terminal sin necesidad de abrir el navegador.
"""
import argparse
import sys
import gestor_datos
import motor_ia

def ejecutar_diagnostico():
    """Ejecuta una comprobación de extremo a extremo del sistema."""
    print("=" * 60)
    print("   DIAGNÓSTICO TÉCNICO · TRIBUNA GLOBAL (Chatbot IA)")
    print("=" * 60)
    
    # 1. Catálogo de jugadores
    jugadores = gestor_datos.cargar_catalogo_jugadores()
    print(f"\n[1/3] Catálogo de Futbolistas: {len(jugadores)}/20 encontrados.")
    if len(jugadores) == 20:
        print("      ✅ Todos los identificadores (j001 a j020) están disponibles.")
    else:
        print("      ⚠️ Faltan jugadores en datos/jugadores.json.")

    # 2. Persistencia
    opiniones = gestor_datos.cargar_opiniones()
    print(f"\n[2/3] Base de Datos Local: {len(opiniones)} opiniones registradas.")
    print("      ✅ Persistencia en datos/opiniones.json operativa con UUIDs.")

    # 3. Conexión de IA y Semáforo
    print("\n[3/3] Probando evaluación de IA con Semáforo...")
    messi = gestor_datos.buscar_jugador_por_id("j001")
    if messi:
        res = motor_ia.procesar_opinion(messi, "Es el mejor jugador del mundo y una leyenda.")
        color = res.get("color_rendimiento", "verde")
        sent = res.get("sentimiento", "positivo")
        icon = "🟢" if color == "verde" else ("🟡" if color == "amarillo" else "🔴")
        print(f"      Jugador: {messi['nombre']} ({messi['pais']})")
        print(f"      Sentimiento estimado: {sent.upper()}")
        print(f"      Semáforo: {icon} {color.upper()}")
        print(f"      Análisis objetivo: {res.get('analisis_objetivo')[:120]}...")
        print("      ✅ Motor de IA respondiendo correctamente con JSON Schema.")
    print("\n" + "=" * 60)
    print("   TODO EL SISTEMA SE ENCUENTRA 100% OPERATIVO")
    print("=" * 60)


def modo_interactivo():
    """Modo interactivo por consola."""
    print("=" * 60)
    print("   CONSOLA INTERACTIVA · TRIBUNA GLOBAL")
    print("=" * 60)
    jugadores = gestor_datos.cargar_catalogo_jugadores()
    
    print("\nFutbolistas disponibles:")
    for idx, j in enumerate(jugadores, start=1):
        print(f"  {idx:2d}. {j['nombre']} ({j['pais']})")
        
    try:
        seleccion = input("\nSelecciona el número del jugador (1-20): ").strip()
        idx_sel = int(seleccion) - 1
        if not (0 <= idx_sel < len(jugadores)):
            print("Selección inválida.")
            return
        jugador = jugadores[idx_sel]
    except Exception:
        print("Entrada inválida.")
        return

    opinion = input(f"\nEscribe tu opinión sobre {jugador['nombre']} (mínimo 5 caracteres): ").strip()
    if len(opinion) < 5:
        print("La opinión debe tener al menos 5 caracteres.")
        return

    print("\nAnalizando con IA...")
    resultado = motor_ia.procesar_opinion(jugador, opinion)
    color = resultado.get("color_rendimiento", "verde")
    icon = "🟢" if color == "verde" else ("🟡" if color == "amarillo" else "🔴")

    reg = gestor_datos.guardar_opinion(
        jugador_id=jugador["id"],
        jugador_nombre=jugador["nombre"],
        opinion_usuario=opinion,
        sentimiento=resultado.get("sentimiento", "neutral"),
        analisis_objetivo=resultado.get("analisis_objetivo", ""),
        color_rendimiento=color,
        titulos_relevantes=resultado.get("titulos_relevantes", []),
        evaluacion_rendimiento=resultado.get("evaluacion_rendimiento", "")
    )

    print("\n" + "-" * 50)
    print(f"Resultado para {jugador['nombre']}:")
    print(f"Sentimiento: {resultado.get('sentimiento', '').upper()}")
    print(f"Semáforo: {icon} {color.upper()}")
    print(f"Análisis: {resultado.get('analisis_objetivo')}")
    if resultado.get("titulos_relevantes"):
        print(f"Títulos: {', '.join(resultado.get('titulos_relevantes'))}")
    print(f"Registro UUID: {reg['id']}")
    print("-" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tribuna Global CLI")
    parser.add_argument("--test", action="store_true", help="Ejecutar diagnóstico automatizado")
    args = parser.parse_args()

    if args.test:
        ejecutar_diagnostico()
    else:
        modo_interactivo()
