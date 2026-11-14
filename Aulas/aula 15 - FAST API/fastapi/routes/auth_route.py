from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from database.connection import get_session
from models.user_sql_model import User
from security.jwt import gerar_token


router = APIRouter(tags=["Autenticação"])  # Grupo de rotas de autenticação


# -----------------------------------------------------------------------------------------------------
# ROTA - gerar o token
@router.post("/token", summary="Fazer login e gerar o token JWT",
             description="""
Faz o login do usuário e gera o **token JWT** usado nas rotas protegidas.

**Autenticação:** não precisa de token (é aqui que ele é gerado).

**Como testar:**
1. Clique em **Try it out**
2. Preencha `username` e `password` (ex.: `admin` / `admin` ou `jose` / `1234`)
3. Clique em **Execute** e copie o `access_token`
4. No topo da página, clique em **Authorize** e faça o login para liberar as rotas com cadeado

**Detalhes:**
- O token vale por **30 minutos**
- Deve ser enviado no cabeçalho `Authorization: Bearer <token>`

**Respostas:**
- `200`: login correto → `{"access_token": "...", "token_type": "bearer"}`
- `401`: usuário ou senha inválidos
""")
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