from pydantic import BaseModel


# Texto da mensagem/ticket enviado pelo cliente."
class PredictRequest(BaseModel):
    text: str


# Saída rota /predict_não implementeada ainda."
class PredictResponse(BaseModel):
    intent: str