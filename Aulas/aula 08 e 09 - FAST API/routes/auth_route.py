from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database.connection import get_session
from models.user_sql_model import User
from security.jwt import gerar_token


router = APIRouter()  # Grupo de rotas de autenticação

# ROTA - gerar o token
@router.post("/token")
def login(
    # Recebe usuário e senha do formulário de login
    form_data: OAuth2PasswordRequestForm = Depends(),  
    session: Session = Depends(get_session)  # Abre uma sessão com o banco
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

    return {
        "access_token": token,  # Token que o cliente vai usar nas próximas requisições
        "token_type": "bearer"  # Tipo do token
    }