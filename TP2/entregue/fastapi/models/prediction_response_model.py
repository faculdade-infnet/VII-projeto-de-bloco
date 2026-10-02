from pydantic import BaseModel

# Modelo que define o formato da resposta que a API devolve
class PredictionResponse(BaseModel):    
    message: str    # Mensagem que foi analisada    
    intent: str     # Intenção identificada na mensagem