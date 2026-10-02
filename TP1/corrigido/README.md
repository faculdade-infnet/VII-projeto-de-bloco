# TP1 - Análise e Segurança de Agentes de IA

**Projeto de Bloco | Instituto Infnet**

Sistema de atendimento ao cliente alimentado por inteligência artificial. Este primeiro TP estabelece a base do
projeto: define o domínio a partir da análise exploratória do dataset e entrega a estrutura da API com
autenticação funcional.

Grupo

- Alberto Frasson
- Johanna Liza
- Samuel Hermany
- Uendel Ives

---

## Objetivo do projeto

O bloco tem duas fases. Na primeira, constrói-se um sistema de atendimento ao cliente alimentado por IA; na
segunda, o sistema de um colega é atacado para identificar as falhas de segurança nele deixadas. Por isso a
segurança é tratada desde o primeiro commit, e não como camada adicionada ao final.

Este TP1 corresponde à competência integradora **"Definir o domínio do sistema com EDA exploratória e API
FastAPI autenticada como base"** e entrega:

1. **Documentação técnica do dataset** - fonte, características e justificativa da escolha.
2. **Análise exploratória (EDA)** - compreensão do problema, inspeção inicial, verificação de qualidade,
   limpeza e preparação, análise univariada e formulação de hipóteses sobre as intenções dos usuários.
3. **API FastAPI modular** com autenticação JWT via `OAuth2PasswordBearer`, expondo `GET /health`,
   `POST /auth/token` e `POST /predict` (rota protegida).
4. **DFD com trust boundaries** e aplicação da tríade CIA a cada componente.

O modelo de machine learning e o agente de IA **não** fazem parte deste TP. A rota `/predict` retorna, por
ora, uma intenção fixa que simula a saída do classificador a ser implementado nos TPs seguintes.

---

## Sobre o dataset

**Customer Support Ticket Dataset** - Kaggle, publicado por Suraj (`suraj520`), licença **CC0: Public
Domain**.
🔗 https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset

> A análise detalhada do dataset está no notebook **[eda/TP1_EDA.ipynb](eda/TP1_EDA.ipynb)** - significado
> das colunas, verificação da qualidade dos dados (valores ausentes, duplicatas, tipos), limpeza e
> preparação, análise univariada e hipóteses sobre as intenções dos usuários.

### Principais características

|                         |                                                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Dimensões**           | 8.469 registros × 17 atributos                                                                                               |
| **Composição**          | 2 variáveis quantitativas, 6 categóricas, 3 temporais, 5 textuais e 1 identificador                                          |
| **Variável de entrada** | `Ticket Description` - relato do cliente em texto livre                                                                      |
| **Variável-alvo**       | `Ticket Type` - 5 categorias praticamente balanceadas (razão de 1,07 entre a maior e a menor)                                |
| **Natureza**            | Dados **sintéticos** - 100% dos e-mails usam domínios reservados pela RFC 2606, decisão declarada pelo autor por privacidade |
| **Completude**          | 13 colunas 100% preenchidas; 4 colunas com ausência **estrutural** (só existem para chamados encerrados)                     |

O conjunto combina dados estruturados e textuais, permitindo investigar o perfil dos clientes, os tipos de
problema, os produtos, os canais de atendimento, as prioridades, os tempos de resposta e resolução e a
satisfação - inclusive cruzando essas dimensões.

### Motivo da escolha

- **Aderência direta ao objetivo.** O par `Ticket Description` → `Ticket Type` é exatamente o problema de
  classificação de intenção da rota `/predict`. Não há necessidade de rotular dados manualmente. Esse uso é
  **explicitamente previsto na documentação oficial**, que lista entre os casos de uso: _"NLP: the ticket
  descriptions can be used for training NLP models to automate ticket categorization"_.
- **Variável-alvo balanceada**, o que dispensa reamostragem e torna a acurácia uma métrica interpretável.
- **Riqueza para uma EDA completa**, com variáveis de todos os tipos em um único conjunto.
- **Licença CC0 e ausência de PII real**, permitindo versionar o CSV em repositório público e conduzir
  exercícios ofensivos sem risco jurídico - enquanto o dataset ainda _simula_ campos sensíveis, preservando
  o valor didático da modelagem de ameaças.
- **Campo de texto livre como superfície de ataque**, que é o vetor explorado em _prompt injection_ nos
  próximos blocos.
- **Escala adequada** (~3,8 MiB), versionável em Git e processável localmente.

---

## Instruções de instalação

### Pré-requisitos

- Python 3.10 ou superior
- `pip`
- **Somente no Windows:** liberar a execução de scripts na sessão atual do PowerShell (uma única vez)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Passo a passo

**1. Clone o repositório e acesse a pasta da API**

```bash
git clone https://github.com/infnet26-alberto-johanna-samuel-uendel/tp01.git
cd tp01/fastapi
```

**2. Crie e ative o ambiente virtual**

```bash
python -m venv .venv
```

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

**3. Instale as dependências**

