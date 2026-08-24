from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "chave-secreta-troque-em-producao"
ALGORITHM = "HS256"

# Usuário admin definido in-code (único com acesso à API)
USUARIO_FAKE = {
    "username": "admin",
    "password": "admin"
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def login_form(
    username: str = Form(..., examples=[""], description="Insira o nome do usuário(admin)"),
    password: str = Form(..., examples=[""], description="Insira a senha do usuário(admin)")
):
    return {"username": username, "password": password}

def gerar_token(username: str):
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)

    dados = {
        "sub": username,
        "exp": expiracao
    }

    token = jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def validar_token_jwt(token: str = Depends(oauth2_scheme)):
    erro = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise erro
    except InvalidTokenError:
        raise erro

    return username

