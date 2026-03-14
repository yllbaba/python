from __future__ import annotations

from fastapi import FastAPI

from app.api.auth_routes import router as auth_router
from app.api.stats_routes import router as stats_router
from app.config import get_settings
from app.database import Database


def create_app() -> FastAPI:
    settings = get_settings()
    Database(settings.db_path).init_db()

    app = FastAPI(title=settings.app_name)
    app.include_router(auth_router)
    app.include_router(stats_router)

    @app.get("/")
    def root() -> dict:
        return {"message": f"{settings.app_name} API"}

    return app


app = create_app()
