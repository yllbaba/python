from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings
from app.database import Database
from app.repositories.auth_repo import AuthRepository
from app.repositories.player_repo import PlayerRepository
from app.repositories.stats_repo import StatsRepository
from app.services.auth_service import AuthService, AuthenticatedUser, AuthError
from app.services.stats_service import StatsService

security = HTTPBearer(auto_error=False)


def get_database() -> Database:
    return Database()


def get_auth_service(db: Database = Depends(get_database)) -> AuthService:
    return AuthService(AuthRepository(db), get_settings())


def get_stats_service(db: Database = Depends(get_database)) -> StatsService:
    return StatsService(StatsRepository(db), PlayerRepository(db))


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    try:
        return auth_service.authenticate(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
