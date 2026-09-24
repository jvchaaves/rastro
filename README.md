# Rastro

Para onde vão as emendas parlamentares.

O Rastro começa com uma consulta por código de emenda federal de 2025, usando o [pacote oficial da CGU](https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares). A resposta distingue valores empenhado, liquidado e pago e informa a origem e o hash do lote importado. O [FI-01](FI-01.md) e o [brief visual](docs/references/rastro-conceito.png) registram o escopo maior do projeto.

## Executar a primeira fatia

Requer Python 3.12 ou superior. Os comandos abaixo rodam na raiz do repositório.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
mkdir -p work
curl -L --fail --silent --show-error https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO -o work/EmendasParlamentares.zip
.venv/bin/python -m rastro import --db data/rastro.sqlite --zip work/EmendasParlamentares.zip
RASTRO_DB=data/rastro.sqlite .venv/bin/uvicorn rastro.api:app --host 127.0.0.1 --port 8000
```

Em outro terminal, consulte uma emenda existente no lote baixado:

```sh
curl http://127.0.0.1:8000/api/emendas/202538970001
```

O código acima foi encontrado no lote da CGU examinado em 24/09/2026; se o conjunto mudar, escolha um código de 2025 presente no ZIP atual. Os valores da API são inteiros em centavos. A documentação OpenAPI fica em `http://127.0.0.1:8000/docs`.

O importador ignora linhas sem código de emenda de 12 dígitos e linhas de outros anos, informando ambas as contagens. Uma falha de leitura ou validação não troca o lote ativo. Reimportar um ZIP já conhecido reutiliza seu registro sem substituir um lote mais recente que esteja ativo.

O ZIP, os bancos SQLite e os nomes de favorecidos do conjunto original não são versionados neste repositório. Pagamento registrado a um favorecido não comprova a aplicação final do recurso.

## Verificar

```sh
.venv/bin/python -m pytest -q
```

As fontes e os resultados da inspeção de 24/09/2026 estão em [pesquisa de dados](docs/research/fontes-2026-09-24.md). O projeto usa um [ciclo manual Plan–Apply–Unify](.paul/STATE.md); nenhum comando `/paul:*` é executado pelo Codex.
