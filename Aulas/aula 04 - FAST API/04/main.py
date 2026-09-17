# arquivo repositório da aula
# https://github.com/professortiagoinfnet/analisesegurancaagentesia_projetobloco/blob/main/etapa_1_2/main_v0.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

### SETUP ###
app = FastAPI()

### Necessário ao usar o pydantic, no endpoint POST ###
class Produto(BaseModel):    
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0 )
    categoria: str
    descricao: str | None = None
    disponivel : bool = True

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

### Endpoint - GET - teste de aplicação ### 
@app.get("/")
def home():
    return {"mensagem": "Minha primeira API com FastAPI"}


### Endpoint - GET - busca todos os produtos ###
@app.get("/produtos", summary="Listar Produtos",
    description="Retorna a lista completa de produtos cadastrados")
def listar_produtos():
    return produtos


# Endpoint - POST - cria um novo produto
@app.post("/produtos", status_code=201, summary="Criar Produto", 
        description="Cria uma produto com JSON",
        openapi_extra={
            "requestBody": {
                "content": {
                    "application/json": {
                        "example": {
                            "nome": "Notebook",
                            "preco": 3500.00
                        }
                    }
                }
            }
        }
)
async def criar_produto(request: Request):
    produto = await request.json()

    novo_produto = {
        "id": len(produtos) + 1,
        "nome": produto["nome"],
        "preco": produto["preco"]
    }

    produtos.append(novo_produto)
    return novo_produto


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
    description="Retorna uma lista com uma quantidade limiete de produtos cadastrados")
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