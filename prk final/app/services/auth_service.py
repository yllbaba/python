from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Tuple

from app.config import Settings
from app.repositories.auth_repo import AuthRepository


class AuthError(Exception):
    pass


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str


class PasswordHasher:
    def __init__(self, pepper: str, iterations: int = 120_000) -> None:
        self.pepper = pepper.encode("utf-8")
        self.iterations = iterations

    def hash_password(self, password: str, salt: bytes) -> str:
        derived_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8") + self.pepper,
            salt,
            self.iterations,
        )
        return derived_key.hex()

    def verify_password(self, password: str, salt_hex: str, expected_hash: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        return self.hash_password(password, salt) == expected_hash


class AuthService:
    def __init__(self, repo: AuthRepository, settings: Settings) -> None:
        self.repo = repo
        self.hasher = PasswordHasher(settings.password_pepper)
        self.token_ttl = settings.auth_token_ttl_minutes

    def register(self, username: str, password: str) -> int:
        existing = self.repo.get_user_by_username(username)
        if existing:
            raise AuthError("Username already exists")
        salt = secrets.token_bytes(16)
        password_hash = self.hasher.hash_password(password, salt)
        return self.repo.create_user(username, password_hash, salt.hex())

    def login(self, username: str, password: str) -> Tuple[str, str]:
        user = self.repo.get_user_by_username(username)
        if not user:
            raise AuthError("Invalid username or password")
        if not self.hasher.verify_password(password, user["password_salt"], user["password_hash"]):
            raise AuthError("Invalid username or password")
        token = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(minutes=self.token_ttl)
        self.repo.update_token(user["id"], token, expires_at.isoformat())
        return token, expires_at.isoformat()

    def authenticate(self, token: str) -> AuthenticatedUser:
        if not token:
            raise AuthError("Missing token")
        user = self.repo.get_user_by_token(token)
        if not user:
            raise AuthError("Invalid token")
        expires_at = user["token_expires_at"]
        if not expires_at:
            raise AuthError("Token expired")
        if datetime.utcnow() > datetime.fromisoformat(expires_at):
            raise AuthError("Token expired")
        return AuthenticatedUser(id=int(user["id"]), username=str(user["username"]))
