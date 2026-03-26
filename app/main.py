from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/healthz")
async def read_root() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home() -> HTMLResponse:
    return HTMLResponse(
        content="<h1>Welcome!</h1>"
        "<p>It's time to shape your restaurant and grow with us.</p>"
    )
