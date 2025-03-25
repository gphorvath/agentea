from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .routers.healthz import healthz_router


app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    """Intercepts the root path and redirects to the API documentation."""
    return RedirectResponse(url="/docs")

app.include_router(healthz_router)