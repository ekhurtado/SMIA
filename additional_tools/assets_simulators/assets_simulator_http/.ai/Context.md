# Simulador Multi-Activo Centralizado

## Descripción del Proyecto
Servidor HTTP con FastAPI + Uvicorn dentro de Docker que simula el estado
técnico de activos industriales (robots, máquinas) en tiempo real.

## Stack Tecnológico
- Backend: Python 3.12, FastAPI, Uvicorn
- Concurrencia: asyncio puro (Lock, shield, CancelledError)
- Streaming: SSE via StreamingResponse nativo de FastAPI
- Frontend: HTML + Tailwind CSS + Flowbite (solo CDN, sin Node.js)
- Templating: Jinja2Templates
- Contenedor: Docker (puerto 5000)

## Estructura de Ficheros Objetivo

/
├── main.py
├── templates/
│   └── index.html
├── Dockerfile
├── requirements.txt
├── AGENTS.md
└── .ai/
├── build.md
├── run.md
└── test.md

## Variable de Entorno Obligatoria
- `AVAILABLE_ASSETS`: lista separada por comas (ej: `robot_A,robot_B,welder_C`)
- El servidor debe parsearla defensivamente al arranque

## PATRONES CRÍTICOS DE CONCURRENCIA — NO NEGOCIABLES

### Patrón 1: asyncio.Lock por activo
Cada activo del diccionario global debe tener su propio asyncio.Lock.
Toda transición idle→busy→idle DEBE ejecutarse dentro de `async with lock`.
NUNCA usar un lock global único para todos los activos (cuello de botella).

### Patrón 2: Protección contra desconexión de cliente
El endpoint POST /api/v1/asset/{asset_id}/action debe:
1. Lanzar la simulación como tarea independiente: `task = asyncio.create_task(_simulate(asset_id, duration))`
2. Proteger el await con shield: `await asyncio.shield(task)`
3. Si llega CancelledError al endpoint, la tarea interna SIGUE ejecutándose
4. La función _simulate() debe restaurar el estado a "idle" en su bloque finally

Patrón correcto obligatorio:
```python
async def _simulate(asset_id: str, duration: float):
    try:
        await asyncio.sleep(duration)
    finally:
        async with assets[asset_id]["lock"]:
            assets[asset_id]["state"] = "idle"

# Dentro del endpoint:
task = asyncio.create_task(_simulate(asset_id, duration))
try:
    await asyncio.shield(task)
except asyncio.CancelledError:
    pass  # tarea continúa en background
```

### Patrón 3: Limpieza del generador SSE
El generador de /ui/stream DEBE tener try/except asyncio.CancelledError
para detectar desconexión del cliente y terminar limpiamente sin memory leaks.

## Restricciones de Diseño
- Duración máxima de tarea simulada: < 30 segundos (límite TCP/timeout)
- El frontend es una SPA sin build tools: solo CDN
- No usar sse-starlette: usar StreamingResponse nativo de FastAPI
- Python 3.12+

## Comandos de Desarrollo

### Build Docker
```bash
docker build -t asset-simulator .
```

### Run Docker
```bash
docker run -p 5000:5000 -e AVAILABLE_ASSETS="robot_A,robot_B,welder_C" asset-simulator
```

### Validación rápida (sin Docker)
```bash
pip install -r requirements.txt
AVAILABLE_ASSETS="robot_A,robot_B" uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Test manual de endpoints
```bash
# Estado de un activo
curl http://localhost:5000/api/v1/asset/robot_A/status

# Lanzar tarea
curl -X POST http://localhost:5000/api/v1/asset/robot_A/action \
  -H "Content-Type: application/json" \
  -d '{"action": "weld", "duration": 10}'

# Stream SSE
curl -N http://localhost:5000/ui/stream
```

## Criterios de Aceptación (Checklist de Calidad)
- [ ] Si robot_A está busy, un segundo POST a robot_A devuelve HTTP 409
- [ ] Si el cliente se desconecta durante un POST /action, el activo vuelve a idle al cumplirse la duración
- [ ] Si se abren 3 pestañas del navegador, las 3 se actualizan simultáneamente vía SSE
- [ ] Al cerrar una pestaña, no quedan generadores SSE zombies (verificar con logs)
- [ ] El spinner de Flowbite aparece/desaparece correctamente al cambiar estado

## Estilo de Código
- Type hints en todas las funciones
- Docstrings en funciones públicas
- Manejo explícito de errores con HTTPException de FastAPI
- Logs informativos con el módulo `logging` estándar de Python