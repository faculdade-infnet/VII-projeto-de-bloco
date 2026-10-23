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

router = APIRouter(tags=["Previsões"])  # Grupo de rotas de previsão
limiter = Limiter(key_func=get_remote_address)  # Limitador de requisições, identifica o cliente pelo IP


# ------------------------------------------------------------------------------------------------------
# ROTA - Busca previsão pelo ID
@router.get("/predictions/{prediction_id}", summary="Buscar uma previsão do usuário logado", 
            description="""
Busca uma previsão salva pelo **ID**.

**Autenticação:** precisa de token (clique em **Authorize** antes).

**Regra de acesso:** só devolve a previsão se ela pertencer ao **usuário logado**.
Se a previsão for de outro usuário, a API responde como se ela não existisse (`404`).

**Como testar:**
1. Faça login no **Authorize** (ex.: `admin` / `admin`)
2. Clique em **Try it out**, informe o `prediction_id` (ex.: `1`) e clique em **Execute**

**Respostas:**
- `200`: previsão encontrada → `{"id": 1, "text": "...", "intent": "...", "owner_id": 1}`
- `401`: sem token, token inválido ou expirado
- `404`: previsão não existe ou é de outro usuário
""")
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


# -----------------------------------------------------------------------------------------------------
# ROTA - Faz a previsão da intenção
@router.post("/predict", summary="Prever a intenção da mensagem", 
             description="""
Recebe a mensagem do cliente e devolve a **intenção** identificada.

**Autenticação:** não precisa de token.

**Como testar:** clique em **Try it out**, envie o JSON abaixo e clique em **Execute**.
```json
{"message": "Quero cancelar meu pedido"}
```

**Validação:**
- O campo `message` é obrigatório e deve ser texto
- Campos extras não são aceitos (ex.: `{"message": "oi", "admin": true}` → `422`)

> Por enquanto a intenção é fixa (`cancelamento`); o modelo de classificação ainda vai ser ligado nesta rota.

**Respostas:**
- `200`: `{"message": "...", "intent": "cancelamento"}`
- `422`: JSON inválido, campo faltando ou campo extra
""")
def predict(predictionRequest: PredictionRequest):  # Recebe a mensagem no formato do PredictionRequest
    predictionResponse = PredictionResponse(
        message=predictionRequest.message,  # Devolve a mesma mensagem recebida
        intent='cancelamento'  # Intenção fixa por enquanto, sem modelo de verdade
    )

    # Retorna a resposta com a mensagem e a intenção
    return predictionResponse


# -----------------------------------------------------------------------------------------------------
# ROTA - Valida a mensagem (válida se tiver mais de 5 caracteres)
@router.post("/valid",  summary="Validar a mensagem (mais de 5 caracteres)", 
             description="""
Verifica se a mensagem é **válida** para análise: precisa ter **mais de 5 caracteres**.

**Autenticação:** não precisa de token.

**Como testar:** clique em **Try it out**, envie o JSON e clique em **Execute**.
```json
{"message": "Onde está meu pedido?"}
```

**Respostas:**
- `200`: `{"message": "...", "valid": "Válido"}` ou `{"message": "...", "valid": "Inválido"}`
- `422`: JSON inválido, campo faltando ou campo extra
""")
def valid(predictionRequest: PredictionRequest):  # Recebe a mensagem no formato do PredictionRequest
    predictionResponse = PredictionValid(
        message=predictionRequest.message,  # Devolve a mesma mensagem recebida
        valid='Válido' if len(predictionRequest.message) > 5 else "Inválido"
    )

    # Retorna a resposta com a mensagem e o resultado da validação
    return predictionResponse


# ----------------------------------------------------------------------------------------------------
# ROTA - Lista todas as previsões (só para o admin)
@router.get("/predicitons", summary="Listar todas as previsões (só admin)", 
            description="""
Lista **todas as previsões** salvas no banco, de todos os usuários.

**Autenticação:** precisa de token.

**Regra de acesso:** só o **admin** (id `1`) pode usar esta rota.
Para os outros usuários a API responde `404`, sem revelar que a rota existe.

**Como testar:**
1. Faça login no **Authorize** com `admin` / `admin`
2. Clique em **Try it out** e em **Execute**

**Respostas:**
- `200`: lista de previsões
- `401`: sem token, token inválido ou expirado
- `404`: usuário não é admin ou não há previsões
""")
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


# --------------------------------------------------------------------------------------------------
# ROTA - Lista todas as previsões com limite de 5 requisições por minuto
@router.get("/predicitons_limited", 
            summary="Listar todas as previsões com limite de 5 por minuto (só admin)", 
            description="""
Mesma função da rota de listar todas as previsões, mas com **limite de requisições** (rate limiting).

**Autenticação:** precisa de token. **Só o admin** (id `1`) pode usar.

**Limite:** **5 requisições por minuto** por IP. A 6ª requisição no mesmo minuto é bloqueada.

**Como testar:**
1. Faça login no **Authorize** com `admin` / `admin`
2. Clique em **Execute** 6 vezes seguidas: da 6ª em diante a resposta é `429`
3. Espere 1 minuto e a rota volta a responder

**Respostas:**
- `200`: lista de previsões
- `401`: sem token, token inválido ou expirado
- `404`: usuário não é admin ou não há previsões
- `429`: limite de 5 requisições por minuto excedido
""")
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
