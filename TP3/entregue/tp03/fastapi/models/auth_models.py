from pydantic import BaseModel


# Modelo de resposta da rota /auth/token
# Define o formato do token retornado depois do login
class Token(BaseModel):
    access_token: str   # token JWT gerado
    token_type: str     # tipo do token ("bearer")