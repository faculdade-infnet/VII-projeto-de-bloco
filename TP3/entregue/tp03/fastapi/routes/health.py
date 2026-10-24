from fastapi import APIRouter

# Grupo de rotas de verificação da API
router = APIRouter()


# ROTA - GET - /health - usa-se para verificAR se a API está no ar e funcionando
@router.get("/health", summary="Status da Aplicação")
def health_check():    
    return {"status": "ok"}