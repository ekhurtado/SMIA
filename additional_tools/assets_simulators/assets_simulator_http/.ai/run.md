# Run Instructions

## Docker Run

```bash
docker run -p 5000:5000 -e AVAILABLE_ASSETS="robot_A,robot_B,welder_C" asset-simulator
```

## Local Run (sin Docker)

```bash
pip install -r requirements.txt
AVAILABLE_ASSETS="robot_A,robot_B" uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## Endpoints Disponibles

| URL | Descripcion |
|-----|-------------|
| http://localhost:5000/ | Frontend SPA |
| http://localhost:5000/ui/stream | Stream SSE |
| http://localhost:5000/docs | Swagger UI |
| http://localhost:5000/api/v1/asset/{id}/status | Estado de activo |

## Variables de Entorno

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| AVAILABLE_ASSETS | Lista de activos separada por comas | robot_A,robot_B,welder_C |

## Verificacion de Salud

```bash
# Verificar que el servidor responde
curl http://localhost:5000/

# Verificar estado de un activo
curl http://localhost:5000/api/v1/asset/robot_A/status
```
