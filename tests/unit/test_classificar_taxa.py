import pytest
from src.emprestimo import classificar_taxa


@pytest.mark.parametrize("score, esperado", [
    (300, 0.045),
    (599, 0.045),
    (600, 0.029),
    (799, 0.029),
    (800, 0.019),
    (1000, 0.019),
])
def test_valores_limite(score, esperado):
   
    resultado = classificar_taxa(score)
    
    assert resultado == esperado


@pytest.mark.parametrize("score, esperado", [
    (450, 0.045), 
    (650, 0.029),  
    (900, 0.019),  
])
def test_classes_de_equivalencia(score, esperado):
    assert classificar_taxa(score) == esperado


def test_score_299_insuficiente():
    with pytest.raises(ValueError, match="Score insuficiente"):
        classificar_taxa(299)


def test_score_negativo_invalido():
    with pytest.raises(ValueError, match="Score inválido"):
        classificar_taxa(-1)


def test_score_1001_invalido():
    with pytest.raises(ValueError, match="Score inválido"):
        classificar_taxa(1001)