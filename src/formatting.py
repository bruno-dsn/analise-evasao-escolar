import math


def percentual(valor: float) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "Sem dado"
    return f"{valor:.1f}%".replace(".", ",")


def pontos_percentuais(valor: float, com_sinal: bool = True) -> str:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "Sem comparação"
    formato = "+.1f" if com_sinal else ".1f"
    return f"{format(valor, formato).replace('.', ',')} p.p."

