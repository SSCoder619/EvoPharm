"""API request and response schemas for system health check."""
from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Minimal health check response."""

    status: str = Field(default="ok", description="Service health indicator")
