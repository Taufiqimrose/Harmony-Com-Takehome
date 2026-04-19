"""FastAPI entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.pipeline.forms_assets import warm_cache_on_startup
from src.routes import jobs
from src.settings import settings


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await warm_cache_on_startup()
    yield


app = FastAPI(title="Title Transfer API", version="0.1.0", lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)

static_dir = Path(__file__).resolve().parent / "static"
if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
