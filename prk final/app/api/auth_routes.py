from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_auth_service, get_current_user
from app.schemas.auth_schema import TokenResponse, UserLogin, UserRegister
from app.services.auth_service import AuthService, AuthError, AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegister, auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    try:
        user_id = auth_service.register(payload.username, payload.password)
        return {"user_id": user_id, "message": "Registered"}
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    try:
        token, expires_at = auth_service.login(payload.username, payload.password)
        return TokenResponse(token=token, expires_at=expires_at)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me")
def me(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {"id": current_user.id, "username": current_user.username}
