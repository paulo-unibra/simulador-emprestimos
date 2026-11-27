import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

client = TestClient(app)

PAYLOAD_BASE = {
    "valor": 10000,
    "prazo": 24,
    "idade": 30,
    "renda": 4000,
    "score": 650,
}


@pytest.fixture(autouse=True)
def limpar_simulacoes_e_contador():
    # Arrange: limpa lista em memória e zera contador antes e depois de cada teste
    for nome_lista in ("simulacoes", "db_simulacoes", "historico_simulacoes"):
        if hasattr(app_module, nome_lista) and isinstance(getattr(app_module, nome_lista), list):
            getattr(app_module, nome_lista).clear()

    for nome_contador in ("contador_id", "proximo_id", "ultimo_id"):
        if hasattr(app_module, nome_contador):
            setattr(app_module, nome_contador, 0 if "contador" in nome_contador or "ultimo" in nome_contador else 1)

    yield

    for nome_lista in ("simulacoes", "db_simulacoes", "historico_simulacoes"):
        if hasattr(app_module, nome_lista) and isinstance(getattr(app_module, nome_lista), list):
            getattr(app_module, nome_lista).clear()


def test_get_simulacoes_lista_vazia():
    # Act
    resposta = client.get("/simulacoes")

    # Assert
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_post_simulacao_valida_e_get_com_um_item():
    # Arrange
    payload = PAYLOAD_BASE.copy()

    # Act
    post_resp = client.post("/simulacoes", json=payload)
    get_resp = client.get("/simulacoes")

    # Assert
    assert post_resp.status_code == 201
    dados_post = post_resp.json()
    assert dados_post["parcela"] == pytest.approx(584.13, abs=0.01)
    assert dados_post["taxa"] == pytest.approx(0.029, abs=0.0001)
    assert dados_post["total_pago"] == pytest.approx(14019.12, abs=0.01)
    assert dados_post["juros"] == pytest.approx(4019.12, abs=0.01)

    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 1


@pytest.mark.parametrize(
    "alteracoes",
    [
        {"score": 250},
        {"renda": 1000},
        {"valor": 499},
        {"prazo": 61},
        {"idade": 17},
        {"idade": 76, "prazo": 60},
        {"score": 1001},
    ],
)
def test_post_simulacao_recusas_e_limites_retornam_400(alteracoes):
    # Arrange
    payload = PAYLOAD_BASE.copy()
    payload.update(alteracoes)

    # Act
    resposta = client.post("/simulacoes", json=payload)

    # Assert
    assert resposta.status_code == 400


def test_post_simulacao_score_850_retorna_201():
    # Arrange
    payload = PAYLOAD_BASE.copy()
    payload["score"] = 850

    # Act
    resposta = client.post("/simulacoes", json=payload)

    # Assert
    assert resposta.status_code == 201
    assert resposta.json()["taxa"] == pytest.approx(0.019, abs=0.0001)