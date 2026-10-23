from fastapi.testclient import TestClient
from main import app

client = TestClient(app)  # Cliente de teste da aplicação FastAPI


# FUNCAO auxiliar - faz login e devolve o header Authorization pronto
def gerar_header(username, password):
    response = client.post("/token", data={"username": username, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------- AUTENTICAÇÃO ----------------

# TEST - login com usuário válido devolve o token
def test_login_valido():
    # Arrange
    dados = {"username": "admin", "password": "admin"}
    # Act
    response = client.post("/token", data=dados)
    # Assert
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# TEST - login com senha errada é rejeitado
def test_login_senha_errada():
    response = client.post("/token", data={"username": "admin", "password": "errada"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuário ou senha inválidos"}


# TEST - rota protegida sem token é bloqueada
def test_rota_protegida_sem_token():
    response = client.get("/predictions/1")
    assert response.status_code == 401


# TEST - token falso é rejeitado
def test_token_invalido():
    response = client.get("/predictions/1", headers={"Authorization": "Bearer token-falso"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Token inválido ou expirado"}


# TEST - rota protegida com token válido funciona
def test_rota_protegida_com_token():
    headers = gerar_header("admin", "admin")
    response = client.get("/predictions/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["owner_id"] == 1


# ---------------- AUTORIZAÇÃO ----------------

# TEST - usuário não vê a previsão de outro usuário
def test_usuario_nao_ve_previsao_de_outro():
    headers = gerar_header("jose", "1234")  # jose é o id 2; a previsão 1 é do admin
    response = client.get("/predictions/1", headers=headers)
    assert response.status_code == 404


# TEST - só o admin lista todas as previsões
def test_listar_previsoes_so_admin():
    resposta_jose = client.get("/predicitons", headers=gerar_header("jose", "1234"))
    resposta_admin = client.get("/predicitons", headers=gerar_header("admin", "admin"))
    assert resposta_jose.status_code == 404
    assert resposta_admin.status_code == 200
    assert len(resposta_admin.json()) == 3


# ---------------- VALIDAÇÃO ----------------

# TEST - /predict com entrada válida
def test_predict_valido():
    response = client.post("/predict", json={"message": "Quero cancelar meu pedido"})
    assert response.status_code == 200
    assert response.json() == {"message": "Quero cancelar meu pedido", "intent": "cancelamento"}


# TEST - /predict sem o campo message é rejeitado
def test_predict_sem_message():
    response = client.post("/predict", json={})
    assert response.status_code == 422


# TEST - /predict com campo extra é rejeitado (extra="forbid")
def test_predict_campo_extra():
    response = client.post("/predict", json={"message": "oi", "admin": True})
    assert response.status_code == 422


# ---------------- RATE LIMITING ----------------

# TEST - a 6ª requisição no mesmo minuto recebe 429
def test_rate_limit():
    headers = gerar_header("admin", "admin")
    status = [client.get("/predicitons_limited", headers=headers).status_code for _ in range(6)]
    assert status[:5] == [200, 200, 200, 200, 200]
    assert status[5] == 429


# ---------------- HEADERS DE SEGURANÇA ----------------

# TEST - middleware coloca os headers de segurança
def test_headers_seguranca():
    response = client.post("/predict", json={"message": "teste"})
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
