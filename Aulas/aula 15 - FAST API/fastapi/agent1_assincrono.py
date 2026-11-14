# não trava, deixa outras coisas rodarem
import asyncio
from agents import Agent, Runner


# Monta o agente com a ferramenta e os parâmetros que forçam a resposta determinística
async def main(agent, prompt_user):
    result = await Runner.run(agent, prompt_user)   # await: espera sem travar o programa
    print(result.final_output)

agent = Agent(name="Atendente", instructions="Você é um atendente de suporte ao cliente.")
prompt_user = "Olá, gostaria de cancelar meu pedido."

asyncio.run(main(agent, prompt_user))   # precisa do asyncio.run pra rodar a função async