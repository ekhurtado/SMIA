# Build Instructions

## Docker Build

```bash
docker build -t asset-simulator .
```

## Build Output

El build genera una imagen Docker con:
- Python 3.12-slim como base
- Dependencias instaladas desde requirements.txt
- Codigo de la aplicacion en /app
- Puerto 5000 expuesto

## Verificacion del Build

```bash
# Verificar que la imagen se creo
docker images asset-simulator

# Verificar que los archivos estan en la imagen
docker run --rm asset-simulator ls -la /app
```

## Solucion de Problemas

### Error: Cannot find module 'fastapi'
Verificar que requirements.txt incluye todas las dependencias.

### Error: Template directory not found
Verificar que templates/index.html existe en el directorio raiz.
