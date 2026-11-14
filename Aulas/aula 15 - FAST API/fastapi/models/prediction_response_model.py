from pydantic import BaseModel

# Modelo que define o formato da resposta que a API devolve
class PredictionResponse(BaseModel):    
    message: str    # Mensagem que foi analisada    
    intent: str     # Intenção identificada na mensagem
    probability: float = 0.0   # novo campo (com valor padrão pra não quebrar o /predict)

# Modelo da resposta da rota de validação da mensagem
class PredictionValid(BaseModel):
    message: str    # Mensagem que foi validada
    valid: str      # Resultado da validação ("Válido" ou "Inválido")