import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "chave-secreta-troque-em-producao" # Chave usada para assinar e validar o token JWT
ALGORITHM = "HS256"         # Algoritmo de assinatura do token

# Usuário admin definido in-code (único com acesso à API)
USUARIO_FAKE = {
    "username": "admin",
    "password": "admin"
}

# Define que o token será enviado no cabeçalho como "Bearer" e que ele é obtido na rota auth/token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Recebe o usuário e a senha pelo formulário da rota de login
def login_form(
    username: str = Form(..., examples=[""], description="Insira o nome do usuário(admin)"),
    password: str = Form(..., examples=[""], description="Insira a senha do usuário(admin)")
):
    return {"username": username, "password": password}

# Gera o token JWT depois que o login é feito com sucesso
def gerar_token(username: str):    
    expiracao = datetime.now(timezone.utc) + timedelta(minutes=30) # tempo expiracao do token 30 minutos

    # Dados do token (usuario, data e hora de expiracao)
    dados = {
        "sub": username,
        "exp": expiracao
    }

    # Cria o token assinado com a chave secreta
    token = jwt.encode(
        dados,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# FUNCAO - Valida o token enviado nas rotas protegidas
def validar_token_jwt(token: str = Depends(oauth2_scheme)):
    # Erro 401 retornado quando o token não é válido
    erro = HTTPException(
        status_code=401,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # Decodifica o token e confere a assinatura e a expiração
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # nome do usuário salvo no token
        username = payload.get("sub")

        # Só o admin definido in-code pode acessar
        if username is None or username != USUARIO_FAKE["username"]:
            raise erro

    # Se o token for inválido, alterado ou expirado, retorna erro 401
    except InvalidTokenError:
        raise erro

    return username