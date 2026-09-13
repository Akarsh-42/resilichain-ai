import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .environment import SupplyChainEnvironment
from .orchestrator import ControlTowerOrchestrator
from .store import StateStore


DATABASE_PATH = os.getenv("RESILICHAIN_DATABASE", "resilichain.db")
store = StateStore(DATABASE_PATH)
environment = SupplyChainEnvironment(store)
orchestrator = ControlTowerOrchestrator(environment)

app = FastAPI(
    title="ResiliChain AI",
    version="0.2.0",
    description="Multi-agent autonomous retail supply-chain recovery control tower.",
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "resilichain-ai"}


@app.post("/api/scenarios/{scenario_id}/reset")
def reset_scenario(scenario_id: str):
    try:
        return environment.reset(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str):
    try:
        return environment.observe(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/scenarios/{scenario_id}/recover")
def recover_scenario(scenario_id: str):
    try:
        return orchestrator.recover(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")
