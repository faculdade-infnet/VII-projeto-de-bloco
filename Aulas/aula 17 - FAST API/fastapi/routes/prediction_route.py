import joblib
from agent import classificar   # função que roda o agente (do agent.py na raiz)
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


# -------------------------------------------------------------------------------
# ROTA - Busca previsão pelo ID
# ---------------------------------------------------------------------------
@router.get("/predictions/{prediction_id}", 
            tags=["Previsões"],
            summary="Buscar uma previsão do usuário logado", 
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


# ------------------------------------------------------------------------------
# ROTA - Faz a previsão da intenção
# ---------------------------------------------------------------------------
@router.post("/predict", 
             tags=["Previsões"],
             summary="Prever a intenção da mensagem", 
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


# ------------------------------------------------------------------------------
# ROTA - Valida a mensagem (válida se tiver mais de 5 caracteres)
# ---------------------------------------------------------------------------
@router.post("/valid", 
             tags=["Previsões"],
             summary="Validar a mensagem (mais de 5 caracteres)", 
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


# -----------------------------------------------------------------------------
# ROTA - Lista todas as previsões (só para o admin)
# ---------------------------------------------------------------------------
@router.get("/predicitons", 
            tags=["Previsões"],
            summary="Listar todas as previsões (só admin)", 
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


# ---------------------------------------------------------------------------
# ROTA - Lista todas as previsões com limite de 5 requisições por minuto
# ---------------------------------------------------------------------------
@router.get("/predicitons_limited",
            tags=["Previsões"], 
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


# ---------------------------------------------------------------------------
# ROTA - Classifica a intenção do usuário pelo teste do EDA
# ---------------------------------------------------------------------------
@router.post("/classify_padrao",
            tags=["Classificações"],
            summary="(Sem LLM) Classificar a intenção da mensagem do usuário",
            description="""
Descobre qual é a **intenção** da mensagem usando o modelo que treinamos no notebook. Essa rota não usa IA (LLM).

**Autenticação:** não precisa de token.

**Como testar:**
1. Clique em **Try it out**
2. Mande uma mensagem, por exemplo: <br>
    - `{"message": "I want to cancel my order"}` ou
    - `{"message": "I need help"}`
3. Clique em **Execute**
4. Se mandar a mensagem vazia, dá erro `422`

**Respostas:**
- `200`: a intenção e a probabilidade
- `422`: mensagem vazia ou faltando
""")
def classify(request: PredictionRequest):
    # carrega o modelo e o vetorizador salvos no notebook
    modelo = joblib.load("melhor_classificador_intent.joblib")
    vectorizer = joblib.load("vectorizer.joblib")

    texto = request.message.strip()       # tira os espaços do começo e do fim
    if not texto:
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode estar vazia"
        )

    # matriz com 1 linha (a mensagem), como mesmas colunas de treino
    X = vectorizer.transform([texto])                 
    intent = modelo.predict(X)[0]                     # [0] = (intenção)a única previsão
    probability = modelo.predict_proba(X).max()       # probabilidade da classe prevista

    return {
        "intent": str(intent),
        "probability": float(probability)
    }


# ---------------------------------------------------------------------------
# ROTA - Protótipo: sempre devolve "cancelamento" (sem usar o LLM)
# ---------------------------------------------------------------------------
@router.post("/classify_semllm",
            tags=["Classificações"],
            summary="(Sem LLM) Protótipo que sempre responde 'cancelamento'",
            description="""
Essa rota é só um **teste**. Não usa o modelo nem a IA, então a resposta é **sempre igual**.

Ela devolve a mensagem enviada com a intenção `cancelamento` e a probabilidade `0.99`.

**Autenticação:** não precisa de token.

**Como testar:**
1. Clique em **Try it out**
2. Mande qualquer mensagem, por exemplo: `{"message": "qual o horário de atendimento?"}`
3. Clique em **Execute**: a resposta vai ser sempre `cancelamento`

**Respostas:**
- `200`: a mensagem, a intenção `cancelamento` e a probabilidade `0.99`
- `422`: mensagem faltando
""")
def classify_semllm(predictionRequest: PredictionRequest):
    predictionResponse = PredictionResponse(
        message=predictionRequest.message,   # devolve a mesma mensagem
        intent='cancelamento',               # intenção fixa (é um protótipo)
        probability=0.99                     # probabilidade fixa
    )
    return predictionResponse

# ---------------------------------------------------------------------------
# ROTA - Usa o agente de IA, que chama o classificador como ferramenta
# ---------------------------------------------------------------------------
@router.post("/classify_comllm",
            tags=["Classificações"],
            summary="(Com LLM) Classificar a intenção usando o agente de IA",
            description="""
Usa um **agente de IA** para descobrir a intenção. O agente usa o nosso modelo como ferramenta e depois escreve a resposta.

**Autenticação:** não precisa de token.

**Atenção:** precisa da **chave da API** no `.env`, e cada teste gasta tokens.

**Como testar:**
1. Clique em **Try it out**
2. Mande uma mensagem, por exemplo: `{"message": "meu pedido chegou quebrado, quero trocar"}`
3. Clique em **Execute** e veja a resposta do agente

**Respostas:**
- `200`: a resposta do agente
- `422`: mensagem faltando
- `500`: deu erro na IA (chave errada, acabaram os tokens ou o site está fora do ar)
""")
def classify_comllm(predictionRequest: PredictionRequest):
    resposta = classificar(predictionRequest.message)   # roda o agente com a mensagem

    # dados de consumo desta requisição
    uso = resposta.context_wrapper.usage
    print(
        f"[tokens] entrada={uso.input_tokens} "
        f"saída={uso.output_tokens} "
        f"total={uso.total_tokens} "
        f"chamadas={uso.requests}"
    )

    return {"response": resposta.final_output}          # a resposta final do agente