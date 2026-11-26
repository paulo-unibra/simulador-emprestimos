from decimal import Decimal


def calcular_parcela_price(valor: float, taxa: float, prazo: int) -> float:
    """Retorna a parcela fixa pela Tabela Price, arredondada a duas casas."""
    if valor <= 0 or taxa < 0 or prazo < 1:
        raise ValueError(
            "Valor deve ser positivo, taxa não negativa e prazo de pelo menos 1 mês"
        )

    if taxa == 0:
        return round(valor / prazo, 2)

    parcela = valor * taxa / (1 - (1 + taxa) ** (-prazo))
    return round(parcela, 2)


def calcular_custo_total(valor: float, parcela: float, prazo: int) -> dict:
    """Calcula o total pago, os juros e o custo percentual do empréstimo (RN08)."""
    if valor <= 0 or parcela <= 0 or prazo <= 0:
        raise ValueError("Valor, parcela e prazo devem ser maiores que zero")

    principal = Decimal(str(valor))
    total_pago = round(Decimal(str(parcela)) * Decimal(str(prazo)), 2)
    total_juros = max(Decimal("0"), round(total_pago - principal, 2))
    custo_percentual = round(total_juros / principal * 100, 2)

    return {
        "total_pago": float(total_pago),
        "total_juros": float(total_juros),
        "custo_percentual": float(custo_percentual),
    }
