# Test Instructions

## Tests Manuales de Endpoints

### 1. Estado de un activo
```bash
curl http://localhost:5000/api/v1/asset/robot_A/status
```

Respuesta esperada:
```json
{
    "asset_id": "robot_A",
    "state": "idle",
    "current_action": null,
    "battery": 100.0
}
```

### 2. Lanzar tarea
```bash
curl -X POST http://localhost:5000/api/v1/asset/robot_A/action \
  -H "Content-Type: application/json" \
  -d '{"action": "weld", "duration": 10}'
```

### 3. Verificar busy
```bash
# Inmediatamente despues del POST anterior, verificar estado
curl http://localhost:5000/api/v1/asset/robot_A/status

# Intentar segunda tarea (debe devolver 409)
curl -X POST http://localhost:5000/api/v1/asset/robot_A/action \
  -H "Content-Type: application/json" \
  -d '{"action": "paint", "duration": 5}'
```

### 4. Stream SSE
```bash
curl -N http://localhost:5000/ui/stream
```

### 5. Test de Desconexion

1. Abrir pestana del navegador en http://localhost:5000/
2. Ejecutar POST /action con duracion larga (ej: 20s)
3. Cerrar la pestana antes de que termine
4. Verificar en logs que el activo vuelve a idle

### 6. Test Multi-Pestana

1. Abrir 3 pestanas en http://localhost:5000/
2. Ejecutar POST /action en una de ellas
3. Verificar que las 3 pestanas muestran el spinner simultaneamente

### 7. Test sin Activos

1. Ejecutar el servidor sin definir AVAILABLE_ASSETS:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5000
   ```
2. Abrir http://localhost:5000/ en el navegador
3. Verificar que se muestra el mensaje "No hay activos disponibles"
4. Verificar que los controles de accion estan deshabilitados
5. Verificar que el stream SSE funciona (el indicador muestra "Conectado")

## Criterios de Aceptacion

- [ ] Si robot_A esta busy, un segundo POST devuelve HTTP 409
- [ ] Si el cliente se desconecta durante POST /action, el activo vuelve a idle
- [ ] Si se abren 3 pestanas, las 3 se actualizan via SSE
- [ ] Al cerrar pestana, no quedan generadores SSE zombies
- [ ] El spinner aparece/desaparece correctamente al cambiar estado
- [ ] El servidor funciona correctamente sin activos definidos
