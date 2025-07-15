from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import subprocess
import os
from typing import List

COMPOSE_FILE = os.path.join(os.path.dirname(__file__), "..", "docker", "compose-templates", "company-topology.yml")

app = FastAPI(title="Topology Orchestrator API")

class TopologyAction(BaseModel):
    action: str  # start | stop | status

@app.post("/topology")
async def manage_topology(req: TopologyAction):
    if req.action == "start":
        return _compose_up()
    if req.action == "stop":
        return _compose_down()
    if req.action == "status":
        return _compose_ps()
    raise HTTPException(status_code=400, detail="Invalid action")

def _compose_up():
    try:
        subprocess.check_call(["docker-compose", "-f", COMPOSE_FILE, "up", "-d"])
        # Return currently running services so the frontend can render containers immediately
        services_info = _compose_ps()
        return {"status": "started", **services_info}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

def _compose_down():
    try:
        subprocess.check_call(["docker-compose", "-f", COMPOSE_FILE, "down", "--remove-orphans"])
        return {"status": "stopped"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

def _compose_ps():
    try:
        output = subprocess.check_output(["docker-compose", "-f", COMPOSE_FILE, "ps", "--services", "--filter", "status=running"])
        services: List[str] = output.decode().strip().split("\n") if output else []
        return {"running_services": services}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Expose the same functionality under the /api prefix so that the
# frontend proxy (see vite.config.js) can reach it at /api/topology
# -----------------------------
api_router = APIRouter(prefix="/api")

@api_router.post("/topology")
async def manage_topology_api(req: TopologyAction):
    """Proxy endpoint matching the frontend expectation (POST /api/topology)."""
    return await manage_topology(req)

# Register router
app.include_router(api_router)

# 启动命令示例：uvicorn backend.main:app --reload --port 8080 