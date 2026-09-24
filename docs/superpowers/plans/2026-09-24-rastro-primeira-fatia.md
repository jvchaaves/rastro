# Rastro CGU First Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. For this project, execution is inline under a manual Plan–Apply–Unify cycle.

**Goal:** Import CGU emendas from the official ZIP for amendment year 2025 into a consistent local snapshot and expose one amendment by code through an HTTP API with provenance.

**Architecture:** A CSV parser translates one official row into a typed amendment record with currency stored in cents. An SQLite importer writes a new batch in one transaction and switches the active batch only after validation. A FastAPI endpoint reads only the active batch. The ZIP is supplied by path at runtime and is never committed.

**Tech Stack:** Python 3.12+, FastAPI 0.135.1, SQLite from the Python standard library, pytest 9.0.2, HTTPX 0.28.1, Uvicorn 0.42.0. This stack is provisional until the student's domain is confirmed in the FI-01.

**Spec:** `FI-01.md`, especially sections 4, 7, 8, 9 and 11; `.paul/PROJECT.md`; `docs/research/fontes-2026-09-24.md`.

## Global Constraints

- Scope this plan to official CGU `EmendasParlamentares.csv` rows whose 12-digit code starts with `2025`.
- Treat `Sem informação` and malformed codes as skipped, not as a shared amendment identifier; count them.
- Never display a partially imported batch. A failed import preserves the previous active batch.
- Reimporting an identical ZIP must not create duplicate rows.
- Store monetary amounts as integer cents and source URL, ZIP SHA-256 and import time with each published batch.
- The first slice does not process favored persons, Siga Brasil, dashboard, subscriptions, alerts or claims about final use of funds.
- Keep the downloaded CGU ZIP out of Git; use synthetic tests with no personal identifiers.

## File Structure

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Runtime and development dependencies, package metadata |
| `.gitignore` | Ignore virtual environments, databases, caches and downloaded ZIPs |
| `src/rastro/cgu.py` | Parse official CGU CSV values and 2025 rows from ZIP |
| `src/rastro/store.py` | Initialize SQLite, import a ZIP atomically and read an active amendment |
| `src/rastro/api.py` | Define the public HTTP contract |
| `src/rastro/__main__.py` | Command-line import entry point |
| `tests/conftest.py` | Build a synthetic official-shaped ZIP fixture |
| `tests/test_cgu.py` | Validate normalization and invalid-code handling |
| `tests/test_store.py` | Verify idempotence and active batch safety |
| `tests/test_api.py` | Verify 200, 404, 503 and provenance fields |

---

### Task 1: Parse a 2025 CGU ZIP

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `src/rastro/__init__.py`, `src/rastro/cgu.py`
- Test: `tests/conftest.py`, `tests/test_cgu.py`

**Interfaces:**
- Produces: `Emenda` dataclass with `codigo`, `ano`, `tipo`, `autor`, `uf_aplicacao`, `funcao`, `empenhado_centavos`, `liquidado_centavos`, `pago_centavos`.
- Produces: `parse_brl_amount(value: str) -> int` and `iter_emendas_2025(zip_path: Path) -> Iterator[Emenda]`.
- Raises: `ValueError` for malformed money or a missing required CSV column; skips rows whose amendment code is not 12 digits or does not begin with `2025`.

- [ ] **Step 1: Add package metadata and a synthetic ZIP fixture.** `pyproject.toml` uses setuptools `src` discovery, requires Python 3.12+, and declares `fastapi==0.135.1`, `uvicorn==0.42.0` and dev dependencies `pytest==9.0.2`, `httpx==0.28.1`. `.gitignore` includes `.venv/`, `__pycache__/`, `.pytest_cache/`, `*.sqlite`, `*.zip`, `work/` and `data/`. The fixture creates `EmendasParlamentares.csv` in a ZIP with Latin-1, `;` and the headers below; it includes a 2025 row, `Sem informação` and a 2024 row.

```python
HEADERS = ["Código da Emenda", "Ano da Emenda", "Tipo de Emenda", "Nome do Autor da Emenda", "UF", "Nome Função", "Valor Empenhado", "Valor Liquidado", "Valor Pago"]
VALID = ["202500010001", "2025", "Individual", "Autora Exemplo", "CE", "Saúde", "15880000,00", "15721200,00", "15721200,00"]
```

