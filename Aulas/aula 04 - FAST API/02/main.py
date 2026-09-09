from fastapi import FastAPI, HTTPException

app = FastAPI()

# "Banco de dados" temporário em memória
produtos = [
    {
        "id": 1,
        "nome": "Notebook",
        "preco": 3500.0
    },
    {
        "id": 2,
        "nome": "Mouse",
        "preco": 100.0
    }
]


@app.get("/")
def home():
    return {"mensagem": "Minha primeira API"}


# Endpoint GET que lista todos os produtos
@app.get("/produtos")
def listar_produtos():
    return produtos


# Endpoint GET que busca um produto específico pelo id
@app.get("/produtos/{produto_id}")
def buscar_produto(produto_id: int):
    for produto in produtos:
        if produto["id"] == produto_id:
            return produto

    # Se não encontrar, retorna erro 404 corretamente
    raise HTTPException(
        status_code=404,
        detail="Produto não encontrado"
    )