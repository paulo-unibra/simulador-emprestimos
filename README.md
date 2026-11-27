# Simulador de Empréstimos e Parcelamentos

[![CI](https://github.com/paulo-unibra/simulador-emprestimos/actions/workflows/ci.yml/badge.svg)](https://github.com/paulo-unibra/simulador-emprestimos/actions/workflows/ci.yml)

Projeto final do curso de extensão **Testes e Qualidade de Software na Prática: Da Automação ao CI** (UNIBRA).

API REST em **Python + FastAPI** que simula empréstimos pessoais (Tabela Price) e parcelamentos no cartão. Cada regra de negócio tem uma rota própria: classificar a taxa pelo score, validar o pedido, calcular a parcela, conferir a margem da renda, calcular o custo total e simular o parcelamento. A aplicação é protegida por duas suítes de testes automatizados (unitários e de integração) executadas em uma pipeline de CI no GitHub Actions.

> Estrutura baseada no [BaseProject](https://github.com/lucasedson-ub/BaseProject) do professor.

## Equipe

| Integrante | Papel | Contribuição |
| --- | --- | --- |
| Paulo Ricardo | P1 | Funções 3 e 4 (`src/custos.py`) e rotas da API (`src/app.py`) |
| Alexandre | P2 | Testes de integração da API |
| José Carlos | P3 | Funções 2 e 5 (`validar_emprestimo`, `validar_margem`) e pipeline de CI |
| Vitor | P4 | Função 1 (`classificar_taxa`) |
| Carlos Antônio Bezerra | P5 | Função 6 (`src/parcelamento.py`), README e evidências |

## Tecnologias

- Python 3.12
- FastAPI + Uvicorn (documentação interativa em `/docs`)
- pytest, pytest-cov e FastAPI TestClient
- GitHub Actions

## Estrutura do projeto

```text
simulador-emprestimos/
├── .github/workflows/ci.yml          # pipeline de CI (unit-tests -> integration-tests)
├── src/
│   ├── emprestimo.py                 # funções 1, 2 e 5 (taxa, validação, margem)
│   ├── custos.py                     # funções 3 e 4 (parcela Price, custo total)
│   ├── parcelamento.py               # função 6 (parcelamento no cartão)
│   ├── app.py                        # API FastAPI
│   └── desconto.py                   # exemplo original do BaseProject
├── tests/
│   ├── unit/                         # testes unitários
│   │   ├── test_classificar_taxa.py
│   │   ├── test_emprestimo.py
│   │   ├── test_custos.py
│   │   ├── test_parcelamento.py
│   │   └── test_desconto.py          # exemplo original do BaseProject
│   └── integration/
│       └── test_api_pedidos.py       # testes de API com TestClient
├── pytest.ini                        # pythonpath = .
├── requirements.txt
└── README.md
```

## Regras de negócio

| Regra | Valor |
| --- | --- |
| Valor do empréstimo | R$ 500,00 a R$ 50.000,00 |
| Prazo | 6 a 60 meses (número inteiro) |
| Idade | mínimo 18 anos; idade ao fim do contrato até 80 anos |
| Score | 0 a 1000; abaixo de 300 o crédito é negado |
| Taxa mensal por score | 300–599: 4,5% · 600–799: 2,9% · 800–1000: 1,9% |
| Margem | parcela de até 30% da renda mensal |
| Parcelamento no cartão | 1x a 3x sem juros · 4x a 12x com 1,99% a.m. |

Entradas que quebram uma regra lançam `ValueError` nas funções e viram **HTTP 400** na API. Campos com tipo errado (ex.: texto no lugar de número) retornam **HTTP 422**, validados pelo próprio FastAPI.

## As 6 funções

| # | Função | Arquivo | O que faz |
| --- | --- | --- | --- |
| 1 | `classificar_taxa(score)` | `src/emprestimo.py` | Define a taxa mensal pela faixa de score; recusa score abaixo de 300 ou fora de 0–1000 |
| 2 | `validar_emprestimo(valor, prazo, idade)` | `src/emprestimo.py` | Confere limites de valor, prazo, maioridade e idade máxima ao fim do contrato |
| 3 | `calcular_parcela_price(valor, taxa, prazo)` | `src/custos.py` | Calcula a parcela fixa pela Tabela Price: `PMT = V × i / (1 − (1 + i)^(−n))` |
| 4 | `calcular_custo_total(valor, parcela, prazo)` | `src/custos.py` | Retorna total pago, total de juros e custo percentual |
| 5 | `validar_margem(renda, parcela)` | `src/emprestimo.py` | Garante que a parcela não passe de 30% da renda |
| 6 | `simular_parcelamento(valor, parcelas)` | `src/parcelamento.py` | Simula compra no cartão de 1x a 12x, com ou sem juros |

## Rotas da API (`src/app.py`)

| Método | Rota | Função usada | Corpo da requisição | Respostas |
| --- | --- | --- | --- | --- |
| GET | `/health` | — | — | 200 |
| POST | `/emprestimos/classificar-taxa` | 1 | `{"score": 650}` | 200 · 400 · 422 |
| POST | `/emprestimos/validar` | 2 | `{"valor": 10000, "prazo": 24, "idade": 30}` | 200 · 400 · 422 |
| POST | `/emprestimos/parcela-price` | 3 | `{"valor": 10000, "taxa": 0.029, "prazo": 24}` | 200 · 400 · 422 |
| POST | `/emprestimos/custo-total` | 4 | `{"valor": 10000, "parcela": 584.13, "prazo": 24}` | 200 · 400 · 422 |
| POST | `/emprestimos/validar-margem` | 5 | `{"renda": 4000, "parcela": 584.13}` | 200 · 400 · 422 |
| POST | `/parcelamentos` | 6 | `{"valor": 1200, "parcelas": 4}` | 200 · 400 · 422 |

As rotas `POST /pedidos` e `GET /pedidos` são o exemplo original do BaseProject e foram mantidas como referência.

### Exemplo: simulando um empréstimo de R$ 10.000 em 24x com score 650

| Passo | Rota | Resposta |
| --- | --- | --- |
| 1. Taxa pelo score | `POST /emprestimos/classificar-taxa` | `{"taxa": 0.029}` |
| 2. Validar o pedido | `POST /emprestimos/validar` | `{"valido": true}` |
| 3. Calcular a parcela | `POST /emprestimos/parcela-price` | `{"parcela": 584.13}` |
| 4. Conferir a margem (renda R$ 4.000) | `POST /emprestimos/validar-margem` | `{"valido": true}` |
| 5. Custo total | `POST /emprestimos/custo-total` | `{"total_pago": 14019.12, "total_juros": 4019.12, "custo_percentual": 40.19}` |

Exemplos de erro:

```http
POST /emprestimos/classificar-taxa   {"score": 250}
-> 400 {"detail": "Score insuficiente"}

POST /emprestimos/validar-margem     {"renda": 1000, "parcela": 584.13}
-> 400 {"detail": "Parcela ultrapassa 30% da renda mensal"}
```

## Como executar

```powershell
# 1. Criar e ativar o ambiente virtual
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Subir a API (documentação em http://127.0.0.1:8000/docs)
uvicorn src.app:app --reload
```

## Como rodar os testes

```powershell
# Testes unitários
pytest tests/unit -v

# Testes de integração / API
pytest tests/integration -v

# Tudo com cobertura (relatório HTML em htmlcov/index.html)
pytest --cov=src --cov-report=html --cov-report=term-missing
```

Técnicas aplicadas nos testes unitários: padrão **AAA** (Arrange, Act, Assert), **classes de equivalência**, **análise de valor limite** com `@pytest.mark.parametrize` e validação de exceções com `pytest.raises`. Nos testes de integração, o `TestClient` do FastAPI valida os cenários de sucesso (200) e de erro (400 e 422) de cada rota.

## Pipeline de CI

O workflow `.github/workflows/ci.yml` roda em todo `push` e `pull_request`, com estratégia **fail fast**:

1. **unit-tests**: instala as dependências e executa `pytest tests/unit -v`.
2. **integration-tests** (`needs: unit-tests`): só roda se os unitários passarem; executa `pytest tests/integration -v --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80`.
3. O relatório `htmlcov/` é publicado como artefato **coverage-report** em toda execução (`if: always()`).

## Evidências

_Prints da aba Actions (pipeline verde com os dois jobs e o artefato coverage-report) serão adicionados aqui._

---

> **Conteúdo original do BaseProject (professor)** — mantido abaixo como referência.

# BaseProject — Testes e Qualidade de Software na Prática: Da Automação ao CI (UNIBRA)

Repositório base para as atividades práticas do curso de extensão de 40h.

## 1. Preparação do Ambiente (No seu computador)

```bash
# 1. Criar e ativar ambiente virtual
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt
```

## 2. Comandos Úteis

```bash
# Rodar apenas testes unitários
pytest tests/unit -v

# Rodar apenas testes de integração/API
pytest tests/integration -v

# Rodar tudo com relatório de cobertura
pytest --cov=src --cov-report=term-missing
```

## 3. Roteiro das Práticas em Sala

- **Prática 1 (Manhã):** Completar `tests/unit/test_desconto.py` aplicando padrão **AAA**, **Valor Limite** (`@pytest.mark.parametrize`) e **`pytest.raises`**.
- **Prática 2 (Tarde):** Completar `tests/integration/test_api_pedidos.py` testando os endpoints `POST /pedidos` e `GET /pedidos` com `TestClient` e verificando a cobertura com `pytest-cov`.
- **Prática 3 (Tarde):** Criar `.github/workflows/ci.yml` com dois jobs (`unit-tests` e `integration-tests` usando `needs: unit-tests`), fazer `git push` e acompanhar o pipeline no **GitHub Actions**.
