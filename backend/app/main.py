"""FootPass API application."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.security import SECURITY_HEADERS
from app.routers import checks, health, images, review, settings as settings_router, stubs

configure_logging("DEBUG" if settings.is_dev else "INFO")
log = get_logger("footpass.api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log.info("startup", extra={"extra": {"version": settings.footpass_version, "env": settings.footpass_env}})
    yield
    log.info("shutdown")


app = FastAPI(
    title="FootPass API",
    version=settings.footpass_version,
    description="Local-first Foot Passport appliance. Not a medical device.",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Local-network use only. In production the proxy is same-origin, so this list
# stays tight; dev adds the Vite origin.
_allowed = ["http://footpass.local", f"http://{settings.footpass_hostname}"]
if settings.is_dev:
    _allowed += ["http://localhost:5173", "http://localhost", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    return response


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    # Never leak internal paths/details to the client (see docs/security.md).
    log.error("unhandled_error", extra={"extra": {"path": request.url.path}}, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "internal error"})


# Routers are mounted under /api; the proxy forwards /api/* here.
app.include_router(health.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(checks.router, prefix="/api")
app.include_router(images.router, prefix="/api")
app.include_router(review.router, prefix="/api")
app.include_router(stubs.router, prefix="/api")