- [ ] **Step 2: Write failing parser tests.** Use the fixture to assert the valid row is the only result and malformed money raises `ValueError`.

```python
def test_parse_brl_amount():
    assert parse_brl_amount("15880000,00") == 1_588_000_000

def test_iter_emendas_filters_invalid_and_other_year(cgu_zip):
    rows = list(iter_emendas_2025(cgu_zip))
    assert [row.codigo for row in rows] == ["202500010001"]
    assert rows[0].pago_centavos == 1_572_120_000
```

- [ ] **Step 3: Run `.venv/bin/python -m pytest tests/test_cgu.py -q` after creating `.venv` and installing `.[dev]`.** Expected result: tests fail because the parser functions do not exist.
- [ ] **Step 4: Implement the parser.** The core amount conversion is exact; `iter_emendas_2025` uses `zipfile.ZipFile.open`, `io.TextIOWrapper(encoding="latin-1", newline="")` and `csv.DictReader(delimiter=";")`, validates the required header set, and yields one `Emenda` per valid 2025 row.

```python
def parse_brl_amount(value: str) -> int:
    normalized = value.strip().replace(".", "").replace(",", ".")
    amount = Decimal(normalized)
    cents = amount * 100
    if not cents.is_finite() or cents != cents.to_integral_value():
        raise ValueError(f"Valor monetário inválido: {value!r}")
    return int(cents)
```

- [ ] **Step 5: Run `.venv/bin/python -m pytest tests/test_cgu.py -q`.** Expected result: all Task 1 tests pass.
- [ ] **Step 6: Commit.** `git add pyproject.toml .gitignore src/rastro tests/conftest.py tests/test_cgu.py` then `git commit -m 'Parseia emendas de 2025 do pacote da CGU'`.

### Task 2: Publish an SQLite batch atomically

**Files:**
- Create: `src/rastro/store.py`, `src/rastro/__main__.py`
- Test: `tests/test_store.py`

**Interfaces:**
- Consumes: `iter_emendas_2025(zip_path: Path) -> Iterator[Emenda]` from Task 1.
- Produces: `import_zip(db_path: Path, zip_path: Path) -> ImportResult`, where `ImportResult` records the ZIP hash, number imported, whether the batch was reused, and import time.
- Produces: `get_active_emenda(db_path: Path, codigo: str) -> tuple[Emenda, BatchInfo] | None` and `has_active_batch(db_path: Path) -> bool`.
- SQLite schema: `batches(sha256 PRIMARY KEY, source_url, imported_at, accepted_rows)`, `emendas(batch_sha256, codigo, ano, tipo, autor, uf_aplicacao, funcao, empenhado_centavos, liquidado_centavos, pago_centavos, PRIMARY KEY(batch_sha256,codigo))`, `state(key PRIMARY KEY, value)`.

- [ ] **Step 1: Write failing storage tests.** Import the synthetic ZIP twice and assert one batch, one active amendment and `reused=True` on the second call. Start from a valid active batch, attempt a second ZIP whose 2025 row has malformed money, and assert the original remains active. A ZIP with two different 2025 rows sharing a code must fail rather than sum or silently overwrite them.

```python
first = import_zip(db_path, cgu_zip)
second = import_zip(db_path, cgu_zip)
assert first.sha256 == second.sha256
assert second.reused is True
assert get_active_emenda(db_path, "202500010001")[0].codigo == "202500010001"
```

- [ ] **Step 2: Run `.venv/bin/python -m pytest tests/test_store.py -q`.** Expected result: tests fail because storage interfaces do not exist.
- [ ] **Step 3: Implement schema and import.** Stream SHA-256 calculation; open a connection with `PRAGMA journal_mode=WAL`; create schema; execute `BEGIN IMMEDIATE`; insert all selected rows under the new batch hash; reject zero selected rows and duplicate 2025 codes; add batch metadata; update `state('active_batch')`; commit. Roll back on any error. For an existing hash, return its batch without inserting rows; keep or select that complete batch as active in one transaction.

