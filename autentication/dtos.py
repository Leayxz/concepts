from dataclasses import dataclass
from errors import ErrorAuth


@dataclass
class AuthResult:
    subject: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    message: str | None = None
    error: ErrorAuth | None = None
