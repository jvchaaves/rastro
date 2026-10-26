"""Verifica a coerência da especificação e gera arquitetura/rastreabilidade.md.

Uso: python3 especificacoes/joao-vitor/verificar.py
Checa: campos obrigatórios das fichas, ids REQ citados, operationIds, campos Entidade.campo
(modelo de dados e schemas do OpenAPI), cobertura de requisitos e operações.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

BASE = Path(__file__).parent
TELAS = BASE / "telas"
ARQ = BASE / "arquitetura"

CAMPOS = ["Superfície · ator", "Objetivo", "Chega de / vai para", "Mostra", "Coleta",
          "Ações", "Estados", "Regras", "Requisitos · contrato", "Acessibilidade", "Anexo"]
ESTADOS = ["carregando", "vazio", "erro", "sucesso", "offline", "sem permissão"]

erros: list[str] = []

# --- requisitos
req_txt = (ARQ / "requisitos.md").read_text()
reqs = set(re.findall(r"^\| (REQ-\d{2}) \|", req_txt, re.M))

# --- openapi
api = yaml.safe_load((ARQ / "contratos/openapi.yaml").read_text())
ops = {}
for caminho, item in api["paths"].items():
    for metodo, op in item.items():
        if isinstance(op, dict) and "operationId" in op:
            ops[op["operationId"]] = f"{metodo.upper()} {caminho}"
schemas = api["components"]["schemas"]


def props(nome, vistos=None):
    vistos = vistos or set()
    if nome in vistos:
        return set()
    vistos.add(nome)
    s = schemas[nome]
    out = set(s.get("properties", {}))
    for parte in s.get("allOf", []):
        if "$ref" in parte:
            out |= props(parte["$ref"].split("/")[-1], vistos)
        out |= set(parte.get("properties", {}))
    return out


schema_props = {n: props(n) for n in schemas}
cli_ops = {"cli:importar", "cli:publicar", "cli:sincronizar", "cli:lotes"}

# --- modelo de dados
modelo = (ARQ / "contratos/modelo-de-dados.md").read_text()
entidades = defaultdict(set)
atual = None
for linha in modelo.splitlines():
    m = re.match(r"^### (\w+)", linha)
    if m:
        atual = m.group(1)
        continue
    m = re.match(r"^\| `([\w`/ ]+)` \|", linha)
    if atual and m:
        for campo in re.findall(r"\w+", m.group(1)):
            entidades[atual].add(campo)
entidades["Emenda"].add("estado_execucao")  # derivado (v_emenda_estado)

# --- fichas
inventario = (TELAS / "inventario.md").read_text()
ids_inv = re.findall(r"^\| ([PDSO]\d{2}) \|", inventario, re.M)
fichas = sorted(p for p in TELAS.glob("[PDSO][0-9][0-9]-*.md"))
ids_fichas = [p.name[:3] for p in fichas]
if sorted(ids_inv) != sorted(ids_fichas):
    erros.append(f"inventário {sorted(ids_inv)} ≠ fichas {sorted(ids_fichas)}")
if len(fichas) < 10:
    erros.append("menos de 10 telas")

tela_reqs, tela_ops, req_telas, op_telas = {}, {}, defaultdict(set), defaultdict(set)
for p in fichas:
    tid = p.name[:3]
    txt = p.read_text()
    if not txt.startswith(f"## {tid} · "):
        erros.append(f"{p.name}: título fora do template")
    for campo in CAMPOS:
        if not re.search(rf"^- \*\*{re.escape(campo)}( \(saída\)| \(argumentos\))?:\*\*", txt, re.M):
            erros.append(f"{p.name}: campo ausente '{campo}'")
    bloco_estados = txt.split("**Estados:**")[1].split("- **Regras:**")[0]
    for e in ESTADOS:
        if f"**{e}" not in bloco_estados:
            erros.append(f"{p.name}: estado '{e}' não especificado")
    for estado in re.split(r"\n(?=  - \*\*)", bloco_estados.strip()):
        if estado.lstrip().startswith("- **") and not re.search(r"REQ-\d{2}|ADR-\d{4}", estado):
            erros.append(f"{p.name}: estado sem requisito → {estado.strip()[:60]}")
    citados = set(re.findall(r"REQ-\d{2}", txt))
    for r in citados - reqs:
        erros.append(f"{p.name}: {r} não existe em requisitos.md")
    bloco_contrato = txt.split("**Requisitos · contrato:**")[1].split("- **Acessibilidade:**")[0]
    usados = set(re.findall(r"\(`([a-z_]+)`", bloco_contrato)) | set(re.findall(r"`(cli:[a-z]+)`", bloco_contrato))
    for o in usados:
        if o not in ops and o not in cli_ops:
            erros.append(f"{p.name}: operação {o} não existe no contrato")
    for o in set(re.findall(r"`([a-z]+_[a-z_]+)`", txt)) & set(ops):
        usados.add(o)
    tela_reqs[tid], tela_ops[tid] = citados, usados
    for r in citados:
        req_telas[r].add(tid)
    for o in usados:
        op_telas[o].add(tid)
    for ent, campo in re.findall(r"`([A-Z]\w+)\.(\w+)", txt):
        if ent in entidades:
            if campo not in entidades[ent]:
                erros.append(f"{p.name}: {ent}.{campo} não existe no modelo de dados")
        elif ent in schema_props:
            if campo not in schema_props[ent]:
                erros.append(f"{p.name}: {ent}.{campo} não existe no schema do OpenAPI")
        else:
            erros.append(f"{p.name}: entidade/schema desconhecido {ent}")

# --- cobertura
outros = "".join(f.read_text() for f in [*(ARQ / "adr").glob("*.md"), ARQ / "qualidade.md"])
for r in sorted(reqs):
    if r not in req_telas and r not in outros:
        erros.append(f"{r} não é citado por nenhuma tela, ADR ou cenário")
for o in ops:
    if o not in op_telas:
        erros.append(f"operação {o} não é usada por nenhuma tela")

# --- matriz
linhas = ["# Matriz de rastreabilidade", "",
          "Gerada por `verificar.py` a partir das fichas em `../telas/`, de `requisitos.md` e de "
          "`contratos/openapi.yaml`. Não editar à mão.", "",
          "## Tela → requisitos → contratos", "",
          "| Tela | Requisitos | Operações (contrato) |", "| :-- | :-- | :-- |"]
for tid in ids_fichas:
    o = ", ".join(f"`{x}`" for x in sorted(tela_ops[tid]))
    linhas.append(f"| {tid} | {', '.join(sorted(tela_reqs[tid]))} | {o} |")
linhas += ["", "## Requisito → telas", "", "| Requisito | Telas | Também em |", "| :-- | :-- | :-- |"]
for r in sorted(reqs):
    tambem = sorted({f"ADR-{f.stem[:4]}" for f in (ARQ / "adr").glob("*.md") if r in f.read_text()}
                    | ({"qualidade"} if r in (ARQ / "qualidade.md").read_text() else set()))
    linhas.append(f"| {r} | {', '.join(sorted(req_telas.get(r, []))) or '—'} | {', '.join(tambem) or '—'} |")
linhas += ["", "## Operação → telas", "", "| Operação | Método e caminho | Telas |", "| :-- | :-- | :-- |"]
for o, mc in ops.items():
    linhas.append(f"| `{o}` | `{mc}` | {', '.join(sorted(op_telas[o]))} |")
for o in sorted(cli_ops):
    linhas.append(f"| `{o}` | CLI (`contratos/cli.md`) | {', '.join(sorted(op_telas.get(o, []))) or '— (agendador)'} |")
(ARQ / "rastreabilidade.md").write_text("\n".join(linhas) + "\n")

if erros:
    print("\n".join(erros))
    sys.exit(1)
print(f"OK · {len(fichas)} telas · {len(reqs)} requisitos · {len(ops)} operações HTTP · matriz gerada")