```bash
python -m pip install -r requirements.txt

# Verificação: deve exibir name, version e location do pacote
python -m pip show fastapi
```

> As dependências do EDA (`pandas`, `matplotlib`, `seaborn`, `jupyter`) são instaladas à parte, conforme o
> ambiente usado para executar o notebook.

---

## Instruções de execução

### API

A partir da pasta `fastapi/`, com o ambiente virtual ativado:

```bash
uvicorn main:app --reload
```

A API sobe em **http://127.0.0.1:8000** e a documentação interativa (Swagger UI) fica em
**http://127.0.0.1:8000/docs**.

#### Endpoints

| Método | Rota          | Autenticação   | Descrição                                                           |
| ------ | ------------- | -------------- | ------------------------------------------------------------------- |
| `GET`  | `/health`     | Pública        | Verifica se a API está ativa. Retorna `{"status": "ok"}`            |
| `POST` | `/auth/token` | Pública        | Autentica o usuário e devolve um token JWT (validade de 30 minutos) |
| `POST` | `/predict`    | **Bearer JWT** | Recebe um texto e retorna uma intenção simulada                     |

#### Credenciais

O usuário administrador é definido _in-code_ em [fastapi/security/auth.py](fastapi/security/auth.py) e é o
único com acesso à API:

| Usuário | Senha   |
| ------- | ------- |
| `admin` | `admin` |

> ⚠️ Credenciais e `SECRET_KEY` estão fixas no código **por exigência do enunciado deste TP**. Não é prática
> aceitável fora deste contexto acadêmico - os riscos correspondentes estão registrados na análise do DFD.

#### Fluxo de uso

**1. Obter o token** (`/auth/token` recebe `application/x-www-form-urlencoded`, padrão do
`OAuth2PasswordBearer`):

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -d "username=admin&password=admin"
```

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

**2. Chamar a rota protegida** com o token no cabeçalho `Authorization`:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Meu produto chegou com defeito e quero devolver\"}"
```

Sem token válido, a rota responde **401**.

> Pelo Swagger UI, use o botão **Authorize** e informe `admin` / `admin` - o token passa a ser enviado
> automaticamente nas requisições a `/predict`.

### EDA

```bash
jupyter notebook eda/TP1_EDA.ipynb
```

O notebook lê o dataset a partir de `data/customer_support_tickets.csv`.

---

## Estrutura de pastas

```
TP1/
├── README.md                          # Este arquivo
│
├── data/
│   └── customer_support_tickets.csv   # Customer Support Ticket Dataset (8.469 × 17)
│
├── docs/
│   ├── fluxo_api_tp1.png              # Diagrama do fluxo da API
│   ├── dfd.drawio                     # Arquivo editável do DFD (draw.io)
│   └── endpoints.png                  # swagger com todos os endpoints
│
├── eda/
│   └── TP1_EDA.ipynb                  # Análise exploratória completa
│
├── fastapi/                           # Aplicação FastAPI
│   ├── main.py                        # Ponto de entrada; registra os routers
│   ├── requirements.txt               # Dependências da API
│   ├── README.md                      # Instruções específicas da API
│   │
│   │
│   ├── models/                        # Modelos Pydantic de entrada e saída
│   │   ├── auth_models.py             # Token
│   │   └── predict_models.py          # PredictRequest, PredictResponse
│   │
│   ├── routes/                        # Definição das rotas/endpoints
│   │   ├── health.py                  # GET  /health
│   │   ├── auth.py                    # POST /auth/token
│   │   └── predict.py                 # POST /predict (protegida)
│   │
│   └── security/                      # Segurança e autenticação
│       └── auth.py                    # JWT, OAuth2PasswordBearer, usuário in-code
│
└── others/
    └── dfd.png                        # DFD com entradas, saídas, trust boundaries e tríade CIA
```

---

## Responsabilidades e dependências

| Módulo      | Responsabilidade                                                                                | Depende de            |
| ----------- | ----------------------------------------------------------------------------------------------- | --------------------- |
| `main.py`   | Cria o app FastAPI, registra os routers e o tratamento de erro 401                              | `routes`              |
| `routes/`   | Define os endpoints. Não tem lógica de segurança, só chama as funções de `security`             | `models`, `security`  |
| `models/`   | Modelos Pydantic que validam a entrada e a saída (`Token`, `PredictRequest`, `PredictResponse`) | nenhum                |
| `security/` | Usuário admin in-code, geração e validação do JWT, `OAuth2PasswordBearer`                       | nenhum módulo interno |

Fluxo: `main.py` → `routes/*` → (`models/*` para validar dados) + (`security/auth.py` para autenticar).
`models` e `security` nunca importam `routes`, para evitar dependência circular.

O diagrama abaixo mostra o caminho de cada requisição pela API:

![Fluxo da API](docs/fluxo_api_tp1.png)

---

## Referências

- Dataset: https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset
- Documentação FastAPI: https://fastapi.tiangolo.com
- RFC 7519 - _JSON Web Token (JWT)_: https://www.rfc-editor.org/rfc/rfc7519
