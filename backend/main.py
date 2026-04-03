from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # autorise React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_password = os.getenv("REDIS_PASSWORD")
r = redis.Redis(host=redis_host, port=6379, password=redis_password, decode_responses=True)

pixel_updates = Counter("pixel_updates_total", "Nombre total de pixels modifiés")

GRID_SIZE = 50

if not r.exists("grid"):
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    r.set("grid", json.dumps(grid))

class PixelUpdate(BaseModel):
    x: int
    y: int
    color: int

@app.get("/grid")
def get_grid():
    grid = json.loads(r.get("grid"))
    return {"grid": grid}

@app.post("/pixel")
def update_pixel(update: PixelUpdate):
    grid = json.loads(r.get("grid"))
    grid[update.y][update.x] = update.color
    r.set("grid", json.dumps(grid))
    pixel_updates.inc()
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    # Readiness: ensure Redis is reachable
    try:
        if not r.ping():
            raise HTTPException(status_code=503, detail="Redis unreachable")
    except Exception as exc:  # pragma: no cover - defensive readiness
        raise HTTPException(status_code=503, detail=str(exc))
    return {"status": "ok"}


@app.get("/livez")
def livez():
    # Liveness: process is up
    return {"status": "alive"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
