import os   # garante que tem este (usa os.environ)
import requests                                                # para chamar a rota /classify_padrao por HTTP
from openai import AsyncOpenAI
from agents import function_tool, Agent, Runner, ModelSettings, OpenAIChatCompletionsModel  # OpenAI Agents SDK (compatível com o Groq)

# System prompt: regras fixas de comportamento do agente
instructions = """
Você é um agente de atendimento ao cliente.

1. Sempre classifique a intenção do usuário utilizando a ferramenta disponível.
2. Utilize a classificação com a mensagem do usuário para retornar a intenção daquela mensagem.
3. Responda de maneira educada e objetiva.
4. Não invente informações.
"""

# FERRAMENTA (tool) do agente — o decorador transforma a função numa ferramenta
@function_tool
def classificar_intencao(texto: str) -> str:
    """Classifica a intenção de uma mensagem de atendimento ao cliente."""  # vira a descrição que o agente lê

    # chama a API (rota do regressor) passando a mensagem
    response = requests.post(
        "http://127.0.0.1:8000/classify_padrao",   # rota criada antes
        json={"message": texto},                   # corpo no formato que o PredictionRequest espera
        timeout=5                                  
    )

    response.raise_for_status()   # se a API responder erro (4xx/5xx), para aqui com erro
    dados = response.json()       # converte a resposta em dicionário {intent, probability}

    # devolve uma string com a intenção e a probabilidade
    return (f"Intenção: {dados['intent']}. \
        Probability: {dados['probability']}")


# Monta o agente com a ferramenta e os parâmetros que forçam a resposta determinística
def configurar_agent():
    # cria o cliente apontando pro Groq (chave + url base)
    client = AsyncOpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
    # cria o modelo do Groq
    model = OpenAIChatCompletionsModel(
        model="openai/gpt-oss-20b",
        openai_client=client
    )
    agent = Agent(
        name="Atendente",             # nome do agente
        model=model,                  # <- modelo do Groq
        instructions=instructions,    # o system prompt lá de cima
        tools=[classificar_intencao], # ferramentas que o agente pode usar
        # retorna o resultado da ferramenta direto, sem o LLM reescrever
        tool_use_behavior="stop_on_first_tool",
        # OBRIGA o agente a chamar essa ferramenta
        model_settings=ModelSettings(tool_choice="classificar_intencao")
    )
    return agent

# Função que a API vai chamar: recebe a mensagem, roda o agente e devolve a resposta
def classificar(prompt_user):
    agent = configurar_agent()                      # cria o agente
    resposta = Runner.run_sync(agent, prompt_user)  # roda de forma síncrona (espera a resposta)
    return resposta                                 # a resposta final fica em resposta.final_output