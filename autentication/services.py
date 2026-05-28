import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

from schemas import UserData
from dtos import AuthResult
from errors import ErrorAuth

SECRET_KEY = "senha-secreta-vinda-do-env"

class AuthService:
    """Serviço responsável pelo registro e autenticação do usuário."""

    def __init__(self, database) -> None:
        self._database = database


    def register(self, user: UserData) -> AuthResult:
        """Use case para registrar um novo usuário no sistema."""

        # Valida se já existe email cadastrado no banco de dados
        if user.email in self._database:
            return AuthResult(error=ErrorAuth.USER_ALREADY_EXISTS)

        # Hash da senha e persistência em banco de dados
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        self._database[user.email] = hashed_password

        return AuthResult(message="User created.")


    def authenticate(self, user: UserData):
        """Use case para autenticar o usuário e permitir acesso ao sistema."""

        # Valida se o email está cadastrado no banco de dados
        if user.email not in self._database:
            return AuthResult(error=ErrorAuth.USER_NOT_FOUND)

        # Valida se a senha persistida é igual a senha fornecida
        if not bcrypt.checkpw(user.password.encode("utf-8"), self._database[user.email]):
            return AuthResult(error=ErrorAuth.INVALID_CREDENTIALS)

        # Geração do access token
        access_payload = {"sub": user.email, "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")

        # Geração do refresh token
        refresh_payload = {"sub": user.email, "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(days=30)}
        refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

        return AuthResult(access_token=access_token, refresh_token=refresh_token)


    def authorize(self, access_token: str) -> AuthResult:
        """Use case responsável por validar o access token corretamente para proteção de dados e rotas."""

        try:
            # Validação para não permitir que autenticação seja feita usando o refresh token
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])

            if payload["type"] != "access": # debt: padronizar em objeto?
                return AuthResult(error=ErrorAuth.INVALID_CREDENTIALS)

            return AuthResult(message="Rota protegida com sucesso. Usuário possui autenticação válida.", subject=payload["sub"])

        except:
            return AuthResult(error=ErrorAuth.INVALID_CREDENTIALS)


    def refresh(self, refresh_token: str):
        """Use case responsável por validar o refresh token e gerar um novo access token por tempo determinado."""

        try:
            # Validação para não permitir que novos tokens sejam assinados usando um access ativo
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

            if payload["type"] != "refresh": # debt: padronizar em objeto?
                return AuthResult(error=ErrorAuth.INVALID_CREDENTIALS)

            # Novo payload com expiração renovada
            new_payload = {"sub": payload["sub"], "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
            new_access = jwt.encode(new_payload, SECRET_KEY, algorithm="HS256")

            return AuthResult(message="Access Token renovado com sucesso.", access_token=new_access)

        except:
            return AuthResult(error=ErrorAuth.INVALID_CREDENTIALS)
