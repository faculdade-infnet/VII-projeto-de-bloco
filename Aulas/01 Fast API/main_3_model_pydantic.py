from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

# "Banco de dados" temporário em memória
produtos = [
    {"id": 1, "nome": "Notebook", "preco": 3500.0},
    {"id": 2, "nome": "Mouse", "preco": 100.0},
    {"id": 3, "nome": "Tecaldo", "preco": 150.0}
]

# Necessário ao usar o pydantic, no endpoint POST 
class Produto(BaseModel):
    nome: str
    preco: float


# Endpoint GET que busca um produto específico pelo id
@app.get("/produtos/{produto_id}")
def buscar_produto(produto_id: int):
    for produto in produtos:
        if produto["id"] == produto_id:
            return produtos

    # Se não encontrar, retorna erro 404 corretamente
    raise HTTPException(
        status_code=404,
        detail="Produto não encontrado"
    )

# Endpoint GET que lista um número X de produtos com a variável "limite"
@app.get("/listar_produtos")
def listar_produtos(limite: int = 10):
 return produtos[:limite]

# Endpoint POST que cria um novo produto
@app.post("/produto", status_code=201)
async def criar_produto(request: Produto):    

    novo_produto = {
        "id": len(produtos) + 1,
        "nome": request.nome,
        "preco": request.preco
    }

    produtos.append(novo_produto)    
    return novo_produto