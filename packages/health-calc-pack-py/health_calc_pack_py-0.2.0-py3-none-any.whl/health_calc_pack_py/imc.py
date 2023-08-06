def calcular_imc(peso: float, altura: float) -> float:
    imc = peso / (altura ** 2)
    return round(imc, 2)
