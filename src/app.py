from threading import Lock

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, FiniteFloat, StrictInt

from src.custos import calcular_custo_total, calcular_parcela_price
from src.desconto import calcular_desconto, calcular_frete
from src.emprestimo import classificar_taxa, validar_emprestimo, validar_margem
from src.parcelamento import simular_parcelamento

app = FastAPI(title="BaseProject - Curso Testes e CI (UNIBRA)")

PEDIDOS_DB: list[dict] = []
simulacoes: list[dict] = []
_simulacoes_lock = Lock()


class PedidoInput(BaseModel):
    item: str
    valor: float
    distancia_km: float = 0.0


class ParcelaPriceInput(BaseModel):
    valor: FiniteFloat
    taxa: FiniteFloat
    prazo: int


class CustoTotalInput(BaseModel):
    valor: FiniteFloat
    parcela: FiniteFloat
    prazo: int


class ClassificarTaxaInput(BaseModel):
    score: StrictInt


class ValidarEmprestimoInput(BaseModel):
    valor: FiniteFloat
    prazo: StrictInt
    idade: StrictInt


class ValidarMargemInput(BaseModel):
    renda: FiniteFloat
    parcela: FiniteFloat


class ParcelamentoInput(BaseModel):
    valor: FiniteFloat
    parcelas: StrictInt


class SimulacaoInput(BaseModel):
    valor: FiniteFloat
    prazo: StrictInt
    idade: StrictInt
    renda: FiniteFloat
    score: StrictInt


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/emprestimos/parcela-price")
def consultar_parcela_price(dados: ParcelaPriceInput):
    try:
        parcela = calcular_parcela_price(dados.valor, dados.taxa, dados.prazo)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    return {"parcela": parcela}


@app.post("/emprestimos/custo-total")
def consultar_custo_total(dados: CustoTotalInput):
    try:
        return calcular_custo_total(dados.valor, dados.parcela, dados.prazo)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.post("/emprestimos/classificar-taxa")
def consultar_taxa(dados: ClassificarTaxaInput):
    try:
        return {"taxa": classificar_taxa(dados.score)}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.post("/emprestimos/validar")
def consultar_validade_emprestimo(dados: ValidarEmprestimoInput):
    try:
        return {"valido": validar_emprestimo(dados.valor, dados.prazo, dados.idade)}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.post("/emprestimos/validar-margem")
def consultar_margem(dados: ValidarMargemInput):
    try:
        return {"valido": validar_margem(dados.renda, dados.parcela)}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.post("/parcelamentos")
def consultar_parcelamento(dados: ParcelamentoInput):
    try:
        return simular_parcelamento(dados.valor, dados.parcelas)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err


@app.post("/simulacoes", status_code=201)
def criar_simulacao(dados: SimulacaoInput):
    try:
        validar_emprestimo(dados.valor, dados.prazo, dados.idade)
        taxa = classificar_taxa(dados.score)
        parcela = calcular_parcela_price(dados.valor, taxa, dados.prazo)
        validar_margem(dados.renda, parcela)
        custo = calcular_custo_total(dados.valor, parcela, dados.prazo)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    with _simulacoes_lock:
        nova_simulacao = {
            "id": len(simulacoes) + 1,
            "taxa": taxa,
            "parcela": parcela,
            "total_pago": custo["total_pago"],
            "juros": custo["total_juros"],
            "custo_percentual": custo["custo_percentual"],
        }
        simulacoes.append(nova_simulacao)
    return nova_simulacao


@app.get("/simulacoes")
def listar_simulacoes():
    with _simulacoes_lock:
        return simulacoes.copy()


@app.post("/pedidos", status_code=201)
def criar_pedido(pedido: PedidoInput):
    if not pedido.item.strip():
        raise HTTPException(status_code=400, detail="Nome do item é obrigatório")

    try:
        total_com_desconto = calcular_desconto(pedido.valor)
        frete = calcular_frete(total_com_desconto, pedido.distancia_km)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    novo_pedido = {
        "id": len(PEDIDOS_DB) + 1,
        "item": pedido.item.strip(),
        "valor_original": round(pedido.valor, 2),
        "total_com_desconto": total_com_desconto,
        "frete": frete,
        "total_final": round(total_com_desconto + frete, 2),
    }
    PEDIDOS_DB.append(novo_pedido)
    return novo_pedido


@app.get("/pedidos")
def listar_pedidos():
    return PEDIDOS_DB
