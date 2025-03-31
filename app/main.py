from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .routers import agents_router, healthz_router, debug_router
from .utils.db import postgres

app = FastAPI()


@app.get("/", include_in_schema=False)
async def root():
    """Intercepts the root path and redirects to the API documentation."""
    return RedirectResponse(url="/docs")


@app.on_event("startup")
async def startup_db_client():
    """Initialize database connection on startup."""
    await postgres.init_db()


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection on shutdown."""
    await postgres.close_db()


app.include_router(agents_router)
app.include_router(healthz_router)
app.include_router(debug_router)
