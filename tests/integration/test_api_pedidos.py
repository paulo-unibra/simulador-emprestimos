import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_health_check_retorna_200():
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.parametrize("rota, dados, status, esperado", [
    (
        "/emprestimos/parcela-price", {"valor": 1000, "taxa": 0.02, "prazo": 12},
        200, {"parcela": 94.56},
    ),
    (
        "/emprestimos/custo-total", {"valor": 10000, "parcela": 584.13, "prazo": 24},
        200, {"total_pago": 14019.12, "total_juros": 4019.12, "custo_percentual": 40.19},
    ),
    ("/emprestimos/parcela-price", {"valor": 1000, "taxa": -0.02, "prazo": 12}, 400, None),
    ("/emprestimos/custo-total", {"valor": 1000, "parcela": 0, "prazo": 3}, 400, None),
    ("/emprestimos/parcela-price", {"valor": 1000, "taxa": 0.02}, 422, None),
    ("/emprestimos/custo-total", {"valor": 1000, "parcela": 100, "prazo": 3.5}, 422, None),
    ("/emprestimos/classificar-taxa", {"score": 650}, 200, {"taxa": 0.029}),
    ("/emprestimos/classificar-taxa", {"score": 299}, 400, {"detail": "Score insuficiente"}),
    ("/emprestimos/validar", {"valor": 10000, "prazo": 24, "idade": 30}, 200, {"valido": True}),
    (
        "/emprestimos/validar", {"valor": 10000, "prazo": 24, "idade": 17},
        400, {"detail": "Cliente menor de idade"},
    ),
    ("/emprestimos/validar-margem", {"renda": 1000, "parcela": 300}, 200, {"valido": True}),
    (
        "/emprestimos/validar-margem", {"renda": 1000, "parcela": 300.01},
        400, {"detail": "Parcela ultrapassa 30% da renda mensal"},
    ),
    ("/emprestimos/validar-margem", {"renda": 0, "parcela": 300}, 400, None),
    (
        "/parcelamentos", {"valor": 900, "parcelas": 3},
        200, {"parcelas": 3, "valor_parcela": 300.0, "total": 900.0, "com_juros": False},
    ),
    ("/parcelamentos", {"valor": 900, "parcelas": 13}, 400, None),
    ("/parcelamentos", {"valor": 900, "parcelas": True}, 422, None),
])
def test_rotas_de_calculo_de_emprestimo(rota, dados, status, esperado):
    resp = client.post(rota, json=dados)

    assert resp.status_code == status
    if esperado is None:
        assert resp.json()["detail"]
    else:
        assert resp.json() == esperado


# TODO (Prática 2):
# 1. Testar POST /pedidos com valor >= 100 e distância > 0 (status 201 e total_final calculado)
# 2. Testar POST /pedidos com valor negativo (status 400 e mensagem de erro)
# 3. Testar POST /pedidos com item vazio (status 400)
# 4. Testar GET /pedidos verificando se o pedido criado aparece na lista
