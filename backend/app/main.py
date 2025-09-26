from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import auth, pumps, results, scenarios, system_curves

app = FastAPI(title="Hydraulic Toolbox API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(pumps.router)
app.include_router(system_curves.router)
app.include_router(scenarios.router)
app.include_router(results.router)
app.mount("/files", StaticFiles(directory="data/exports"), name="exports")

