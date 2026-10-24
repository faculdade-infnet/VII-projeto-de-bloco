from sqlmodel import SQLModel, Field

# Tabela "user" no banco, que guarda os usuários da API
class User(SQLModel, table=True):
    # PK, gerada automaticamente pelo banco
    id: int | None = Field(default=None, unique=True, primary_key=True)    
    username: str       # Nome de usuário usado no login    
    password: str       # Senha do usuário
