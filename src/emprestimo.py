def classificar_taxa(score: int) -> float:
    if isinstance(score, bool) or not isinstance(score, int):
        raise ValueError("Score inválido")

    if score < 0 or score > 1000:
        raise ValueError("Score inválido")

    if score < 300:
        raise ValueError("Score insuficiente")

    if score <= 599:
        return 0.045

    if score <= 799:
        return 0.029

    return 0.019