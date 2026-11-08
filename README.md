<div align="center" id="inicio">

# ⚽ Tribuna Global · Chatbot de Análisis Futbolístico con IA

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/Licencia-MIT-green.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/usuario/Chatbot-IA?style=social)](https://github.com)
[![Forks](https://img.shields.io/github/forks/usuario/Chatbot-IA?style=social)](https://github.com)
[![Issues](https://img.shields.io/github/issues/usuario/Chatbot-IA)](https://github.com)

**Plataforma inteligente y ultra rápida de análisis y evaluación objetiva de futbolistas mundiales, impulsada por IA y un sistema de clasificación semafórica de rendimiento.**

</div>

---

> [!IMPORTANT]
> ### ⚡ Acceso Directo e Instrucciones de Evaluación (Para el Profesor y Evaluadores)
> 
> Esta solución cuenta con un motor de Inteligencia Artificial desarrollado en Python/Streamlit que corre en el **puerto 8501**. Se puede ejecutar y abrir de dos formas:
> 
> #### 🔗 Enlace Directo a la Aplicación en Vivo:
> 👉 **[http://localhost:8501](http://localhost:8501)** *(o también [http://127.0.0.1:8501](http://127.0.0.1:8501))*
> 
> ---
> 
> #### 🛠️ Las 2 Formas Oficiales de Ejecución:
> 
> 1. **Forma 1 · Ejecución Rápida con 1 Clic (Recomendada):**
>    * Haz doble clic en el archivo [`iniciar_chatbot.bat`](iniciar_chatbot.bat) o [`run.bat`](run.bat).
>    * El script inteligente verifica Python, instala dependencias faltantes de `requirements.txt` e inicia el backend abriendo automáticamente la página en [http://localhost:8501](http://localhost:8501).
>    * *(En Linux o macOS ejecutar: `bash run.sh`)*.
> 
> 2. **Forma 2 · Desde Visual Studio Code (F5 o Live Server):**
>    * **Con F5 / Tareas de VS Code:** Presiona la tecla **F5** o abre la carpeta; la tarea configurada en [`.vscode/tasks.json`](.vscode/tasks.json) iniciará el servidor de IA de inmediato.
>    * **Con la extensión Live Server:** Si inicias Live Server (puerto `5500` / `5501`), el archivo [`index.html`](index.html) intercepta la petición automáticamente y te redirige en 3 segundos a [http://localhost:8501](http://localhost:8501) (aclarando que el motor de IA de Python opera en el puerto 8501).

---

<details>
<summary>📑 <strong>Tabla de Contenidos (Haz clic para desplegar)</strong></summary>

1. [Acerca del Proyecto](#-acerca-del-proyecto)
2. [Construido con](#-construido-con)
3. [Arquitectura del Sistema](#-arquitectura-del-sistema)
4. [Prerrequisitos](#-prerrequisitos)
5. [Instalación](#-instalación)
6. [Uso y Características](#-uso-y-características)
7. [Pruebas](#-pruebas)
8. [Hoja de Ruta (Roadmap)](#-hoja-de-ruta-roadmap)
9. [Contacto](#-contacto)

</details>

---

## 📖 Acerca del Proyecto

**Tribuna Global** es un asistente conversacional especializado en el mundo del fútbol que recibe opiniones, comentarios y críticas de aficionados sobre futbolistas de élite y genera respuestas rápidas, objetivas e imparciales basadas en el rendimiento real en la cancha y los títulos obtenidos con sus clubes y selecciones.

### Características Principales
- 🟢🟡🔴 **Sistema de Semáforo de Rendimiento:** Categoriza objetivamente al jugador según su palmarés y regularidad en cancha.
- ⚡ **Respuestas Rápidas con IA:** Integración con modelos LLM (`gpt-4o-mini`) con `temperatura 0` y salida garantizada mediante `JSON Schema` (Structured Outputs).
- 🛡️ **Seguridad de Claves:** Manejo estricto de credenciales por medio de variables de entorno protegidas (`.env` en `.gitignore`).
- 💾 **Persistencia de Registros:** Asignación automática de identificadores únicos (`UUID4`) para auditoría y consulta histórica.
- 🎨 **Interfaz Moderna en Tema Oscuro:** Diseñada en Streamlit con experiencia fluida e intuitiva.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 🛠️ Construido con

* ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) - Lenguaje de programación principal.
* ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) - Framework frontend y motor de interfaz reactiva.
* ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white) - Modelo LLM con Structured Outputs (`gpt-4o-mini`).
* ![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white) - Persistencia y catálogo estructurado de datos.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 🏛️ Arquitectura del Sistema

```text
Chatbot-IA/
│
├── .streamlit/
│   └── config.toml               # Configuración de tema oscuro y servidor Streamlit
│
├── .vscode/
│   ├── launch.json               # Configuración de depuración F5 en VS Code
│   └── tasks.json                # Tarea automatizada al abrir carpeta en VS Code
│
├── datos/
│   ├── jugadores.json            # Catálogo oficial con identificadores estables (j001 - j020)
│   └── opiniones.json            # Registro histórico de opiniones persistidas con UUID
│
├── tests/
│   └── test_chatbot.py           # Suite de pruebas unitarias automatizadas con pytest
│
├── .env.example                  # Plantilla de variables de entorno para claves API
├── .gitignore                    # Reglas de exclusión para no exponer credenciales
├── app.py                        # Interfaz gráfica Streamlit y orquestador UI/UX
├── demo_cli.py                   # Herramienta de consola y diagnóstico sin navegador
├── gestor_datos.py               # Capa de acceso a datos, filtrado y persistencia
├── index.html                    # Redirección amigable e interfaz puente para Live Server
├── iniciar_chatbot.bat           # Lanzador automático inteligente en Windows (1 clic)
├── motor_ia.py                   # Motor analítico, prompts, JSON Schema y fallback heurístico
├── requirements.txt              # Dependencias del proyecto
├── run.bat                       # Alias de ejecución rápida en Windows
├── run.sh                        # Script de ejecución para Linux y macOS
└── README.md                     # Documentación profesional del sistema
```

### Flujo de Datos

```text
[ Aficionado / Usuario ]
           │
           ▼
[ Validación UI (5 a 1000 caracteres) ]
           │
           ▼
[ Motor IA (Temperatura 0 + JSON Schema) ]
           │
           ├────────► [ OpenAI gpt-4o-mini ] (con API Key)
           └────────► [ Heurística Rápida Local ] (Fallback de contingencia)
           │
           ▼
[ Semáforo (Verde / Amarillo / Rojo) + Sentimiento + Análisis ]
           │
           ▼
[ Persistencia en datos/opiniones.json (UUID v4) ]
           │
           ▼
[ Tarjeta Dinámica en Tribuna Global ]
```

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 📋 Prerrequisitos

* **Python 3.10 o superior** instalado en el sistema.
* Un gestor de paquetes como `pip`.
* *(Opcional)* Clave de API de OpenAI (`OPENAI_API_KEY`) para activar las llamadas en tiempo real con `gpt-4o-mini`. El sistema cuenta con un motor local inteligente de contingencia que opera de manera autónoma si no se ingresa una clave.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## ⚙️ Instalación

1. **Clonar o ubicarse en el directorio del proyecto:**
   ```bash
   cd "c:\Users\osori\Desktop\trabajos de campus\Chatbot-IA"
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   # En Windows PowerShell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias necesarias:**
   ```bash
   py -m pip install -r requirements.txt
   ```

4. **Configurar las variables de entorno:**
   * Copia el archivo `.env.example` a `.env`:
     ```bash
     copy .env.example .env
     ```
   * Abre `.env` y coloca tu API Key de OpenAI:
     ```env
     OPENAI_API_KEY=sk-...tu_clave_real_aqui...
     DEFAULT_MODEL=gpt-4o-mini
     ```
   > ⚠️ **Importante:** El archivo `.env` se encuentra agregado en el `.gitignore` para proteger la clave y evitar fugas de credenciales.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 🚀 Uso y Características

### 1. Iniciar el Servidor de la Aplicación
Ejecuta en tu terminal:
```bash
py -m streamlit run app.py
```
La aplicación se abrirá automáticamente en tu navegador en:
`http://localhost:8501`

### 2. Modos de Uso

* **Sección "Emitir opinión":**
  1. Selecciona el futbolista en la barra lateral (ej. `Vinícius Júnior · Brasil`, `Lionel Messi · Argentina`).
  2. Escribe tu opinión en el campo inferior (validación de 5 a 1000 caracteres).
  3. Recibe la evaluación inmediata con el semáforo de color correspondiente:
     * 🟢 **Verde:** Rendimiento de élite, títulos trascendentes y palmarés comprobado.
     * 🟡 **Amarillo:** Rendimiento regular, intermitente o en desarrollo.
     * 🔴 **Rojo:** Rendimiento bajo, crítico o deficiente.
  4. La opinión se guarda automáticamente con su identificador único (`UUID`).

* **Sección "Consultar opiniones":**
  1. Filtra las opiniones históricas por jugador, sentimiento estimado o color del semáforo.
  2. Visualiza métricas globales de participación en tiempo real.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 🧪 Pruebas

Puedes ejecutar una prueba automatizada del motor analítico y del gestor de datos ejecutando:

```bash
# Probar carga del catálogo oficial de 20 futbolistas
py -c "import gestor_datos; print('Catálogo OK, total jugadores:', len(gestor_datos.cargar_catalogo_jugadores()))"

# Probar análisis y semáforo de opinión
py -c "import motor_ia, gestor_datos; j = gestor_datos.buscar_jugador_por_id('j006'); print(motor_ia.procesar_opinion(j, 'Me parece que no es tan bueno porque es de brasil'))"
```

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 🗺️ Hoja de Ruta (Roadmap)

- [x] Estructura inicial con `datos/jugadores.json` y los 20 futbolistas oficiales.
- [x] Configuración de persistencia local en `datos/opiniones.json` con UUID.
- [x] Motor de IA con soporte para `temperatura 0` y `JSON Schema` (`gpt-4o-mini`).
- [x] Sistema semafórico con colores Verde, Amarillo y Rojo según títulos y rendimiento.
- [x] Interfaz gráfica en Streamlit con tema oscuro replicando el diseño oficial.
- [x] Módulo de consulta histórica con filtros y métricas por jugador.
- [x] Gráficos interactivos de evolución y distribución de sentimiento y semáforo.
- [x] Exportación de reportes de auditoría en formatos CSV y JSON.

<p align="right">(<a href="#inicio">Volver al inicio ⬆</a>)</p>

---

## 📬 Contacto

Desarrollado para el proyecto formativo de Inteligencia Artificial aplicada al fútbol.

* **Proyecto:** Tribuna Global - Chatbot IA de Opinión Futbolística
* **Repositorio:** [Chatbot-IA](https://github.com)

<p align="center">Hecho con pasión por el fútbol y la inteligencia artificial ⚽🤖</p>

