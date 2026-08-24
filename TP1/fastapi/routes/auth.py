from fastapi import APIRouter, HTTPException, Depends
from models.auth_models import Token
from security.auth import USUARIO_FAKE, gerar_token, login_form

router = APIRouter()


@router.post("/auth/token", response_model=Token, status_code=200)
def login(form_data: dict = Depends(login_form)):
    username, password = form_data

    if (
        form_data["username"] != USUARIO_FAKE["username"]
        or form_data["password"] != USUARIO_FAKE["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    token = gerar_token(form_data["username"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }