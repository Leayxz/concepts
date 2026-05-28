from enum import Enum

class ErrorAuth(Enum):
    USER_ALREADY_EXISTS = "User already exists."
    USER_NOT_FOUND = "User not found."
    INVALID_CREDENTIALS = "Invalid credentials."
    TOO_MANY_REQUESTS = "Too many requests. Retry after 60 seconds."


CODE_ERROR_MAPPING = {
    ErrorAuth.USER_ALREADY_EXISTS: 409,
    ErrorAuth.USER_NOT_FOUND: 404,
    ErrorAuth.INVALID_CREDENTIALS: 401,
}
