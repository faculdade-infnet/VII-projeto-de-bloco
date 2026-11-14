# fica parado esperando a resposta
from agents import Agent, Runner


# Monta o agente com a ferramenta e os parâmetros que forçam a resposta determinística
def configurar_agent():
    agent = Agent(name="Atendente", instructions="Você é um atendente de suporte ao cliente.")
    prompt_user = "Olá, gostaria de cancelar meu pedido."

    resposta = Runner.run_sync(agent, prompt_user)   # chama direto e espera
    print(resposta.final_output)