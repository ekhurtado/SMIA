**Contexto y Rol:**
Eres un Arquitecto de Software Experto especializado en Python y simulaciones industriales. Debes escribir el código completo, robusto y listo para producción para un **Simulador Multi-Activo Centralizado** utilizando **FastAPI** y **Uvicorn** dentro de un contenedor Docker.

**Requisitos Críticos de Arquitectura (Asincronía Pura):**
1. **Estado Global Dinámico:** Los activos a simular se inyectan mediante la variable de entorno `AVAILABLE_ASSETS` (ej. `robot_A,robot_B`). Al arrancar, inicializa un diccionario global en memoria para almacenar el estado técnico de cada activo (estado actual `"idle"`/`"busy"`, batería, etc.). Es OBLIGATORIO proteger todas las transiciones de estado (lectura-modificación-escritura) utilizando `asyncio.Lock` (ya sea un lock global o uno por activo) para garantizar matemáticamente la integridad de los datos frente a condiciones de carrera asíncronas.
2. **Protección contra Desconexiones (CRÍTICO):** Cuando se inicie una simulación de tarea (POST `/action`), el servidor debe usar `await asyncio.sleep(duration)` para retrasar la respuesta HTTP. Sin embargo, si el cliente se desconecta prematuramente y FastAPI lanza un `asyncio.CancelledError`, el activo **debe** continuar su simulación internamente. Debes usar `asyncio.shield()` o un bloque `try... finally` para garantizar matemáticamente que, una vez transcurrido el tiempo, el estado del activo vuelva a `"idle"` sin corromper la memoria del servidor. Nota: Asume que las duraciones de las tareas simuladas (`duration`) serán inferiores a 30 segundos para evitar que la capa TCP o el navegador cierren la conexión por timeout (504 Gateway Timeout) antes de que el servidor envíe la respuesta HTTP 200.

**Especificación de las APIs (Enrutamiento Dinámico):**
* **API Pública (Software Externo):**
  * `GET /api/v1/asset/{asset_id}/status`: Retorna el JSON con la telemetría del activo.
  * `POST /api/v1/asset/{asset_id}/action`: Recibe un JSON validado por Pydantic (ej. `{"action": "weld", "duration": 15}`). Cambia el estado a `"busy"`, espera el tiempo asíncronamente (protegido contra desconexiones), restaura a `"idle"` y devuelve HTTP 200.
* **API BFF (Interfaz Web):**
  * `GET /ui/stream`: Endpoint asíncrono que implementa Server-Sent Events (SSE) utilizando el generador nativo `StreamingResponse` de FastAPI. Es CRÍTICO que el generador de eventos incluya un bloque `try... except asyncio.CancelledError` para detectar la desconexión del cliente, cerrar el generador limpiamente y prevenir fugas de memoria. Debe emitir el JSON del estado global hacia los clientes conectados periódicamente o cuando haya mutaciones de estado, sin bloquear el Event Loop.

**Especificación del Frontend (SPA Estricta sin Node.js):**
* Usa `Jinja2Templates` de FastAPI para servir un único archivo `templates/index.html`.
* **Stack UI:** Usa estrictamente **Tailwind CSS y Flowbite vía CDN**. No utilices herramientas de build.
* **Reactividad:** El frontend utilizará la API nativa de JavaScript `EventSource` conectada a `/ui/stream`. El DOM debe reaccionar a los eventos SSE para repintar una cuadrícula (Grid) global de tarjetas (Cards) de activos.
* **Experiencia Visual:** Si el estado de un activo recibido por SSE es `"busy"`, su tarjeta debe mostrar dinámicamente un Spinner de carga de Flowbite. También se debe añadir una animación SVG que simule la realización de la tarea del activo (por ejemplo, un brazo robótico). Al volver a `"idle"`, el Spinner debe desaparecer. Debe incluir un panel para forzar tareas (`POST /action`) manualmente con `fetch()`.

**Entregables Esperados:**
Genera los archivos completos, sin omitir lógica interna:
1. `main.py` (Lógica FastAPI, Pydantic, manejo de excepciones de cancelación, SSE).
2. `templates/index.html` (UI reactiva con Tailwind/Flowbite).
3. `Dockerfile` (Configurado para ejecutar `uvicorn main:app --host 0.0.0.0 --port 5000`).
4. `requirements.txt` (fastapi, uvicorn, jinja2, pydantic, y si aplica, sse-starlette).