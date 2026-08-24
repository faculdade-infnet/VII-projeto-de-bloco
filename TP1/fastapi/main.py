from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from routes import health, auth, predict

app = FastAPI(
    title="TP1 - Fast API Customer Support",
    description="Projeto de Bloco: Análise e Segurança de Agentes de IA"
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        return JSONResponse(
            status_code=401,
            content={"detail": "Usuário não autenticado."}
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predict.router)
