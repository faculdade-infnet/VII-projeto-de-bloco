from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from database.connection import get_session
from models.user_sql_model import User
from security.jwt import validar_token


# FUNCAO, pega o usuário logado a partir do token
def get_current_user(
    username: str = Depends(validar_token),  # Valida o token e recebe o nome do usuário de dentro dele
    session: Session = Depends(get_session)  # Abre uma sessão com o banco
):
    statement = select(User).where(
        User.username == username  # Busca o usuário pelo nome que veio no token
    )

    user = session.exec(statement).first()  # Busca e pega o primeiro resultado

    # Se o usuário do token não existe mais no banco
    if user is None:
        raise HTTPException(
            status_code=401,  # Erro de não autorizado
            detail="Usuário não encontrado"
        )

    # Devolve o objeto User do usuário logado
    return user