from sqlmodel import SQLModel, Field

# Tabela "prediction" no banco, que guarda as previsões feitas
class Prediction(SQLModel, table=True):
    # Chave primária, gerada automaticamente pelo banco
    id: int | None = Field(default=None, primary_key=True)    
    text: str       # Texto que foi enviado para análise    
    intent: str     # Intenção identificada para o texto
    owner_id: int = Field(foreign_key="user.id")    # FK liga a previsão ao ID usuário