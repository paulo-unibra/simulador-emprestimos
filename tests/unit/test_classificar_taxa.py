import pytest

from src.emprestimo import classificar_taxa


@pytest.mark.parametrize(
    ("score", "taxa_esperada"),
    [
        (300, 0.045),
        (599, 0.045),
        (600, 0.029),
        (799, 0.029),
        (800, 0.019),
        (1000, 0.019),
    ],
)
def test_classificar_taxa_faixas_e_limites(score, taxa_esperada):
    # Arrange & Act
    taxa = classificar_taxa(score)

    # Assert
    assert taxa == taxa_esperada


@pytest.mark.parametrize(
    ("score_invalido", "mensagem"),
    [
        (-1, "Score inválido"),
        (1001, "Score inválido"),
        (299, "Score insuficiente"),
    ],
)
def test_classificar_taxa_erros_e_limites_invalidos(score_invalido, mensagem):
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match=mensagem):
        classificar_taxa(score_invalido)