# Laboratorio – Servidor basado en contenedores (Docker)

Clase modelo · Gestión de Infraestructura para DevOps · Diploma DevOps Engineer (DMC Institute)

API de una tienda en línea (Python/Flask) y su base de datos Redis, cada una en su contenedor,
conectadas por una red Docker y con los datos guardados en un volumen.

| Archivo | Qué es |
|---|---|
| `app.py` | API Flask: `/salud` responde sola; `/` cuenta visitas en Redis |
| `requirements.txt` | Dependencias de la API (Flask y cliente de Redis) |
| `Dockerfile` | Receta de la imagen `tienda-api:1.0` |
| `compose.yaml` | Solución del reto 1 (pasos 3 a 6 en un solo archivo) |
| `probar.sh` | Ensayo automático de los 6 pasos, con verificación de cada resultado |

## Requisitos (VM Linux)
- Docker Engine activo y tu usuario en el grupo `docker`
- `curl` instalado
- Acceso a Docker Hub para descargar las imágenes

## Ensayo rápido antes de la clase
```bash
bash probar.sh            # ejecuta y verifica los 6 pasos; al final deja la VM limpia
bash probar.sh --limpiar  # solo limpia (útil justo antes de empezar la clase)
```

## Paso 1 · Verificar Docker
```bash
docker version --format '{{.Server.Version}}'
systemctl is-active docker
docker run --rm hello-world
```

## Paso 2 · Imágenes y contenedores
```bash
docker pull nginx:1.27-alpine
docker images
docker run -d --name web -p 8080:80 nginx:1.27-alpine
docker ps
curl -I http://localhost:8080        # HTTP/1.1 200 OK
docker logs web --tail 1
docker rm -f web
```

## Paso 3 · Alojar el backend en un contenedor
```bash
docker build -t tienda-api:1.0 .
docker run -d --name api -p 8080:5000 tienda-api:1.0
curl http://localhost:8080/salud     # {"contenedor":"<id>","estado":"ok"}
curl -i http://localhost:8080/       # 500: todavía no hay base de datos
```

## Paso 4 · Volúmenes
```bash
docker volume create redis-data
docker run -d --name cache -v redis-data:/data redis:7-alpine redis-server --appendonly yes
docker exec cache redis-cli set curso devops
docker rm -f cache                   # espera un par de segundos antes de borrar
docker run -d --name cache -v redis-data:/data redis:7-alpine redis-server --appendonly yes
docker exec cache redis-cli get curso   # devops
```

## Paso 5 · Redes
```bash
docker network create dmc-net
docker network connect dmc-net cache
docker rm -f api
docker run -d --name api --network dmc-net -p 8080:5000 -e REDIS_HOST=cache tienda-api:1.0
curl http://localhost:8080/          # {"tienda":"DMC","visitas":1}
curl http://localhost:8080/          # {"tienda":"DMC","visitas":2}
```

## Paso 6 · Prueba de fuego
```bash
docker rm -f api cache
docker run -d --name cache --network dmc-net -v redis-data:/data redis:7-alpine redis-server --appendonly yes
docker run -d --name api --network dmc-net -p 8080:5000 -e REDIS_HOST=cache tienda-api:1.0
curl http://localhost:8080/          # {"tienda":"DMC","visitas":3}
```

## Reto
1. Escribir un `compose.yaml` con lo que hicimos hoy (la solución está en este repositorio):
   ```bash
   docker rm -f api cache
   docker compose up -d --build
   curl http://localhost:8080/       # el contador continúa
   docker compose down               # el volumen redis-data se conserva
   ```
2. Agregar un `HEALTHCHECK` al Dockerfile de la API.
3. Publicar `tienda-api:1.0` en tu cuenta de Docker Hub (`docker tag` y `docker push`).
