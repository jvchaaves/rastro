"""Verifica a coerência da especificação e gera arquitetura/rastreabilidade.md.

Uso:
  python3 especificacoes/joao-vitor/verificar.py             # confere tudo
  python3 especificacoes/joao-vitor/verificar.py --escrever  # regenera a coluna "Telas" de requisitos.md

Confere:
- os 11 campos do template (nomes exatos) e os 6 estados de cada ficha; todo estado cita REQ ou ADR;
- ids REQ citados, operationIds, comandos cli: e campos Entidade.campo (modelo de dados e OpenAPI);
- diretiva 5: toda ação aponta uma operação, um comando cli:, um evento ou a marca "ação local",
  e toda navegação "→ Pxx" cita a operação que a tela de destino chama;
- diretiva 1: a coluna "Telas" de requisitos.md é igual às citações das fichas;
- coluna "Módulo" de requisitos.md e x-modulo de cada operação com os quatro módulos do grupo;
- atores × telas iguais no inventário e no C4 de contexto;
- cobertura: todo REQ citado por tela, ADR ou cenário; toda operação usada por alguma tela.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

BASE = Path(__file__).parent
TELAS = BASE / "telas"
ARQ = BASE / "arquitetura"
ESCREVER = "--escrever" in sys.argv

CAMPOS = ["Superfície · ator", "Objetivo", "Chega de / vai para", "Mostra", "Coleta",
          "Ações", "Estados", "Regras", "Requisitos · contrato", "Acessibilidade", "Anexo"]
ESTADOS = ["carregando", "vazio", "erro", "sucesso", "offline", "sem permissão"]
MODULOS = {"ingestao", "nucleo", "consulta", "saida", "todos"}
EVENTOS = {"lote.publicado", "alertas.gerados"}
DESTINO = {  # operação que cada tela chama ao abrir (telas/diretrizes.md, diretiva 5)
    "P01": {"obter_status"}, "P02": {"listar_emendas"}, "P03": {"obter_emenda"},
    "P04": {"obter_linha_do_tempo"}, "P05": {"listar_favorecidos"}, "P06": {"obter_agregacoes"},
    "P07": {"obter_autor"}, "P08": {"listar_mudancas"},
    "P09": {"listar_lotes", "obter_lote", "listar_traducoes"}, "P10": {"obter_municipio"},
    "D01": {"obter_contrato"}, "S01": {"listar_opcoes_filtro"}, "S02": None, "S03": None,
    "S04": {"listar_assinaturas"}, "S05": {"listar_alertas"}, "O02": {"cli:publicar"},
}
ORDEM = {"P": 0, "D": 1, "S": 2, "O": 3}


def ordenar(ids):
    return sorted(ids, key=lambda x: (ORDEM[x[0]], x))


erros: list[str] = []

# --- requisitos
req_path = ARQ / "requisitos.md"
req_txt = req_path.read_text()
LINHA_REQ = re.compile(r"^\| (REQ-\d{2}) \|(.*)\| ([^|]*) \|$", re.M)
reqs = set(re.findall(r"^\| (REQ-\d{2}) \|", req_txt, re.M))
req_modulo = {}
for m in LINHA_REQ.finditer(req_txt):
    celulas = [c.strip() for c in m.group(2).split(" | ")]
    req_modulo[m.group(1)] = celulas[-1]
    if len(celulas) != 5:
        erros.append(f"requisitos.md: {m.group(1)} não tem as 7 colunas")
for r, mod in req_modulo.items():
    if not {x.strip() for x in mod.split(",")} <= MODULOS:
        erros.append(f"requisitos.md: {r} com módulo desconhecido '{mod}'")
    linha = next(l for l in req_txt.splitlines() if l.startswith(f"| {r} |"))
    if "O SISTEMA" not in linha:
        erros.append(f"requisitos.md: {r} sem o sujeito 'O SISTEMA'")

# --- openapi
api = yaml.safe_load((ARQ / "contratos/openapi.yaml").read_text())
ops, op_modulo = {}, {}
for caminho, item in api["paths"].items():
    for metodo, op in item.items():
        if isinstance(op, dict) and "operationId" in op:
            ops[op["operationId"]] = f"{metodo.upper()} {caminho}"
            op_modulo[op["operationId"]] = op.get("x-modulo")
            if op.get("x-modulo") not in MODULOS - {"todos"}:
                erros.append(f"openapi.yaml: {op['operationId']} sem x-modulo válido")
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
cli_txt = (ARQ / "contratos/cli.md").read_text()
cli_ops = set(re.findall(r"`(cli:[a-z]+)`", cli_txt))

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

# --- diretrizes: 3 a 5 princípios verificáveis
diretrizes = (TELAS / "diretrizes.md").read_text()
principios = re.findall(r"^\d\. \*\*", diretrizes.split("## Princípios verificáveis")[1].split("\n## ")[0], re.M)
if not 3 <= len(principios) <= 5:
    erros.append(f"diretrizes.md: {len(principios)} princípios (o enunciado pede de 3 a 5)")

# --- fichas
inventario = (TELAS / "inventario.md").read_text()
ids_inv = re.findall(r"^\| ([PDSO]\d{2}) \|", inventario, re.M)
fichas = sorted(TELAS.glob("[PDSO][0-9][0-9]-*.md"), key=lambda p: (ORDEM[p.name[0]], p.name))
ids_fichas = [p.name[:3] for p in fichas]
if sorted(ids_inv) != sorted(ids_fichas):
    erros.append(f"inventário {sorted(ids_inv)} ≠ fichas {sorted(ids_fichas)}")
if len(fichas) < 10:
    erros.append("menos de 10 telas")

tela_reqs, tela_ops, req_telas, op_telas = {}, {}, defaultdict(set), defaultdict(set)
total_acoes = 0
for p in fichas:
    tid = p.name[:3]
    txt = p.read_text()
    if not txt.startswith(f"## {tid} · "):
        erros.append(f"{p.name}: título fora do template")
    for campo in CAMPOS:
        if not re.search(rf"^- \*\*{re.escape(campo)}:\*\*", txt, re.M):
            erros.append(f"{p.name}: campo ausente ou com nome fora do template '{campo}'")
    objetivo = re.search(r"^- \*\*Objetivo:\*\* (.+)$", txt, re.M)
    if objetivo and re.search(r"[.!?] [A-ZÁÉÍÓÚ]", objetivo.group(1)):
        erros.append(f"{p.name}: objetivo com mais de uma frase")
    if not (TELAS / "anexos" / f"{tid}.png").exists():
        erros.append(f"{p.name}: anexo anexos/{tid}.png não existe")

    bloco_estados = txt.split("**Estados:**")[1].split("- **Regras:**")[0]
    for e in ESTADOS:
        if f"**{e}" not in bloco_estados:
            erros.append(f"{p.name}: estado '{e}' não especificado")
    for estado in re.split(r"\n(?=  - \*\*)", bloco_estados.strip()):
        if estado.lstrip().startswith("- **") and not re.search(r"REQ-\d{2}|ADR-\d{4}", estado):
            erros.append(f"{p.name}: estado sem requisito → {estado.strip()[:60]}")

    # diretiva 5: toda ação aponta contrato
    bloco_acoes = txt.split("- **Ações:**")[1].split("- **Estados:**")[0]
    for acao in re.split(r"\n(?=  - )", bloco_acoes.strip()):
        total_acoes += 1
        citadas = set(re.findall(r"\(`([a-z]+_[a-z_]+)`", acao)) | set(re.findall(r"`(cli:[a-z]+)`", acao))
        for o in citadas:
            if o not in ops and o not in cli_ops:
                erros.append(f"{p.name}: ação cita {o}, que não existe no contrato")
        tem_evento = any(e in acao for e in EVENTOS)
        if not (citadas or tem_evento or "ação local" in acao):
            erros.append(f"{p.name}: ação sem contrato → {acao.strip()[:70]}")
        for destino in re.findall(r"→ ([PDSO]\d{2})\b", acao):
            esperado = DESTINO.get(destino)
            if esperado is None:
                if "ação local" not in acao:
                    erros.append(f"{p.name}: navegação para {destino} sem a marca 'ação local'")
            elif not esperado & citadas:
                erros.append(f"{p.name}: navegação para {destino} sem a operação de destino {sorted(esperado)}")

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
            if campo not in entidades[ent] and campo not in schema_props.get(ent, set()):
                erros.append(f"{p.name}: {ent}.{campo} não existe no modelo de dados")
        elif ent in schema_props:
            if campo not in schema_props[ent]:
                erros.append(f"{p.name}: {ent}.{campo} não existe no schema do OpenAPI")
        else:
            erros.append(f"{p.name}: entidade/schema desconhecido {ent}")

# --- diretiva 1: coluna "Telas" de requisitos.md
def telas_de(r):
    return ", ".join(ordenar(req_telas.get(r, []))) or "—"


novo_req_txt = LINHA_REQ.sub(lambda m: f"| {m.group(1)} |{m.group(2)}| {telas_de(m.group(1))} |", req_txt)
if novo_req_txt != req_txt:
    if ESCREVER:
        req_path.write_text(novo_req_txt)
        print("coluna 'Telas' de requisitos.md regenerada")
    else:
        for m in LINHA_REQ.finditer(req_txt):
            if m.group(3).strip() != telas_de(m.group(1)):
                erros.append(f"requisitos.md: {m.group(1)} Telas '{m.group(3).strip()}' ≠ fichas '{telas_de(m.group(1))}' (rode --escrever)")

# --- atores × telas: inventário = C4 de contexto
def atores(texto, secao, col):
    out = {}
    tabela = []
    for linha in texto.split(secao)[1].splitlines():
        if linha.startswith("|"):
            tabela.append(linha)
        elif tabela:
            break
    for linha in tabela[2:]:
        c = [x.strip() for x in linha.strip("|").split("|")]
        out[c[0]] = set(re.findall(r"[PDSO]\d{2}", c[col]))
    return out


inv_atores = atores(inventario, "### Atores × telas", 1)
c4 = (ARQ / "c4-contexto.md").read_text()
c4_atores = {k: v for k, v in atores(c4, "## Pessoas e sistemas externos", -1).items()
             if k in inv_atores or k.split(" (")[0] in {a.split(" (")[0] for a in inv_atores}}
for ator, telas in inv_atores.items():
    if c4_atores.get(ator) != telas:
        erros.append(f"ator '{ator}': inventário {ordenar(telas)} ≠ C4 {ordenar(c4_atores.get(ator, set()))}")

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
linhas += ["", "## Requisito → telas", "", "| Requisito | Módulo | Telas | Também em |", "| :-- | :-- | :-- | :-- |"]
for r in sorted(reqs):
    tambem = sorted({f"ADR-{f.stem[:4]}" for f in (ARQ / "adr").glob("*.md") if r in f.read_text()}
                    | ({"qualidade"} if r in (ARQ / "qualidade.md").read_text() else set()))
    linhas.append(f"| {r} | {req_modulo.get(r, '?')} | {telas_de(r)} | {', '.join(tambem) or '—'} |")
linhas += ["", "## Operação → telas", "", "| Operação | Módulo | Método e caminho | Telas |", "| :-- | :-- | :-- | :-- |"]
for o, mc in ops.items():
    linhas.append(f"| `{o}` | {op_modulo[o]} | `{mc}` | {', '.join(ordenar(op_telas[o]))} |")
for o in sorted(cli_ops):
    linhas.append(f"| `{o}` | {'nucleo' if o == 'cli:traducao' else 'ingestao'} | CLI (`contratos/cli.md`) | "
                  f"{', '.join(ordenar(op_telas.get(o, []))) or '— (agendador ou operador)'} |")
(ARQ / "rastreabilidade.md").write_text("\n".join(linhas) + "\n")

if erros:
    print("\n".join(erros))
    sys.exit(1)
adrs = len(list((ARQ / "adr").glob("*.md")))
print(f"OK · {len(fichas)} telas · {total_acoes} ações com contrato · {len(reqs)} requisitos · "
      f"{len(ops)} operações HTTP · {len(cli_ops)} comandos CLI · {adrs} ADRs · matriz gerada")
