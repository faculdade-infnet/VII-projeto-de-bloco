from fastapi.testclient import TestClient
from main import app

client = TestClient(app)  # Cliente de teste: faz requisições direto na app, sem subir servidor


# TEST - a raiz da API responde
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "ok"
    }
