from fastapi import APIRouter, Depends

from models.predict_models import PredictRequest, PredictResponse
from security.auth import validar_token_jwt

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, username: str = Depends(validar_token_jwt)):
    
    return PredictResponse(intent="Usuário autenticado\nRetorno rota \predict")