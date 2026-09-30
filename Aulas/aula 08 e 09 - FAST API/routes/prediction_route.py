from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select
from database.connection import get_session
from models.prediction_request_model import PredictionRequest
from models.prediction_response_model import PredictionResponse, PredictionValid
from models.prediction_sql_model import Prediction
from models.user_sql_model import User
from security.dependencies import get_current_user

router = APIRouter()  # Grupo de rotas de previsão
limiter = Limiter(key_func=get_remote_address)  # Limitador de requisições, identifica o cliente pelo IP

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

# ROTA - Valida a mensagem (válida se tiver mais de 5 caracteres)
@router.post("/valid")
def valid(predictionRequest: PredictionRequest):  # Recebe a mensagem no formato do PredictionRequest
    predictionResponse = PredictionValid(
        message=predictionRequest.message,  # Devolve a mesma mensagem recebida
        valid='Válido' if len(predictionRequest.message) > 5 else "Inválido"
    )

    # Retorna a resposta com a mensagem e o resultado da validação
    return predictionResponse

# ROTA - Lista todas as previsões (só para o admin)
@router.get("/predicitons")
def get_all_predicitons(
    session: Session = Depends(get_session),  # Abre uma sessão com o banco
    current_user: User = Depends(get_current_user)):  # Pega o usuário logado a partir do token
    # Só o admin (id 1) pode listar todas
    if current_user.id != 1:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")

    statement = select(Prediction).where(
        Prediction.owner_id > 0
    )

    predictions = session.exec(statement).fetchall()  # Busca todas as previsões

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")

    # Devolve a lista de previsões
    return predictions

# ROTA - Lista todas as previsões com limite de 5 requisições por minuto
@router.get("/predicitons_limited")
@limiter.limit("5/minute")  # A 6ª requisição no mesmo minuto recebe erro 429
def get_all_predicitons_limited(
    request: Request,  # Obrigatório: o SlowAPI precisa da requisição
    session: Session = Depends(get_session),  # Abre uma sessão com o banco
    current_user: User = Depends(get_current_user)):  # Pega o usuário logado a partir do token
    # Só o admin (id 1) pode listar todas
    if current_user.id != 1:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")

    statement = select(Prediction).where(
        Prediction.owner_id > 0
    )

    predictions = session.exec(statement).fetchall()  # Busca todas as previsões

    if len(predictions) == 0:
        raise HTTPException(status_code=404, detail="Prediction não encontrada")

    # Devolve a lista de previsões
    return predictions
