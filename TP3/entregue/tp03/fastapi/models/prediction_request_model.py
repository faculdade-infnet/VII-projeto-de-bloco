from pydantic import BaseModel, ConfigDict

# Modelo que define o formato dos dados que chegam na requisição de previsão
class PredictionRequest(BaseModel):
    # Não aceita campos extras além dos definidos aqui (se mandar outro campo, dá erro)
    model_config = ConfigDict(extra="forbid")
    
    message: str    # Texto da mensagem que vai ser analisada