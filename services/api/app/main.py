"""Rozlicz API - FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.config import settings
from app.database import engine, init_db
from app.routers import auth, billing, documents, taxes

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("rozlicz_api_starting", version="0.1.0")
    await init_db()
    yield
    # Shutdown
    logger.info("rozlicz_api_shutting_down")
    await engine.dispose()


app = FastAPI(
    title="Rozlicz API",
    description="Automated accounting service for Polish e-commerce JDG",
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(taxes.router, prefix="/taxes", tags=["taxes"])


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "rozlicz-api"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Rozlicz API",
        "version": "0.1.0",
        "docs": "/docs",
    }
