from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from routes import health, auth, predict

# Cria a aplicação FastAPI com título e descrição que aparecem na documentação (/docs)
app = FastAPI(
    title="TP1 - Fast API Customer Support",
    description="Projeto de Bloco: Análise e Segurança de Agentes de IA"
)

# Tratamento personalizado de erros HTTP
# Sempre que alguma rota lançar uma HTTPException, essa função é chamada
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    # Se o erro for 401 (não autenticado), retorna uma mensagem padrão em português
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"detail": "Usuário não autenticado."}
        )

    # Para os outros erros, mantém o código e a mensagem originais
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

# Registra as rotas na aplicação
app.include_router(health.router)   # rota para verificar se a API está funcionando
app.include_router(auth.router)     # rotas de autenticação (login e geração do token JWT)
app.include_router(predict.router)  # rota de predição (protegida por autenticação)
