from fastapi import APIRouter, Depends
from models.predict_models import PredictRequest, PredictResponse
from security.auth import validar_token_jwt

# Cria o grupo de rotas de predição
router = APIRouter()


# Rota - POST - /predict
# só executa se o token JWT for válido
@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest,     
            username: str = Depends(validar_token_jwt)):

    # resposta fixa (simulação da classificação do ticket)
    return PredictResponse(intent="Technical issue")