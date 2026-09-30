from sqlmodel import create_engine, Session

# Endereço do banco de dados: usa SQLite e o arquivo database.db
DATABASE_URL = "sqlite:///database.db"

# Cria a conexão com o banco, que vai ser usada pelo resto da aplicação
engine = create_engine(DATABASE_URL)


# Função que abre uma sessão com o banco para ser usada nas rotas
def get_session():
    # Abre a sessão e fecha automaticamente quando terminar
    with Session(engine) as session:
        # Entrega a sessão para a rota que pediu
        yield session