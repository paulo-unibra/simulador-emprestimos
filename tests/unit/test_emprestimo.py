import pytest
from src.emprestimo import validar_emprestimo


def test_emprestimo_valido():
    assert validar_emprestimo(10000, 24, 30) == True


def test_valor_abaixo_do_limite():
    with pytest.raises(ValueError, match="Valor fora do limite permitido"):
        validar_emprestimo(499, 24, 30)


def test_prazo_invalido():
    with pytest.raises(ValueError, match="Prazo inválido"):
        validar_emprestimo(10000, 5, 30)


def test_menor_de_idade():
    with pytest.raises(ValueError, match="Cliente menor de idade"):
        validar_emprestimo(10000, 24, 17)


def test_idade_maxima():
    with pytest.raises(ValueError, match="Prazo ultrapassa idade máxima"):
        validar_emprestimo(10000, 60, 77)