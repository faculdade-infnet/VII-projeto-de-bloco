from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from database.connection import get_session
from models.user_sql_model import User
from security.jwt import validar_token


def get_current_user(
    username: str = Depends(validar_token),
    session: Session = Depends(get_session)
):
    statement = select(User).where(
        User.username == username
    )

    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    return user