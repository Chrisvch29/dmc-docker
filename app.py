import os, socket
from flask import Flask
from redis import Redis

app = Flask(__name__)
db = Redis(host=os.getenv("REDIS_HOST", "cache"), port=6379)

@app.get("/salud")
def salud():
    return {"estado": "ok", "contenedor": socket.gethostname()}

@app.get("/")
def inicio():
    return {"tienda": "DMC", "visitas": db.incr("visitas")}
