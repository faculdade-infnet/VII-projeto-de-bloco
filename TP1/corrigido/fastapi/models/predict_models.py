from pydantic import BaseModel


# Modelo de entrada da rota /predict
# Recebe o texto da mensagem/ticket enviado pelo cliente
class PredictRequest(BaseModel):
    text: str   # texto do ticket que será classificado


# Modelo de saída da rota /predict
class PredictResponse(BaseModel):
    intent: str   # intenção/categoria identificada no ticket