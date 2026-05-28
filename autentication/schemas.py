from pydantic import BaseModel, EmailStr

class UserData(BaseModel):
    "Validação de entrada para cadastro e login."

    email: EmailStr
    password: str


class RefreshToken(BaseModel):
    "Validação de entrada para o refresh token."
    refresh_token: str
