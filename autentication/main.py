from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services import AuthService
from schemas import UserData, RefreshToken
from errors import CODE_ERROR_MAPPING, ErrorAuth


app = FastAPI()
database = {}
auth_service = AuthService(database=database)


@app.post("/v1/register/")
def register(user: UserData):
    """Endpoint responsável pelo registro de um novo usuário em DB."""

    result = auth_service.register(user=user)

    if result.error:
        return JSONResponse(status_code=CODE_ERROR_MAPPING[result.error], content={"error": result.error.value})

    return JSONResponse(status_code=201, content={"message": result.message})


@app.post("/v1/authenticate/")
def authenticate(user: UserData):
    """Endpoint responsável pela autenticação de um usuario cadastrado em DB."""

    authentication = auth_service.authenticate(user=user)

    if authentication.error:
        return JSONResponse(status_code=CODE_ERROR_MAPPING[authentication.error], content={"error": authentication.error.value})

    return JSONResponse(status_code=200, content={"access_token": authentication.access_token, "refresh_token": authentication.refresh_token})


@app.post("/v1/refresh/")
def refresh(payload: RefreshToken):
    """Endpoint responsável por gerar um novo access token com expiration válido."""

    refresh = auth_service.refresh(refresh_token=payload.refresh_token)

    if refresh.error:
        return JSONResponse(status_code=CODE_ERROR_MAPPING[refresh.error], content={"error": refresh.error.value})

    return JSONResponse(status_code=200, content={"message": refresh.message, "access_token": refresh.access_token})


@app.get("/v1/profile/")
def profile(request: Request):
    """Endpoint exemplo para validação do JWT em rotas protegidas."""

    bearer_token = request.headers.get("Authorization") # Header de autorização

    if not bearer_token:
        return JSONResponse(status_code=CODE_ERROR_MAPPING[ErrorAuth.INVALID_CREDENTIALS], content={"error": ErrorAuth.INVALID_CREDENTIALS.value})

    access_token = bearer_token.split(" ")[1] # debt: deveria ser parseado
    subject = auth_service.authorize(access_token=access_token)

    if subject.error:
        return JSONResponse(status_code=CODE_ERROR_MAPPING[subject.error], content={"error": subject.error.value})

    return JSONResponse(status_code=200, content={"message": subject.message, "subject": subject.subject})
