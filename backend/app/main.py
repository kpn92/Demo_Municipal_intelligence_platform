from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Phase 1 - Cleanliness & Waste Collection MVP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} API is running",
        "version": settings.app_version
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )
        row = result.fetchone()

    return {
        "database": row[0],
        "user": row[1],
        "connection": "successful"
    }


@app.get("/api/v1/public-config")
def public_config():
    return {
        "frontend_base_url": settings.frontend_base_url,
        "google_maps_api_key": settings.google_maps_api_key or "",
    }

app.include_router(api_router, prefix="/api/v1")
