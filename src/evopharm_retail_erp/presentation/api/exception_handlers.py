"""Centralized API exception handlers for mapping domain and application exceptions to standard HTTP responses."""
from __future__ import annotations

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("evopharm.api.exceptions")


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the FastAPI application."""

    @app.exception_handler(KeyError)
    async def key_error_handler(request: Request, exc: KeyError) -> JSONResponse:
        msg = str(exc).strip("'")
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Resource not found: {msg}",
                    "details": None,
                }
            },
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        msg = str(exc)
        if "stale" in msg.lower() or "conflict" in msg.lower() or "already exists" in msg.lower():
            status = 409
            code = "STATE_CONFLICT"
        else:
            status = 400
            code = "INVALID_REQUEST"

        return JSONResponse(
            status_code=status,
            content={
                "error": {
                    "code": code,
                    "message": msg,
                    "details": None,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        exc_name = exc.__class__.__name__
        msg = str(exc)

        # Categorize known domain/application exceptions dynamically by name
        if "NotFound" in exc_name:
            status = 404
            code = "RESOURCE_NOT_FOUND"
        elif "Already" in exc_name or "Duplicate" in exc_name or "Conflict" in exc_name:
            status = 409
            code = "RESOURCE_CONFLICT"
        elif "Invalid" in exc_name or "Error" in exc_name and not exc_name.endswith("ServerError"):
            status = 400
            code = "BAD_REQUEST"
        else:
            logger.error("Unhandled API exception: %s: %s", exc_name, msg, exc_info=True)
            status = 500
            code = "INTERNAL_SERVER_ERROR"
            msg = "An internal server error occurred."

        return JSONResponse(
            status_code=status,
            content={
                "error": {
                    "code": code,
                    "message": msg,
                    "details": None,
                }
            },
        )
