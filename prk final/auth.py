from app.config import get_settings
from app.database import Database
from app.repositories.auth_repo import AuthRepository
from app.services.auth_service import AuthService, AuthError


class Auth:
    """Legacy wrapper around the refactored AuthService."""

    def __init__(self) -> None:
        self._service = AuthService(AuthRepository(Database()), get_settings())

    def register(self, username: str, password: str) -> str:
        try:
            self._service.register(username, password)
            return "Registered!"
        except AuthError:
            return "User exists!"

    def login(self, username: str, password: str) -> str:
        token, _ = self._service.login(username, password)
        return token
