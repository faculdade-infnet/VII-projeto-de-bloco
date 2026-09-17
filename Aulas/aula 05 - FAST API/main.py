# arquivo repositório da aula
# https://github.com/professortiagoinfnet/analisesegurancaagentesia_projetobloco/blob/main/etapa_1_2/main_v2_jwt.py
import jwt
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, Field

### SETUP ###
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token_jwt")

USUARIO_FAKE = {"username": "admin","password": "admin"}
TOKEN_FAKE = "token-fake-admin"
SECRET_KEY = "CHAVE SECRETA"


### "Banco de dados" temporário em memória ###
produtos = [
    {
        "id": 1,
        "nome": "Notebook",
        "preco": 3500.0,
        "categoria": "Eletrônico",
        "descricao": "Notebook com processador Intel Core i7, 16GB de RAM e 512GB SSD",
        "disponivel": True
    },
    {
        "id": 2,
        "nome": "Mouse",
        "preco": 100.0,
        "categoria": "Periféricos",
        "descricao": "Mouse ergonômico com sensor óptico",
        "disponivel": True
    },
    {
        "id": 3,
        "nome": "Teclado",
        "preco": 150.0,
        "categoria": "Periféricos",
        "descricao": "Teclado mecânico com switches azuis",
        "disponivel": True
    }
]


### FUNÇÕES ###
# Pega o token que veio na requisição (o Depends(oauth2_scheme) já extrai isso do cabeçalho Authorization) e compara com o token fixo TOKEN_FAKE. Se for diferente, retorna erro 401. Se for igual, deixa passar. É a versão "simples" de validação, sem JWT.
def validar_token(token: str = Depends(oauth2_scheme)):

    if token != TOKEN_FAKE:
        raise HTTPException(
            status_code=401,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token

# Recebe o nome do usuário e monta um JWT de verdade: define que o token expira em 30 minutos, coloca o username dentro do token (sub) e assina tudo com a SECRET_KEY. O resultado é a string do token que vai ser devolvida pro cliente.
def gerar_token(username: str):

    expiracao = datetime.now(timezone.utc) + timedelta(minutes=30)

    dados = {
        "sub": username,
        "exp": expiracao
    }

    token = jwt.encode(
        dados,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token

# É a versão "de verdade" da validação. Tenta decodificar o token usando a mesma SECRET_KEY. Se o token foi adulterado, expirou, ou tá mal formado, o jwt.decode já dispara InvalidTokenError, e aí cai no erro 401. Se der certo, pega o username de dentro do token e retorna ele.
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
            algorithms=["HS256"]
        )

        username = payload.get("sub")

        if username is None:
            raise erro

    except InvalidTokenError:
        raise erro

    return username


### MODELOS pydantic ###
class Produto(BaseModel):    
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0 )
    categoria: str
    descricao: str | None = None
    disponivel : bool = True


### Endpoint - GET - teste de aplicação ### 
@app.get("/")
def home():
    return {"mensagem": "Minha primeira API com FastAPI"}


### Endpoint - GET - busca todos os produtos ###
@app.get("/produtos", summary="Listar Produtos",
    description="Retorna a lista completa de produtos cadastrados")
def listar_produtos():
    return produtos


# Endpoint - GET - busca um produto específico pelo id do produto
@app.get("/produtos/{id}", summary="Bucara produto por ID", 
         description="Busca um produto pelo seu ID")
def buscar_produto(id: int):
    for item in produtos:
        if item["id"] == id:
            return item

    # Se não encontrar, retorna erro 404
    raise HTTPException(
        status_code=404,
        detail="Produto não encontrado"
    )

# Endpoint - GET - lista um número X de produtos definido pela variável "limite"
@app.get("/listar_produtos_limite", summary="Listar Produtos (X itens)",
    description="Retorna uma lista com uma quantidade limite de produtos cadastrados")
def listar_produtos(limite: int = 10):
    return produtos[:limite]


# Endpoint - POST - cria um novo produto com o modelo pydantic
@app.post("/produtos_pydantic", status_code=201, 
          summary="Criar Produto", description="Cria um produto usando um modelo Pydantic")
async def criar_produto(item: Produto):

    novo_produto = {
        "id": len(produtos) + 1,
        "nome": item.nome,
        "preco": item.preco,
        "categoria": item.categoria,
        "descricao": item.descricao,
        "disponivel": item.disponivel
    }

    produtos.append(novo_produto)
    return novo_produto


# É igual à rota /listar_produtos_limite, mas protegida: antes de executar a função, o FastAPI roda validar_token_jwt. Se o token não for válido, nem chega a executar o corpo da função — já retorna 401 direto.
# Endpoint - GET - lista um número X de produtos definido pela variável "limite" porem somente se o token for válido
@app.get("/listar_produtos_limite_protegido", 
         summary="Listar Produtos (X itens) somente se autenticado", 
         description="Retorna uma lista com uma quantidade limite de produtos somente se o usuário estiver autenticado")
def listar_produtos(limite: int = 10, token: str = Depends(validar_token_jwt)):
    return produtos[:limite]


# É a rota de login que gera o token real. Recebe usuário e senha (via OAuth2PasswordRequestForm), confere se batem com USUARIO_FAKE. Se estiver certo, chama gerar_token pra criar o JWT e devolve ele no formato padrão {access_token, token_type}. É essa rota que o oauth2_scheme aponta (tokenUrl="/token_jwt") — por isso o Swagger sabe onde buscar o token quando você clica em "Authorize".
# Endpoint - GET - faz o login com usuário e senha
@app.post("/token_jwt", summary="Login", description="Faz o login gerando um token se usuário e senha forem válidos")
def login(form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm )):

    if (
        form_data.username != USUARIO_FAKE["username"]
        or form_data.password != USUARIO_FAKE["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )

    token = gerar_token(form_data.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }