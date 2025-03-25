"""Healthz router for the API."""

from fastapi import APIRouter


router = APIRouter(prefix="/healthz", tags=["healthz"])


@router.get("/")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}
