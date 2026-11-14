# EXCUTAR APLICAÇÃO COMPLETO

```bash
# Criar o .venv
py -m venv .venv

# Criar naversao 3.10 o .venv com as dependências atualizadas
py -3.10 -m venv .venv --upgrade-deps

# Criar o .venv com as dependências atualizadas
py -m venv .venv --upgrade-deps
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
fastapi dev main.py
```

# Criar requirements.txt

```bash
py -m pip freeze > requirements.txt
```

# Instalar pelo requirements.txt

```bash
py -m pip install -r requirements.txt
```

## Rodar arquivo

```bash
# Dentro do ambiente virtual .venv
jupyter nbconvert --execute --inplace "EDA_Bitext_Sample_Customer_Service.ipynb"

# Dentro do ambiente virtual .venv de forma interativa(da pra visualizar as celulas que ja foram executados com o resultado parcial)
papermill "EDA_Bitext_Sample_Customer_Service.ipynb" "EDA_Bitext_Sample_Customer_Service.ipynb" --log-output

# Confirmar que excutou tudo sem erro
$LASTEXITCODE
```

# Extras

1. Apagar tudo e recriar o ambiente virtual

   **Windows (PowerShell):**

```bash
deactivate
Remove-Item -Recurse -Force .venv
```
