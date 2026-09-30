import requests

url = "http://localhost:8000/docs"


# TEST - Origem NÃO liberada no CORS: o header deve vir vazio (None) e o navegador bloqueia
def test_cors_origem_nao_permitida():
    headers = {
        "Origin": "http://localhost:3001"
    }

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") is None


# TEST - Origem liberada no CORS: o header deve devolver a própria origem
def test_cors_origem_permitida():
    headers = {
        "Origin": "http://localhost:3000"
    }

    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"