from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import config
from app.core.database import init_db
from app.core.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Application starting up...")
    await init_db()
    yield
    print("Application shutting down...")


app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/healthz")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home() -> HTMLResponse:
    return HTMLResponse(
        content="<h1>Welcome!</h1>"
        "<p>It's time to shape your restaurant and grow with us.</p>"
    )
