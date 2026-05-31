# Guia para AI Agents - Asset Simulator HTTP

## Estructura del Proyecto

```
/
├── main.py                    # Backend FastAPI completo
├── templates/
│   └── index.html             # Frontend SPA reactivo
├── Dockerfile                 # Contenedor Python 3.12
├── requirements.txt           # Dependencias Python
├── AGENTS.md                  # Este archivo
└── .ai/
    ├── build.md               # Instrucciones de build
    ├── run.md                 # Instrucciones de ejecucion
    ├── test.md                # Instrucciones de testing
    └── skills/
        ├── css-animations/    # Patrones de animaciones CSS
        ├── fastapi-python/    # Mejores practicas FastAPI
        └── frontend-design/   # Diseno de interfaces web
```

## Comandos de Desarrollo

### Build Docker
```bash
docker build -t asset-simulator .
```

### Run Docker
```bash
docker run -p 5000:5000 -e AVAILABLE_ASSETS="robot_A,robot_B,welder_C" asset-simulator
```

### Validacion local (sin Docker)
```bash
pip install -r requirements.txt
AVAILABLE_ASSETS="robot_A,robot_B" uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Ejecutar sin activos
```bash
# El servidor funciona correctamente sin activos definidos
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## Patrones de Concurrencia

### Patrón 1: asyncio.Lock por activo
Cada activo tiene su propio Lock. NUNCA usar lock global.

```python
assets[asset_id] = {
    "state": "idle",
    "lock": asyncio.Lock()  # Lock por activo
}
```

### Patrón 2: Proteccion contra desconexion
Usar `asyncio.create_task()` + `asyncio.shield()` + `CancelledError`.

```python
task = asyncio.create_task(_simulate(asset_id, duration))
try:
    await asyncio.shield(task)
except asyncio.CancelledError:
    pass  # La tarea continua en background
```

### Patrón 3: Limpieza SSE
El generador DEBE tener `try/except asyncio.CancelledError`.

```python
async def event_generator():
    try:
        while True:
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Cliente SSE desconectado")
        raise
```

## Endpoints API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/api/v1/asset/{asset_id}/status` | Estado de un activo |
| POST | `/api/v1/asset/{asset_id}/action` | Ejecutar accion |
| GET | `/ui/stream` | Stream SSE |
| GET | `/` | Frontend SPA |

## Comportamiento sin Activos

Cuando no hay activos definidos en `AVAILABLE_ASSETS`:
- El servidor arranca correctamente
- La interfaz muestra un mensaje "No hay activos disponibles"
- Los controles de accion estan deshabilitados
- Los endpoints existentes devuelven 404 para activos inexistentes

## Skills Library

| Skill | Path | Descripcion | Cuando usar |
|-------|------|-------------|-------------|
| css-animations | `.ai/skills/css-animations/SKILL.md` | Patrones de animaciones CSS keyframes, animation-delay, fill-mode y motion determinista. | Cuando se necesitan animaciones CSS decorativas, shimmer, glow, parallax o motion simple en un solo elemento. |
| fastapi-python | `.ai/skills/fastapi-python/SKILL.md` | Mejores practicas de desarrollo FastAPI con Python: tipos, async, patrones RORO, manejo de errores. | Cuando se desarrollan o modifican endpoints, operaciones async o estructura del backend FastAPI. |
| frontend-design | `.ai/skills/frontend-design/SKILL.md` | Diseno de interfaces web distintivas y production-grade con foco en estetica y tipografia. | Cuando se disenan, crean o estilizan componentes, paginas o aplicaciones web con alta calidad visual. |

## Criterios de Aceptacion

- [ ] Si robot_A esta busy, un segundo POST devuelve HTTP 409
- [ ] Si el cliente se desconecta durante POST /action, el activo vuelve a idle
- [ ] Si se abren 3 pestanas, las 3 se actualizan via SSE
- [ ] Al cerrar pestana, no quedan generadores SSE zombies
- [ ] El spinner aparece/desaparece correctamente al cambiar estado
- [ ] El servidor funciona correctamente sin activos definidos
