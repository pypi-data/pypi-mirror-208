# nome_do_projeto/macronutrientes.py
OBJETIVOS = {
    1: "Ganho de Massa Muscular",
    2: "Perda de Gordura",
    3: "Manutenção do Peso"
}

def calcular_macronutrientes(peso, objetivo):
    if isinstance(objetivo, str):
        objetivo = {v: k for k, v in OBJETIVOS.items()}.get(objetivo)

    if objetivo not in OBJETIVOS:
        raise ValueError("Objetivo inválido")

    if objetivo == 1:
        carboidratos = 4 * peso
        proteinas = 2 * peso
        gorduras = 1 * peso
    elif objetivo == 2:
        carboidratos = 3 * peso
        proteinas = 4 * peso
        gorduras = 3 * peso
    else:  # objetivo == 3
        carboidratos = 4 * peso
        proteinas = 4 * peso
        gorduras = 2 * peso

    return {
        "Carboidratos": carboidratos,
        "Proteinas": proteinas,
        "Gorduras": gorduras
    }
