# Simulador de Empréstimos e Parcelamentos

[![CI](https://github.com/paulo-unibra/simulador-emprestimos/actions/workflows/ci.yml/badge.svg)](https://github.com/paulo-unibra/simulador-emprestimos/actions/workflows/ci.yml)

Projeto final do curso de extensão **Testes e Qualidade de Software na Prática: Da Automação ao CI** (UNIBRA).

API REST em **Python + FastAPI** que simula empréstimos pessoais (Tabela Price) e parcelamentos no cartão. O cliente informa valor, prazo, idade, renda e score e recebe a taxa, a parcela, o total pago e os juros, ou o motivo da recusa. A aplicação é protegida por duas suítes de testes automatizados (unitários e de integração) executadas em uma pipeline de CI no GitHub Actions.

> Estrutura baseada no [BaseProject](https://github.com/lucasedson-ub/BaseProject) do professor.

## Equipe

| Integrante | Responsabilidade |
| --- | --- |
| _Nome P1_ | Funções 3 e 4 + rotas da API (`src/app.py`) |
| _Nome P2_ | Função 1 + testes de integração de `/simulacoes` |
| _Nome P3_ | Função 2 + repositório e pipeline de CI |
| _Nome P4_ | Função 5 + testes de integração de `/{id}`, `DELETE` e `/parcelamentos` |
| Carlos Antônio Bezerra | Função 6 + README, evidências e roteiro da apresentação |

Cada integrante implementou ao menos uma função de regra de negócio **e os seus testes unitários**.

## Tecnologias

- Python 3.12
- FastAPI (documentação interativa em `/docs`)
- pytest, pytest-cov e FastAPI TestClient
- GitHub Actions

## Estrutura do projeto

```text
simulador-emprestimos/
├── .github/workflows/ci.yml     # pipeline de CI (unit-tests -> integration-tests)
├── src/
│   ├── emprestimo.py            # as 6 funções de regras de negócio
│   └── app.py                   # API FastAPI
├── tests/
│   ├── unit/                    # testes unitários (30+)
│   └── integration/             # testes de API com TestClient (6+)
├── pytest.ini                   # pythonpath = .
├── requirements.txt
└── README.md
```

## Regras de negócio

| Regra | Valor |
| --- | --- |
| Valor do empréstimo | R$ 500,00 a R$ 50.000,00 |
| Prazo | 6 a 60 meses |
| Idade | mínimo 18 anos; idade ao fim do contrato até 80 anos |
| Score | 0 a 1000; abaixo de 300 o crédito é negado |
| Taxa mensal por score | 300–599: 4,5% · 600–799: 2,9% · 800–1000: 1,9% |
| Margem | parcela de até 30% da renda mensal |
| Parcelamento no cartão | 1x a 3x sem juros · 4x a 12x com 1,99% a.m. |

Entradas inválidas lançam `ValueError` nas funções e viram **HTTP 400** na API. ID inexistente retorna **HTTP 404**.

## As 6 funções (`src/emprestimo.py`)

| # | Função | O que faz |
| --- | --- | --- |
| 1 | `classificar_taxa(score)` | Define a taxa de juros mensal pela faixa de score; recusa score abaixo de 300 ou fora de 0–1000 |
| 2 | `validar_emprestimo(valor, prazo, idade)` | Confere limites de valor, prazo, maioridade e idade máxima ao fim do contrato |
| 3 | `calcular_parcela_price(valor, taxa, prazo)` | Calcula a parcela fixa pela Tabela Price: `PMT = V × i / (1 − (1 + i)^(−n))` |
| 4 | `calcular_custo_total(valor, parcela, prazo)` | Retorna total pago, total de juros e custo percentual |
| 5 | `validar_margem(renda, parcela)` | Garante que a parcela não passe de 30% da renda |
| 6 | `simular_parcelamento(valor, parcelas)` | Simula compra no cartão de 1x a 12x, com ou sem juros |

## Rotas da API (`src/app.py`)

| Método | Rota | Descrição | Respostas |
| --- | --- | --- | --- |
| GET | `/health` | Verifica se a API está no ar | 200 |
| POST | `/emprestimos/classificar-taxa` | Retorna a taxa mensal em decimal para o score | 200 · 400 · 422 |
| POST | `/emprestimos/validar` | Valida valor, prazo e idade do cliente | 200 · 400 · 422 |
| POST | `/emprestimos/parcela-price` | Calcula a parcela fixa pela Tabela Price | 200 · 400 · 422 |
| POST | `/emprestimos/custo-total` | Calcula total pago, juros e custo percentual | 200 · 400 · 422 |
| POST | `/emprestimos/validar-margem` | Verifica se a parcela cabe em 30% da renda | 200 · 400 · 422 |
| POST | `/parcelamentos` | Simula um parcelamento no cartão | 200 · 400 · 422 |

Rotas de simulação completa planejadas:

| Método | Rota | Descrição | Respostas |
| --- | --- | --- | --- |
| POST | `/simulacoes` | Cria uma simulação de empréstimo | 201 · 400 |
| GET | `/simulacoes` | Lista as simulações | 200 |
| GET | `/simulacoes/{id}` | Busca uma simulação pelo ID | 200 · 404 |
| DELETE | `/simulacoes/{id}` | Remove uma simulação | 204 · 404 |

Exemplo de requisição:

```http
POST /simulacoes
Content-Type: application/json

{"valor": 10000, "prazo": 24, "idade": 30, "renda": 4000, "score": 650}
```

Resposta (201):

```json
{"id": 1, "taxa": 0.029, "parcela": 584.13, "total_pago": 14019.12, "total_juros": 4019.12, "custo_percentual": 40.19}
```

## Como executar

```bash
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

### Consultar os cálculos com `curl`

Com a API rodando, execute em outro terminal. Informe a taxa mensal em decimal (`0.02` para 2% ao mês) e o prazo inteiro em meses.

```bash
curl -X POST http://127.0.0.1:8000/emprestimos/classificar-taxa \
  -H 'Content-Type: application/json' \
  -d '{"score":650}'

curl -X POST http://127.0.0.1:8000/emprestimos/validar \
  -H 'Content-Type: application/json' \
  -d '{"valor":10000,"prazo":24,"idade":30}'

curl -X POST http://127.0.0.1:8000/emprestimos/parcela-price \
  -H 'Content-Type: application/json' \
  -d '{"valor":1000,"taxa":0.02,"prazo":12}'

curl -X POST http://127.0.0.1:8000/emprestimos/custo-total \
  -H 'Content-Type: application/json' \
  -d '{"valor":10000,"parcela":584.13,"prazo":24}'

curl -X POST http://127.0.0.1:8000/emprestimos/validar-margem \
  -H 'Content-Type: application/json' \
  -d '{"renda":4000,"parcela":584.13}'

curl -X POST http://127.0.0.1:8000/parcelamentos \
  -H 'Content-Type: application/json' \
  -d '{"valor":900,"parcelas":3}'
```

## Como rodar os testes

```bash
# Testes unitários
pytest tests/unit -v

# Testes de integração / API
pytest tests/integration -v

# Tudo com cobertura (relatório HTML em htmlcov/index.html)
pytest --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80
```

Técnicas aplicadas nos testes unitários: padrão **AAA** (Arrange, Act, Assert), **classes de equivalência**, **análise de valor limite** com `@pytest.mark.parametrize` e validação de exceções com `pytest.raises`.

## Pipeline de CI

O workflow `.github/workflows/ci.yml` roda em todo `push` e `pull_request`, com estratégia **fail fast**:

1. **unit-tests**: instala as dependências e executa `pytest tests/unit -v`.
2. **integration-tests** (`needs: unit-tests`): só roda se os unitários passarem; executa os testes de API com cobertura mínima de 80%.
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
