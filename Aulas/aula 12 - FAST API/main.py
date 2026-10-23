import os
import runpy
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import SQLModel
from database.connection import engine
from routes.auth_route import router as auth_router
from routes.prediction_route import router as prediction_router
from routes.prediction_route import limiter as prediction_limiter

# Se o arquivo do banco ainda não existe
if not os.path.exists("database.db"):  
    # Roda script, cria o banco
    runpy.run_path(os.path.join("database", "create_database.py"))  
    # Roda script, popula banco
    runpy.run_path(os.path.join("database", "populate_database.py"))

# Cria a aplicação FastAPI
app = FastAPI(
    title="API de Predição de Intenção",   # nome que aparece no topo do /docs
    description="API para prever a intenção do cliente, com JWT, rate limiting e CORS.",
    version="1.0.0"                        # aparece ao lado do título (padrão: 0.1.0)
)
SQLModel.metadata.create_all(engine)  # Cria as tabelas no banco se ainda não existirem


# RATE LIMITING - Guarda o limitador no estado da aplicação
app.state.limiter = prediction_limiter
# Quando o limite estoura, devolve erro 429 (Too Many Requests) com mensagem para o usuário
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# CORS - Origens que podem acessar a API pelo navegador
origens_permitidas = [
    "http://localhost:3000",
    "http://localhost:8501"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origens_permitidas,  # Só essas origens são liberadas
    allow_credentials=True,            # Permite enviar credenciais (cookies, headers de autenticação)
    allow_methods=["*"],               # Libera todos os métodos HTTP
    allow_headers=["*"],               # Libera todos os headers enviados pelo frontend
)


# MIDDLEWARE - Tempo de processamento em todas as requisições
@app.middleware("http")
async def process_time(request: Request, call_next):
    start = time.time()  # Marca o início
    response = await call_next(request)  # Executa a rota e recebe a resposta
    final = time.time()  # Marca o fim
    response.headers["X-Process-Time"] = str(final - start)  # Tempo gasto no header da resposta
    return response


# MIDDLEWARE - Headers de segurança em todas as respostas
@app.middleware("http")
async def security_headers(request: Request, call_next):

    response = await call_next(request)  # Executa a rota e recebe a resposta

    # HSTS: obriga o navegador a usar HTTPS (1 ano, incluindo subdomínios)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Impede que a página seja colocada dentro de um iframe
    response.headers["X-Frame-Options"] = "DENY"
    # Evita MIME sniffing (navegador adivinhar o tipo do arquivo e tentar executar)
    response.headers["X-Content-Type-Options"] = "nosniff"
    # CSP: só carrega conteúdo do próprio domínio (comentado porque quebra o Swagger, usar só em produção)
    # response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response


# ROTA - raiz da API, usada para conferir se a aplicação está no ar
@app.get("/home", tags=["Status"], summary="Verificar se a API está no ar",
             description="""
Rota simples para conferir se a API está funcionando.

**Autenticação:** não precisa de token.

**Como testar:** clique em **Try it out** e depois em **Execute**.

**Respostas:**
- `200`: a API está no ar → `{"message": "ok"}`
"""                                              # ← texto completo (aparece ao abrir a rota)
)
@app.get("/", include_in_schema=False)   # "/" continua respondendo, mas não aparece no /docs
def home():
    return {"message": "ok"}


app.include_router(auth_router)        # Add rotas de autenticação
app.include_router(prediction_router)  # Add rotas de previsão
