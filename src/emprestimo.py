
def classificar_taxa(score):
    if score < 0 or score > 1000:
        raise ValueError("Score inválido")

    if score < 300:
        raise ValueError("Score insuficiente")

    if score < 600:
        return 0.045

    if score < 800:
        return 0.029

    return 0.019


def validar_emprestimo(valor, prazo, idade):

    if valor < 500 or valor > 50000:
        raise ValueError("Valor fora do limite permitido")

    if not isinstance(prazo, int) or prazo < 6 or prazo > 60:
        raise ValueError("Prazo inválido")

    if idade < 18:
        raise ValueError("Cliente menor de idade")

    if idade + prazo / 12 > 80:
        raise ValueError("Prazo ultrapassa idade máxima")

    return True

