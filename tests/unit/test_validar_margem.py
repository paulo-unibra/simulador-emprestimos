"""Testes unitários da Função 5 — validar_margem.

Técnicas: padrão AAA, classes de equivalência, análise de valor limite
(@pytest.mark.parametrize) e validação de exceções (pytest.raises).
"""

import pytest

from src.emprestimo import validar_margem


# Classe válida — parcela até 30% da renda. Limite: exatamente 30% (900 de 3000) é aceito.
@pytest.mark.parametrize(
    "renda, parcela",
    [
        (3000.00, 100.00),
        (3000.00, 899.99),
        (3000.00, 900.00),
        (101.00, 30.30),
    ],
)
def test_parcela_dentro_da_margem_retorna_true(renda, parcela):
    # Arrange: valores do parametrize

    # Act
    resultado = validar_margem(renda, parcela)

    # Assert
    assert resultado is True


# Classe inválida — parcela acima de 30% da renda. Limite: 1 centavo acima.
@pytest.mark.parametrize(
    "renda, parcela",
    [
        (3000.00, 900.01),
        (3000.00, 1500.00),
        (1000.00, 584.13),
    ],
)
def test_parcela_acima_da_margem_lanca_erro(renda, parcela):
    # Act / Assert
    with pytest.raises(ValueError, match="Parcela ultrapassa 30% da renda mensal"):
        validar_margem(renda, parcela)


# Classe inválida — renda ou parcela zero ou negativa.
@pytest.mark.parametrize(
    "renda, parcela",
    [
        (0, 100.00),
        (-3000.00, 100.00),
        (3000.00, 0),
        (3000.00, -100.00),
    ],
)
def test_renda_ou_parcela_nao_positiva_lanca_erro(renda, parcela):
    # Act / Assert
    with pytest.raises(ValueError, match="Renda e parcela devem ser maiores que zero"):
        validar_margem(renda, parcela)
