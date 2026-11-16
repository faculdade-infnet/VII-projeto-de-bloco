from fastapi import APIRouter


router = APIRouter(tags=["Saúde"])  # Grupo de rotas de previsão

# ROTA - raiz da API, usada para conferir se a aplicação está no ar
@router.get("/helth", summary="Status da API",
             description="""
Verifica se a API está no ar.

**Autenticação:** rota **pública**, não precisa de token.

**Como testar:** clique em **Try it out** e depois em **Execute**.

**Respostas:**
- `200`: a API está no ar → `{"message": "ok"}`
"""                                              # ← texto completo (aparece ao abrir a rota)
)
@router.get("/", include_in_schema=False)   # "/" continua respondendo, mas não aparece no /docs
def helth():
    return {"message": "ok"}