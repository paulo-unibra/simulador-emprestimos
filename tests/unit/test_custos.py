import pytest

from src.custos import calcular_custo_total, calcular_parcela_price


@pytest.mark.parametrize("taxa, prazo, parcela_esperada", [
    (0.02, 12, 94.56),
    (0, 3, 333.33),
    (0.02, 1, 10203.00),
])
def test_calcular_parcela_price(taxa, prazo, parcela_esperada):
    assert calcular_parcela_price(1000, taxa, prazo) == parcela_esperada


@pytest.mark.parametrize("valor, taxa, prazo", [
    (0, 0.02, 12),
    (-1, 0.02, 12),
    (1000, -0.02, 12),
    (1000, 0, 0),
])
def test_calcular_parcela_price_rejeita_entradas_invalidas(valor, taxa, prazo):
    with pytest.raises(ValueError):
        calcular_parcela_price(valor, taxa, prazo)


def test_calcular_custo_total_com_juros():
    assert calcular_custo_total(10000, 584.13, 24) == {
        "total_pago": 14019.12,
        "total_juros": 4019.12,
        "custo_percentual": 40.19,
    }


def test_calcular_custo_total_quando_arredondamento_deixa_total_abaixo_do_valor():
    assert calcular_custo_total(1000, 333.33, 3) == {
        "total_pago": 999.99,
        "total_juros": 0.0,
        "custo_percentual": 0.0,
    }


@pytest.mark.parametrize("valor, parcela, prazo", [
    (0, 100, 12),
    (-1, 100, 12),
    (1000, 0, 12),
    (1000, -1, 12),
    (1000, 100, 0),
    (1000, 100, -1),
])
def test_calcular_custo_total_rejeita_entradas_nao_positivas(valor, parcela, prazo):
    with pytest.raises(ValueError):
        calcular_custo_total(valor, parcela, prazo)
