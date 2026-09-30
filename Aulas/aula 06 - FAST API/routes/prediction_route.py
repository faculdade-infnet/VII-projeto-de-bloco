from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.connection import get_session
from models.prediction_request_model import PredictionRequest
from models.prediction_response_model import PredictionResponse
from models.prediction_sql_model import Prediction
from models.user_sql_model import User
from security.dependencies import get_current_user

router = APIRouter()  # Grupo de rotas de previsão

# ROTA - Busca previsão pelo ID
@router.get("/predictions/{prediction_id}")  
def get_prediction(
    prediction_id: int,  # Id da previsão vindo da URL
    session: Session = Depends(get_session),  # Abre uma sessão com o banco
    current_user: User = Depends(get_current_user)  # Pega o usuário logado a partir do token
):
    statement = select(Prediction).where(
        Prediction.id == prediction_id,  # Filtra pelo id da previsão
        Prediction.owner_id == current_user.id  # Garante que a previsão é do usuário logado
    )

    prediction = session.exec(statement).first()  # Busca e pega o primeiro resultado
    # Se não achou, ou se a previsão é de outro usuário
    if prediction is None:  
        raise HTTPException(status_code=404, detail="Prediction não encontrada") 

    # Devolve a previsão encontrada
    return prediction

# ROTA - Faz a previsão da intenção
@router.post("/predict")
def predict(predictionRequest: PredictionRequest):  # Recebe a mensagem no formato do PredictionRequest
    predictionResponse = PredictionResponse(
        message=predictionRequest.message,  # Devolve a mesma mensagem recebida
        intent='cancelamento'  # Intenção fixa por enquanto, sem modelo de verdade
    )

    # Retorna a resposta com a mensagem e a intenção
    return predictionResponse