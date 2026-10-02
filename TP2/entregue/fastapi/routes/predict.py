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
@router.get("/predictions/{prediction_id}", summary="Obter previsão pelo ID")
def get_prediction(prediction_id: int,
                   session: Session = Depends(get_session),
                    current_user: User = Depends(get_current_user)
):
    # seleciona pelo id da previsao e pelo usuario logado
    statement = select(Prediction).where(
        Prediction.id == prediction_id,
        Prediction.owner_id == current_user.id
    )

    prediction = session.exec(statement).first()  # primeira previsao encontrada
    # Se não achou, ou se a previsão é de outro usuário
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")
    
    return prediction


# ROTA - Faz a previsão da intenção (protegida)
@router.post("/predict", summary="Fazer previsão pela intenção da mensagem")
def predict(predictionRequest: PredictionRequest,  
    current_user: User = Depends(get_current_user)
):
    predictionResponse = PredictionResponse(
        message=predictionRequest.message,  # Devolve a mesma mensagem recebida
        intent="Technical issue"  # Intenção fixa por enquanto, sem modelo de verdade
    )

    # Resposta com mensagem e intenção
    return predictionResponse


# ROTA - Lista todas as previsões (só para o admin)
@router.get("/predictions", summary="Obtém todas as previsões do usuário logado")
def get_all_predictions(session: Session = Depends(get_session),  
    current_user: User = Depends(get_current_user)
    ): 
    # Só as previsões do usuário logado
    statement = select(Prediction).where(
        Prediction.owner_id == current_user.id
    )

    # Devolve a lista de previsões
    return session.exec(statement).all()