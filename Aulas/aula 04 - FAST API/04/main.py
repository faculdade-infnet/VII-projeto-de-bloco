from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# "Banco de dados" temporário em memória
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

# Necessário ao usar o pydantic, no endpoint POST 
class Produto(BaseModel):    
    nome: str = Field(min_length=2)
    preco: float = Field(gt=0 )
    categoria: str
    descricao: str | None = None
    disponivel : bool = True



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
@app.post("/criar_produto", status_code=201)
async def criar_produto(request: Produto):    
    novo_produto = {
        "id": len(produtos) + 1,
        "nome": request.nome,
        "preco": request.preco,
        "categoria": request.categoria,
        "descricao": request.descricao,
        "disponivel": request.disponivel
    }
    produtos.append(novo_produto)
    return novo_produto