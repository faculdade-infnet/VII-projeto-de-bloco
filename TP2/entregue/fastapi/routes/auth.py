from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select
from database.connection import get_session
from models.auth_models import Token
from models.user_sql_model import User
from security.jwt import gerar_token


router = APIRouter(prefix="/auth")   # Grupo de rotas de autenticação
limiter = Limiter(key_func=get_remote_address) 

# ROTA - gerar o token (POST /auth/token)
# RATE LIMIT: no máximo 10 requisições por minuto por cliente (IP). A 11ª recebe erro 429.
# Justificativa: um usuário de verdade dificilmente erra a senha mais de 10 vezes em 1 minuto,
# então o limite não atrapalha o uso normal. Já um ataque de força bruta precisa testar muitas
# senhas bem rápido. Com o limite, o atacante fica preso a 10 tentativas por minuto.
@router.post("/token", summary="Login", response_model=Token)
@limiter.limit("10/minute")
def login(
    request: Request,  # Obrigatório: o SlowAPI precisa da requisição para saber o IP do cliente
    # Recebe usuário e senha do formulário de login
    form_data: OAuth2PasswordRequestForm = Depends(),  
    session: Session = Depends(get_session) 
):
    statement = select(User).where(
        User.username == form_data.username  # Busca o usuário pelo nome
    )

    user = session.exec(statement).first()  # Busca e pega o primeiro resultado
    
    # Se o usuário existe e se a senha está correta
    if user is None or user.password != form_data.password:  
        raise HTTPException(
            status_code=401, 
            detail="Usuário ou senha inválidos"
        )

    token = gerar_token(user.username)  # Gera o token JWT para o usuário

    return {"access_token": token, "token_type": "bearer"}