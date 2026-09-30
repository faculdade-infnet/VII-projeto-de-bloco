import os
import runpy
from fastapi import FastAPI
from sqlmodel import SQLModel

from database.connection import engine
from routes.auth_route import router as auth_router
from routes.prediction_route import router as prediction_router

# Se o arquivo do banco ainda não existe
if not os.path.exists("database.db"):  
    # Roda script, cria o banco
    runpy.run_path(os.path.join("database", "create_database.py"))  
    # Roda script, popula banco
    runpy.run_path(os.path.join("database", "populate_database.py"))


app = FastAPI()  # Cria a aplicação FastAPI
SQLModel.metadata.create_all(engine)  # Cria as tabelas no banco se ainda não existirem


app.include_router(auth_router)        # Add rotas de autenticação
app.include_router(prediction_router)  # Add rotas de previsão