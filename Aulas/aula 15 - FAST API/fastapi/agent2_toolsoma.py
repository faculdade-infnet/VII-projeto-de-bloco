from agents import function_tool, Agent, Runner

@function_tool
def somar(a: int, b: int) -> int:
    """Soma dois números."""
    soma = a + b
    print(f"Soma:{soma}")      # print só para ver se o LLM chamou a função
    return soma

agent = Agent(
    name="Atendente",
    instructions='''
    Você é um agente matemático.
    Utilize a função somar quando for necessário realizar uma soma.
    ''',
    tools=[somar]
)

prompt_user = "Olá, calcule 123456 + 654321"
resposta = Runner.run_sync(agent, prompt_user)
print(resposta.final_output)