```sql
CREATE TABLE IF NOT EXISTS batches (
  sha256 TEXT PRIMARY KEY,
  source_url TEXT NOT NULL,
  imported_at TEXT NOT NULL,
  accepted_rows INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS emendas (
  batch_sha256 TEXT NOT NULL REFERENCES batches(sha256),
  codigo TEXT NOT NULL,
  ano INTEGER NOT NULL,
  tipo TEXT NOT NULL,
  autor TEXT NOT NULL,
  uf_aplicacao TEXT NOT NULL,
  funcao TEXT NOT NULL,
  empenhado_centavos INTEGER NOT NULL,
  liquidado_centavos INTEGER NOT NULL,
  pago_centavos INTEGER NOT NULL,
  PRIMARY KEY (batch_sha256, codigo)
);
CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
```

- [ ] **Step 4: Add `.venv/bin/python -m rastro import --db data/rastro.sqlite --zip work/EmendasParlamentares.zip`.** Print only hash, counts and import time; never print raw rows or personal identifiers.
- [ ] **Step 5: Run `.venv/bin/python -m pytest tests/test_store.py -q`.** Expected result: all Task 2 tests pass.
- [ ] **Step 6: Commit.** `git add src/rastro/store.py src/rastro/__main__.py tests/test_store.py` then `git commit -m 'Publica lotes da CGU de forma atômica'`.

### Task 3: Read one amendment through a documented API

**Files:**
- Create: `src/rastro/api.py`
- Test: `tests/test_api.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: `get_active_emenda()` and `has_active_batch()` from Task 2.
- Produces: `create_app(db_path: Path) -> FastAPI` with `GET /api/emendas/{codigo}`.
- Success response: `codigo`, `ano`, `tipo`, `autor`, `uf_aplicacao`, `funcao`, `valores_centavos` with `empenhado`, `liquidado`, `pago`, and `proveniencia` with `fonte`, `url`, `sha256_lote`, `importado_em`.
- Error responses: 503 when no batch is published; 404 for a code absent from the active batch; 422 for a path code that is not exactly 12 digits.

- [ ] **Step 1: Write failing API tests with FastAPI `TestClient`.** Assert the 200 response shape and cents for an imported synthetic row; assert 503 before import, 404 for another valid code and 422 for malformed code. Assert the response never contains raw CSV fields or identifiers of favored persons.

```python
client = TestClient(create_app(db_path))
response = client.get("/api/emendas/202500010001")
assert response.status_code == 200
assert response.json()["valores_centavos"]["pago"] == 1_572_120_000
assert response.json()["proveniencia"]["sha256_lote"]
```

- [ ] **Step 2: Run `.venv/bin/python -m pytest tests/test_api.py -q`.** Expected result: tests fail because `create_app` does not exist.
- [ ] **Step 3: Implement the response model and endpoint.** Use Pydantic response models for the documented fields, `HTTPException` for 404 and 503, and an exact `^[0-9]{12}$` validation constraint for the path parameter. Query only the active batch. Set `fonte` to `Portal da Transparência / CGU` and `url` to the official download page.

```python
from pydantic import BaseModel

class ValoresCentavos(BaseModel):
    empenhado: int
    liquidado: int
    pago: int

class Proveniencia(BaseModel):
    fonte: str
    url: str
    sha256_lote: str
    importado_em: str

class EmendaResponse(BaseModel):
    codigo: str
    ano: int
    tipo: str
    autor: str
    uf_aplicacao: str
    funcao: str
    valores_centavos: ValoresCentavos
    proveniencia: Proveniencia
```
- [ ] **Step 4: Document local commands in README.** Include environment setup, dependency install, the import command, starting `uvicorn rastro.api:app`, and a sample `curl` query. If using `create_app(db_path)`, expose `app = create_app(Path(os.environ.get("RASTRO_DB", "data/rastro.sqlite")))` for Uvicorn.
- [ ] **Step 5: Run `.venv/bin/python -m pytest -q` and request one imported code through a locally running API.** Expected result: tests pass; HTTP 200 includes the exact code and batch provenance.
- [ ] **Step 6: Commit.** `git add src/rastro/api.py tests/test_api.py README.md` then `git commit -m 'Expõe consulta de emenda com proveniência'`.

## Review and completion checks

- Check `git diff --check`, `.venv/bin/python -m pytest -q` and `git status --short --branch`.
- Run one real CGU import from an external ZIP path; record accepted and skipped counts without committing the ZIP or personal data.
- Compare the API response for one public emenda against the corresponding CSV row by code and monetary fields.
- Update `.paul/STATE.md` and create an execution summary in `.paul/` that compares planned and actual work as the manual UNIFY step.
