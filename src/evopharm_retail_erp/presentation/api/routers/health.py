"""Health check API router."""
from __future__ import annotations

from fastapi import APIRouter
from ..schemas.health import HealthResponse

router = APIRouter(tags=["System / Health"])


@router.get("/health", response_model=HealthResponse, summary="Process Health Check")
async def health_check() -> HealthResponse:
    """Minimal health check endpoint indicating API process status."""
    return HealthResponse(status="ok")
