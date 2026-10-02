from fastapi import APIRouter, HTTPException, Depends
from models.auth_models import Token
from security.auth import USUARIO_FAKE, gerar_token, login_form

# grupo de rotas de autenticação
router = APIRouter()


# ROTA - POST - /auth/token - Recebe usuário e senha e devolve o token JWT
@router.post("/auth/token", response_model=Token, status_code=200)
def login(form_data: dict = Depends(login_form)):
    username, password = form_data

    # Confere se o usuário e a senha são iguais aos do admin definido in-code
    if (form_data["username"] != USUARIO_FAKE["username"]
        or form_data["password"] != USUARIO_FAKE["password"]):
        
        # Se erro
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    # Se correto, gera o token JWT para o usuário
    token = gerar_token(form_data["username"])

    # Retorna o token
    return {
        "access_token": token,
        "token_type": "bearer"
    }