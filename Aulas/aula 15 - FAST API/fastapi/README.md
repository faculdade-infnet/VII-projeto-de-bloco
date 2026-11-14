# EXCUTAR APLICAÇÃO COMPLETO

```bash
# Criar o .venv com as dependências atualizadas
py -m venv .venv --upgrade-deps
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
uvicorn main:app --reload

# ou
fastapi dev main.py
```

## Rodar Testes Automatizados

```bash
# Dentro do ambinte virtual .venv
py -m pytest -v
```

## Rodar arquivo ipynb

```bash
# Dentro do ambiente virtual .venv
jupyter nbconvert --execute --inplace "EDA_Bitext_Sample_Customer_Service.ipynb"

# Dentro do ambiente virtual .venv de forma interativa(da pra visualizar as celulas que ja foram executados com o resultado parcial)
papermill "EDA_Bitext_Sample_Customer_Service.ipynb" "EDA_Bitext_Sample_Customer_Service.ipynb" --log-output

# Confirmar que excutou tudo sem erro
$LASTEXITCODE
```

## Pré-requisitos

- VS Code
- Python 3.10 ou superior
- pip
- **Só no Windows:** permitir execução de scripts no PowerShell (necessário só uma vez)

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Instruções de instalação

1. Clone o repositório:

```bash
git clone https://github.com/<usuario>/<nome-do-repositorio>.git
cd <nome-do-repositorio>
```

2. Abra o projeto e acesse a pasta da API:

```bash
cd .\fastapi
```

3. Crie e ative um ambiente virtual:
   - Verifique se está dentro da pasta "fastapi"

```bash
# Criar mabiente virtual
py -m venv .venv

# Ative o ambiente virtual
.venv\Scripts\Activate.ps1
```

4. Instale as dependências a partir do arquivo requirements.txt:

```bash
py -m pip install -r requirements.txt
```

5. Verifique se foi instalado corretamente (deve aparecer name, location e outras informações sobre o pacote)

```bash
py -m pip show fastapi
```

## Instruções de execução

1. Acesse a pasta da API e certifique-se de que o ambiente virtual está ativado (veja passo 3 da instalação, caso tenha aberto um novo terminal):

```bash
cd .\fastapi
```

2. Execute a aplicação:

```bash
uvicorn main:app --reload

# ou
fastapi dev main.py
```

3. A API estará disponível em:
   http://127.0.0.1:8000/docs

# Extras

1. Apagar tudo e recriar o ambiente virtual

   **Windows (PowerShell):**

```bash
deactivate
Remove-Item -Recurse -Force .venv
```

2. Criar requirements.txt

```bash
# Dentro do .venv
py -m pip freeze > requirements.txt
```

<details>
<summary>Acesar rotas protegidas</summary>
1. Conforme imagem abaixo, clique em Authorize e informe usuário (admin)  e senha (admin)

![Descrição](images/oAuth2.png)

2. Após estar autenticado voce poderá acessar a rota 'listar_produtos_limite_protegido'

Obs. na pratica é igual a outra rota, porém agora necessita de autenticaçã o para acesso

![Descrição](images/rota_protegida.png)

</details>
