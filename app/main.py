from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.v1.endpoints.auth import router as auth_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()


# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     print("Application starting up...")
#     await init_db()
#     yield
#     print("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(auth_router, prefix=settings.API_PREFIX)


@app.get("/healthz")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home() -> HTMLResponse:
    return HTMLResponse(
        content="<h1>Welcome!</h1>"
        "<p>It's time to shape your restaurant and grow with us.</p>"
    )
