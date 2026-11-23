#!/usr/bin/env python3
"""Coletor da Etapa 1 (Trabalho 2, João Vitor): mudanças de emendas entre lotes da CGU.

Esqueleto do tutorial, uma função por passo:
  1. obter      — baixa (ou lê) o ZIP da CGU e guarda o CSV bruto em bruto/, com a data no nome
  2. extrair    — lê o CSV com o módulo csv (nunca regex sobre o formato), com o número da linha
  3. normalizar — uma regra com nome por transformação; devolve o registro ou DESCARTE(motivo)
     3b. comparar — pareia os registros de dois lotes pelo código da emenda e monta o item de mudança
  4. deduplicar — chave estável (hash do código e dos dois lotes), não posição no arquivo
  5. gravar     — corpus.jsonl, descartes.jsonl e REGRAS.md; rodar duas vezes dá o mesmo arquivo

Uso:
  python3 coletor.py                       # recalcula tudo a partir de bruto/ (não acessa a rede)
  python3 coletor.py --baixar              # baixa o lote vigente da CGU para bruto/ e recalcula
  python3 coletor.py --obter-zip ARQ.zip --coletado-em AAAA-MM-DD   # registra um ZIP já baixado

Só biblioteca padrão do Python (3.10+).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BRUTO = AQUI / "bruto"
MANIFESTO = BRUTO / "lotes.json"
CORPUS = AQUI / "corpus.jsonl"
DESCARTES = AQUI / "descartes.jsonl"
REGRAS = AQUI / "REGRAS.md"

URL_CGU = "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO"
MEMBRO = "EmendasParlamentares.csv"
RECORTE_ANOS = {2025, 2026}

# Nome no arquivo da CGU -> nome no projeto (modelo de dados do Trabalho 1: Emenda.* e RegistroExecucao.etapa)
COLUNAS = {
    "Código da Emenda": "codigo",
    "Ano da Emenda": "ano",
    "Tipo de Emenda": "tipo",
    "Código do Autor da Emenda": "autor_codigo",
    "Nome do Autor da Emenda": "autor_nome",
    "Número da emenda": "numero",
    "Possui Apoiador/Solicitante?": "possui_apoiador",
    "Localidade de aplicação do recurso": "localidade_gasto",
    "Código Município IBGE": "municipio_ibge",
    "Município": "municipio_nome",
    "Código UF IBGE": "uf_ibge",
    "UF": "uf_gasto",
    "Região": "regiao",
    "Código Função": "funcao_codigo",
    "Nome Função": "funcao_nome",
    "Código Subfunção": "subfuncao_codigo",
    "Nome Subfunção": "subfuncao_nome",
    "Código Programa": "programa_codigo",
    "Nome Programa": "programa_nome",
    "Código Ação": "acao_codigo",
    "Nome Ação": "acao_nome",
    "Código Plano Orçamentário": "plano_orcamentario_codigo",
    "Nome Plano Orçamentário": "plano_orcamentario_nome",
    "Valor Empenhado": "empenhado_centavos",
    "Valor Liquidado": "liquidado_centavos",
    "Valor Pago": "pago_centavos",
    "Valor Restos A Pagar Inscritos": "rap_inscrito_centavos",
    "Valor Restos A Pagar Cancelados": "rap_cancelado_centavos",
    "Valor Restos A Pagar Pagos": "rap_pago_centavos",
}
ROTULO = {v: k for k, v in COLUNAS.items()}
VALORES = [c for c in COLUNAS.values() if c.endswith("_centavos")]

SIGLA_UF = {
    "ACRE": "AC", "ALAGOAS": "AL", "AMAPÁ": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARÁ": "CE",
    "DISTRITO FEDERAL": "DF", "ESPÍRITO SANTO": "ES", "GOIÁS": "GO", "MARANHÃO": "MA",
    "MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS", "MINAS GERAIS": "MG", "PARÁ": "PA",
    "PARAÍBA": "PB", "PARANÁ": "PR", "PERNAMBUCO": "PE", "PIAUÍ": "PI", "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS", "RONDÔNIA": "RO", "RORAIMA": "RR",
    "SANTA CATARINA": "SC", "SÃO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO",
}

# Regras, na ordem em que aparecem em REGRAS.md. "exemplo" é o item do bruto que motivou a regra:
# o coletor confere, a cada execução, que aquela linha ainda mostra o caso (ver conferir_exemplos).
REGRAS_DEF = [
    ("R01", "extrair", "Ler o CSV como Latin-1, separador `;`, todos os campos entre aspas, com o módulo `csv`; o número da linha física vira a proveniência",
     "qualquer linha; ex. 2026-11-19:92156", "linhas lidas"),
    ("R02", "extrair", "Tirar espaços das pontas do nome da coluna", "cabeçalho do lote 2026-11-19: `\"Possui Apoiador/Solicitante? \"` (espaço no fim)", "cabeçalhos com espaço"),
    ("R03", "normalizar", "Descartar linha com ano fora de 2025 e 2026 (`ano_fora_do_recorte`). É a primeira regra de descarte, para as seguintes dizerem respeito só ao recorte",
     "2026-10-26:2 (ano 2014)", "linhas descartadas"),
    ("R04", "normalizar", "Descartar linha com `Código da Emenda` = \"Sem informação\" (`codigo_ausente`): sem código não há como parear lotes",
     "2026-10-26:2 traz o código \"Sem informação\"; nos lotes de 26/10 e 19/11 todas as linhas assim são de 2014 a 2020 e já saem pela R03", "linhas descartadas"),
    ("R05", "normalizar", "Descartar linha cujo código não tem 12 dígitos (`codigo_invalido`)", "nenhuma linha no recorte; regra de guarda do formato documentado", "linhas descartadas"),
    ("R06", "normalizar", "Descartar a segunda ocorrência de um código no mesmo lote (`codigo_duplicado_no_lote`)", "nenhuma linha no recorte; regra de guarda da chave", "linhas descartadas"),
    ("R07", "normalizar", "Converter valor `250000,00` (vírgula decimal, sem milhar, sem `R$`) em centavos inteiros", "2026-11-19:92156, `Valor Liquidado` = `11044500,00`", "valores convertidos"),
    ("R08", "normalizar", "Trocar UF por extenso pela sigla (`PARAÍBA` → `PB`); UF fora da lista das 27 vira descarte `uf_desconhecida`", "2026-11-19:94749, UF = `PARAÍBA`", "linhas com UF"),
    ("R09", "normalizar", "`UF` = \"Sem informação\" e `Código UF IBGE` = `-1` viram nulo: emenda nacional, de uma região ou no exterior; `localidade_gasto` e `regiao` guardam qual", "2026-11-19:82700 (202542920009, localidade \"Nacional\")", "linhas com UF nula"),
    ("R10", "normalizar", "`UF` = \"Múltiplo\" e `Código UF IBGE` = `-14` viram nulo: emenda em mais de uma UF (o modelo do Trabalho 1 só previa \"Sem informação\")", "2026-10-26:82849 (202536300010), descartada por `uf_desconhecida` na primeira execução", "linhas com UF múltipla"),
    ("R11", "normalizar", "`Código Município IBGE` = \"Sem informação\" vira nulo", "2026-11-19:94749 (MÚLTIPLO, PB)", "linhas com município nulo"),
    ("R12", "normalizar", "`Município` = \"Múltiplo\" ou \"Sem informação\" vira nulo; a localidade original fica em `localidade_gasto`", "2026-11-19:94749, Município = `Múltiplo`", "linhas com nome de município nulo"),
    ("R13", "normalizar", "`Possui Apoiador/Solicitante?`: \"Sim\" → `true`, \"Não se aplica\" → nulo; a coluna só existe a partir do lote 2026-11-19", "cabeçalho do lote 2026-11-19 (coluna 7)", "linhas com a coluna"),
    ("R14", "comparar", "Parear os lotes pelo código da emenda, nunca pela posição: a mesma emenda muda de linha entre lotes", "202612460001: linha 92065 em 2026-10-26 e 92156 em 2026-11-19", "emendas pareadas"),
    ("R15", "comparar", "Não comparar campo que só existe em um dos lotes (`possui_apoiador`); ele fica no registro do lote novo", "cabeçalho do lote 2026-11-19 (coluna 7)", "emendas com o campo ignorado na comparação"),
    ("R16", "comparar", "Descartar emenda presente nos dois lotes sem nenhum campo diferente (`sem_mudanca`)", "202638970001: linha 88995 nos dois lotes, com todos os campos iguais", "emendas descartadas"),
    ("R17", "comparar", "Emenda só no lote novo vira item `nova`", "202613390002 (2026-11-19:90420)", "itens"),
    ("R18", "comparar", "Emenda só no lote anterior vira item `removida`, com a proveniência do lote anterior", "202614110020 (2026-10-26:93641)", "itens"),
    ("R19", "comparar", "Emenda nos dois lotes com campo diferente vira item `alterada`, com a lista de campos (antes, depois e, para valor, a diferença em centavos)", "202612460001 (Liquidado e Pago)", "itens"),
    ("R20", "comparar", "Derivar `estado_antes` e `estado_depois` pela regra do REQ-105 do Trabalho 1 (`sem_execucao` … `paga`), sem interpretar o motivo", "202612460001", "itens com estado"),
    ("R21", "deduplicar", "Chave = SHA-256 de `codigo|lote_anterior|lote_novo`; uma chave repetida não entra duas vezes", "todas as linhas do corpus", "chaves repetidas descartadas"),
]


# ───────────────────────── 1. OBTER ─────────────────────────

def _sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_manifesto() -> list[dict]:
    if not MANIFESTO.exists():
        return []
    return json.loads(MANIFESTO.read_text(encoding="utf-8"))


def obter(origem: str, coletado_em: str | None = None, nota: str | None = None) -> dict:
    """Baixa (URL) ou lê (caminho) o ZIP da CGU e guarda o CSV bruto em bruto/<data>_EmendasParlamentares.csv.gz.

    O CSV é guardado byte a byte como veio no ZIP (só comprimido com gzip -n, que é determinístico).
    A data no nome é a data de referência do lote: a data do arquivo dentro do ZIP.
    Idempotente: o mesmo lote não entra duas vezes no manifesto.
    """
    BRUTO.mkdir(exist_ok=True)
    cabecalhos: dict[str, str] = {}
    with tempfile.TemporaryDirectory() as tmp:
        zip_local = Path(tmp) / "lote.zip"
        if origem.startswith("http"):
            cab = {"User-Agent": "rastro-coletor/1.0 (UFPB DINF00071)"}
            etags = [l["cabecalhos_http"]["ETag"] for l in ler_manifesto() if (l.get("cabecalhos_http") or {}).get("ETag")]
            if etags:
                cab["If-None-Match"] = etags[-1]  # requisição condicional: não baixa de novo um lote já guardado
            req = urllib.request.Request(origem, headers=cab)
            try:
                resp = urllib.request.urlopen(req, timeout=300)
            except urllib.error.HTTPError as e:
                if e.code == 304:
                    print("obter: a CGU respondeu 304 (lote vigente já está em bruto/) — nada a baixar")
                    return ler_manifesto()[-1]
                raise
            with resp, open(zip_local, "wb") as out:
                shutil.copyfileobj(resp, out)
                cabecalhos = {k: resp.headers.get(k) for k in ("Last-Modified", "ETag", "Content-Length") if resp.headers.get(k)}
                url_final = resp.geturl()
            coletado_em = coletado_em or dt.date.today().isoformat()
        else:
            shutil.copyfile(origem, zip_local)
            url_final = None
            if not coletado_em:
                raise SystemExit("--coletado-em é obrigatório ao registrar um ZIP já baixado")
        with zipfile.ZipFile(zip_local) as z:
            info = z.getinfo(MEMBRO)
            data_ref = dt.date(*info.date_time[:3]).isoformat()
            membros = sorted(i.filename for i in z.infolist())
            nome_gz = f"{data_ref}_{MEMBRO}.gz"
            destino = BRUTO / nome_gz
            with z.open(info) as src:
                dados = src.read()
        manifesto = ler_manifesto()
        if any(l["data_referencia"] == data_ref for l in manifesto):
            print(f"obter: lote {data_ref} já está em bruto/ — nada a fazer")
            return next(l for l in manifesto if l["data_referencia"] == data_ref)
        with open(destino, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            gz.write(dados)
        lote = {
            "data_referencia": data_ref,
            "coletado_em": coletado_em,
            "url": URL_CGU,
            "url_final": url_final,
            "cabecalhos_http": cabecalhos or None,
            "zip_sha256": _sha256(zip_local),
            "zip_membros": membros,
            "arquivo_bruto": f"bruto/{nome_gz}",
            "csv_sha256": hashlib.sha256(dados).hexdigest(),
            "csv_bytes": len(dados),
            "nota": nota,
        }
    manifesto.append(lote)
    manifesto.sort(key=lambda l: l["data_referencia"])
    _gravar_atomico(MANIFESTO, json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n")
    print(f"obter: lote {data_ref} guardado em bruto/{nome_gz}")
    return lote


# ───────────────────────── 2. EXTRAIR ─────────────────────────

def extrair(lote: dict, contagem: Counter):
    """Gera (linha, registro_bruto) do CSV do lote, com o parser csv. A linha 1 é o cabeçalho."""
    caminho = AQUI / lote["arquivo_bruto"]
    with gzip.open(caminho, "rb") as gz:
        dados = gz.read()
    if hashlib.sha256(dados).hexdigest() != lote["csv_sha256"]:
        raise SystemExit(f"{caminho}: SHA-256 não confere com bruto/lotes.json")
    texto = io.TextIOWrapper(io.BytesIO(dados), encoding="latin-1", newline="")
    leitor = csv.reader(texto, delimiter=";", quotechar='"')
    cabecalho_original = next(leitor)
    cabecalho = [c.strip() for c in cabecalho_original]                       # R02
    contagem["R02"] += sum(1 for a, b in zip(cabecalho_original, cabecalho) if a != b)
    desconhecidas = [c for c in cabecalho if c not in COLUNAS]
    if desconhecidas:
        raise SystemExit(f"lote {lote['data_referencia']}: colunas novas não mapeadas: {desconhecidas}")
    for linha in leitor:
        contagem["R01"] += 1
        if len(linha) != len(cabecalho):
            raise SystemExit(f"lote {lote['data_referencia']} linha {leitor.line_num}: {len(linha)} campos, esperado {len(cabecalho)}")
        yield leitor.line_num, dict(zip(cabecalho, linha))


# ───────────────────────── 3. NORMALIZAR ─────────────────────────

class Descarte(Exception):
    def __init__(self, motivo: str, detalhe: str | None = None):
        super().__init__(motivo)
        self.motivo, self.detalhe = motivo, detalhe


def _centavos(valor: str) -> int:
    inteiro, sep, frac = valor.partition(",")
    if not sep or len(frac) != 2 or not inteiro.lstrip("-").isdigit() or not frac.isdigit():
        raise Descarte("valor_invalido", valor)
    sinal = -1 if inteiro.startswith("-") else 1
    return sinal * (int(inteiro.lstrip("-")) * 100 + int(frac))


def normalizar(bruto: dict, contagem: Counter) -> dict:
    """Uma regra com nome por transformação. Devolve o registro normalizado ou levanta Descarte."""
    codigo = bruto["Código da Emenda"]
    ano = int(bruto["Ano da Emenda"]) if bruto["Ano da Emenda"].isdigit() else None
    if ano not in RECORTE_ANOS:                                                # R03
        contagem["R03"] += 1
        raise Descarte("ano_fora_do_recorte", bruto["Ano da Emenda"])
    if codigo == "Sem informação":                                             # R04
        contagem["R04"] += 1
        raise Descarte("codigo_ausente", f"ano {ano}")
    if not (len(codigo) == 12 and codigo.isdigit()):                           # R05
        contagem["R05"] += 1
        raise Descarte("codigo_invalido", codigo)

    reg: dict = {}
    for coluna, nome in COLUNAS.items():
        if coluna not in bruto:
            continue
        reg[nome] = bruto[coluna]
    reg["ano"] = ano
    for nome in VALORES:                                                       # R07
        reg[nome] = _centavos(reg[nome])
        contagem["R07"] += 1
    uf = reg["uf_gasto"]
    if uf == "Sem informação":                                                 # R09
        reg["uf_gasto"] = None
        contagem["R09"] += 1
    elif uf == "Múltiplo":                                                     # R10
        reg["uf_gasto"] = None
        contagem["R10"] += 1
    else:                                                                      # R08
        if uf not in SIGLA_UF:
            raise Descarte("uf_desconhecida", uf)
        reg["uf_gasto"] = SIGLA_UF[uf]
        contagem["R08"] += 1
    if reg["uf_ibge"] in ("-1", "-14"):                                        # R09, R10
        reg["uf_ibge"] = None
    if reg["municipio_ibge"] == "Sem informação":                              # R11
        reg["municipio_ibge"] = None
        contagem["R11"] += 1
    if reg["municipio_nome"] in ("Múltiplo", "Sem informação"):                # R12
        reg["municipio_nome"] = None
        contagem["R12"] += 1
    if "possui_apoiador" in reg:                                               # R13
        contagem["R13"] += 1
        reg["possui_apoiador"] = {"Sim": True, "Não se aplica": None}.get(reg["possui_apoiador"], reg["possui_apoiador"])
    return reg


def estado_execucao(r: dict) -> str:
    """REQ-105 do Trabalho 1 (ADR-0006): etapa mais avançada e, havendo pagamento, se ele alcança o devido."""
    pagamento = r["pago_centavos"] + r["rap_pago_centavos"]
    devido = r["empenhado_centavos"] - r["rap_cancelado_centavos"]
    if pagamento > 0:
        return "paga" if pagamento >= devido else "paga_em_parte"
    if r["liquidado_centavos"] > 0:
        return "liquidada"
    if r["empenhado_centavos"] > 0:
        return "empenhada"
    return "sem_execucao"


def carregar_lote(lote: dict, contagem: Counter, descartes: list) -> dict:
    """extrair + normalizar de um lote inteiro. Devolve {codigo: (linha, registro)}."""
    registros: dict[str, tuple[int, dict]] = {}
    ref = lote["data_referencia"]
    for linha, bruto in extrair(lote, contagem):
        try:
            reg = normalizar(bruto, contagem)
            if reg["codigo"] in registros:                                     # R06
                contagem["R06"] += 1
                raise Descarte("codigo_duplicado_no_lote", f"primeira em {ref}:{registros[reg['codigo']][0]}")
            registros[reg["codigo"]] = (linha, reg)
        except Descarte as d:
            descartes.append({"lote": ref, "fonte": _fonte(lote, linha), "codigo": bruto.get("Código da Emenda"),
                              "motivo": d.motivo, "detalhe": d.detalhe})
    return registros


def _fonte(lote: dict, linha: int) -> str:
    return f"cgu-emendas/{lote['data_referencia']}_{MEMBRO}:{linha}"


# ───────────────────────── 3b. COMPARAR ─────────────────────────

def _brl(c: int) -> str:
    s = f"{abs(c) / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if c < 0 else "R$ ") + s


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def _contexto(r: dict) -> str:
    local = r["localidade_gasto"]
    return (f"Emenda {r['codigo']} ({r['ano']}), de {r['autor_nome']}, {r['tipo']}, "
            f"função {r['funcao_nome']}, local de aplicação {local}")


def _valor_txt(campo: str, v) -> str:
    if campo in VALORES:
        return _brl(v)
    return "sem informação" if v is None else str(v)


def comparar(lote_a: dict, regs_a: dict, lote_b: dict, regs_b: dict, contagem: Counter, descartes: list) -> list[dict]:
    """Pareia pelo código (R14) e monta um item por emenda nova, removida ou alterada."""
    ref_a, ref_b = lote_a["data_referencia"], lote_b["data_referencia"]
    so_em_b = {c for _, r in regs_b.values() for c in r} - {c for _, r in regs_a.values() for c in r}
    itens = []
    for codigo in sorted(set(regs_a) | set(regs_b)):
        em_a, em_b = regs_a.get(codigo), regs_b.get(codigo)
        base = {"codigo_emenda": codigo, "lote_anterior": ref_a, "lote_novo": ref_b}
        if em_a and em_b:
            contagem["R14"] += 1
            (la, ra), (lb, rb) = em_a, em_b
            if so_em_b & set(rb):
                contagem["R15"] += 1                                           # R15
            alteracoes = []
            for campo in COLUNAS.values():
                if campo not in ra or campo not in rb or ra[campo] == rb[campo]:
                    continue
                alt = {"campo": campo, "antes": ra[campo], "depois": rb[campo]}
                if campo in VALORES:
                    alt["diferenca_centavos"] = rb[campo] - ra[campo]
                alteracoes.append(alt)
            if not alteracoes:                                                 # R16
                contagem["R16"] += 1
                descartes.append({"lote": ref_b, "fonte": _fonte(lote_b, lb), "codigo": codigo, "motivo": "sem_mudanca",
                                  "detalhe": f"igual a {_fonte(lote_a, la)}"})
                continue
            contagem["R19"] += 1                                               # R19
            partes = []
            for alt in alteracoes:
                frase = f"{ROTULO[alt['campo']]} passou de {_valor_txt(alt['campo'], alt['antes'])} para {_valor_txt(alt['campo'], alt['depois'])}"
                if "diferenca_centavos" in alt:
                    d = alt["diferenca_centavos"]
                    frase += f" ({'+' if d > 0 else '-'}{_brl(abs(d))})"
                partes.append(frase)
            texto = (f"{_contexto(rb)}. Entre o lote de {_data_br(ref_a)} e o de {_data_br(ref_b)}: "
                     + "; ".join(partes) + ".")
            item = {**base, "presenca": "alterada", "alteracoes": alteracoes,
                    "estado_antes": estado_execucao(ra), "estado_depois": estado_execucao(rb),
                    "emenda": rb, "fonte_anterior": _fonte(lote_a, la)}
            fonte = _fonte(lote_b, lb)
        elif em_b:                                                             # R17
            contagem["R17"] += 1
            lb, rb = em_b
            texto = (f"{_contexto(rb)}. Aparece pela primeira vez no lote de {_data_br(ref_b)} (não estava no de {_data_br(ref_a)}), com "
                     + ", ".join(f"{ROTULO[c]} {_brl(rb[c])}" for c in VALORES) + ".")
            item = {**base, "presenca": "nova", "alteracoes": [], "estado_antes": None,
                    "estado_depois": estado_execucao(rb), "emenda": rb, "fonte_anterior": None}
            fonte = _fonte(lote_b, lb)
        else:                                                                  # R18
            contagem["R18"] += 1
            la, ra = em_a
            texto = (f"{_contexto(ra)}. Estava no lote de {_data_br(ref_a)}, com "
                     + ", ".join(f"{ROTULO[c]} {_brl(ra[c])}" for c in VALORES)
                     + f", e não aparece no lote de {_data_br(ref_b)}.")
            item = {**base, "presenca": "removida", "alteracoes": [], "estado_antes": estado_execucao(ra),
                    "estado_depois": None, "emenda": ra, "fonte_anterior": _fonte(lote_a, la)}
            fonte = _fonte(lote_a, la)
        contagem["R20"] += 1                                                   # R20
        itens.append({"texto": texto, "campos": item, "fonte": fonte, "coletado_em": lote_b["coletado_em"]})
    return itens


# ───────────────────────── 4. DEDUPLICAR ─────────────────────────

def chave(item: dict) -> str:
    c = item["campos"]
    return hashlib.sha256(f"{c['codigo_emenda']}|{c['lote_anterior']}|{c['lote_novo']}".encode()).hexdigest()


def deduplicar(itens: list[dict], contagem: Counter, descartes: list) -> list[dict]:
    vistos: dict[str, dict] = {}
    for it in itens:
        k = chave(it)
        if k in vistos:                                                        # R21
            contagem["R21"] += 1
            descartes.append({"lote": it["campos"]["lote_novo"], "fonte": it["fonte"], "codigo": it["campos"]["codigo_emenda"],
                              "motivo": "chave_repetida", "detalhe": k})
            continue
        vistos[k] = it
    saida = []
    for k, it in sorted(vistos.items(), key=lambda kv: (kv[1]["campos"]["lote_novo"], kv[1]["campos"]["codigo_emenda"])):
        c = it["campos"]
        saida.append({"id": f"rastro-mud-{c['lote_novo'].replace('-', '')}-{c['codigo_emenda']}",
                      "texto": it["texto"], "campos": c, "fonte": it["fonte"], "coletado_em": it["coletado_em"], "chave": k})
    return saida


# ───────────────────────── 5. GRAVAR ─────────────────────────

def _gravar_atomico(caminho: Path, conteudo: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=caminho.parent, prefix=caminho.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)
    os.chmod(tmp, 0o644)
    os.replace(tmp, caminho)


def _jsonl(linhas: list[dict]) -> str:
    return "".join(json.dumps(l, ensure_ascii=False, separators=(",", ":")) + "\n" for l in linhas)


def gravar(corpus: list[dict], descartes: list[dict], contagem: Counter, lotes: list[dict]) -> None:
    """Reescreve os arquivos inteiros, em ordem estável: rodar duas vezes dá bytes iguais e não duplica item."""
    _gravar_atomico(CORPUS, _jsonl(corpus))
    descartes = sorted(descartes, key=lambda d: (d["lote"], d["motivo"], d["fonte"]))
    _gravar_atomico(DESCARTES, _jsonl(descartes))
    _gravar_atomico(REGRAS, _regras_md(contagem, corpus, descartes, lotes))


def _regras_md(contagem: Counter, corpus: list[dict], descartes: list[dict], lotes: list[dict]) -> str:
    por_motivo = Counter(d["motivo"] for d in descartes)
    por_presenca = Counter(i["campos"]["presenca"] for i in corpus)
    linhas = [
        "# Regras da coleta e da normalização",
        "",
        "Gerado por `coletor.py` a cada execução: as contagens são as da última execução, e o exemplo de cada regra "
        "é conferido pelo coletor (ele para se a linha citada não mostrar mais o caso).",
        "",
        "Lotes: " + ", ".join(f"`{l['data_referencia']}` ({l['arquivo_bruto']})" for l in lotes) + ".",
        "",
        "| Regra | Passo | O que faz | Item do bruto que a motivou | Itens afetados |",
        "| :-- | :-- | :-- | :-- | --: |",
    ]
    for rid, passo, texto, exemplo, unidade in REGRAS_DEF:
        cel = lambda t: t.replace("|", "\\|")
        linhas.append(f"| {rid} | {passo} | {cel(texto)} | {cel(exemplo)} | {contagem.get(rid, 0)} {unidade} |")
    linhas += ["", "## Resultado", "",
               f"- Itens no corpus: {len(corpus)} ("
               + ", ".join(f"{k} {v}" for k, v in sorted(por_presenca.items())) + ").",
               "- Descartes em `descartes.jsonl`: " + ", ".join(f"`{k}` {v}" for k, v in sorted(por_motivo.items())) + ".",
               "- A soma das linhas lidas é igual à soma de registros pareáveis e descartes de linha "
               "(o coletor confere isso e para se não bater).", ""]
    return "\n".join(linhas)


# ───────────────────────── conferências ─────────────────────────

def conferir_exemplos(lotes: list[dict], regs: dict[str, dict], descartes: list[dict]) -> None:
    """Garante que os exemplos citados em REGRAS.md continuam verdadeiros nos lotes de bruto/."""
    a, b = regs.get("2026-10-26"), regs.get("2026-11-19")
    if a is None or b is None:
        return
    d2 = next(d for d in descartes if d["fonte"].endswith("2026-10-26_EmendasParlamentares.csv:2"))
    assert d2["motivo"] == "ano_fora_do_recorte" and d2["detalhe"] == "2014" and d2["codigo"] == "Sem informação", "R03/R04: exemplo mudou"
    assert a["202612460001"][0] == 92065 and b["202612460001"][0] == 92156, "R14: linhas do exemplo mudaram"
    assert b["202612460001"][1]["liquidado_centavos"] == 1104450000, "R07: exemplo mudou"
    assert b["202612770004"][0] == 94749 and b["202612770004"][1]["municipio_nome"] is None, "R12: exemplo mudou"
    assert "202613390002" in b and "202613390002" not in a, "R17: exemplo mudou"
    assert "202614110020" in a and "202614110020" not in b, "R18: exemplo mudou"
    assert a["202614110020"][0] == 93641 and b["202613390002"][0] == 90420, "R17/R18: linhas do exemplo mudaram"
    assert a["202638970001"][1] == {k: v for k, v in b["202638970001"][1].items() if k != "possui_apoiador"}, "R16: exemplo mudou"
    assert b["202542920009"][0] == 82700 and b["202542920009"][1]["uf_gasto"] is None, "R09: exemplo mudou"
    assert a["202536300010"][0] == 82849 and a["202536300010"][1]["uf_gasto"] is None, "R10: exemplo mudou"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baixar", action="store_true", help="baixa o lote vigente da CGU antes de recalcular")
    ap.add_argument("--obter-zip", metavar="ARQ", help="registra um ZIP da CGU já baixado")
    ap.add_argument("--coletado-em", metavar="AAAA-MM-DD", help="data em que o ZIP foi baixado (com --obter-zip)")
    ap.add_argument("--nota", help="observação gravada no manifesto (com --obter-zip)")
    args = ap.parse_args(argv)

    if args.obter_zip:
        obter(args.obter_zip, args.coletado_em, args.nota)
    if args.baixar:
        obter(URL_CGU)

    lotes = ler_manifesto()
    if len(lotes) < 2:
        print("são necessários ao menos dois lotes em bruto/lotes.json", file=sys.stderr)
        return 1

    contagem: Counter = Counter()
    descartes: list[dict] = []
    regs = {l["data_referencia"]: carregar_lote(l, contagem, descartes) for l in lotes}
    conferir_exemplos(lotes, regs, descartes)

    lidas = contagem["R01"]
    descartes_de_linha = sum(1 for d in descartes)
    pareaveis = sum(len(r) for r in regs.values())
    if lidas != pareaveis + descartes_de_linha:
        raise SystemExit(f"contagem não fecha: {lidas} lidas ≠ {pareaveis} registros + {descartes_de_linha} descartes")

    itens = []
    for anterior, novo in zip(lotes, lotes[1:]):
        itens += comparar(anterior, regs[anterior["data_referencia"]], novo, regs[novo["data_referencia"]], contagem, descartes)
    corpus = deduplicar(itens, contagem, descartes)
    gravar(corpus, descartes, contagem, lotes)
    print(f"OK · {len(lotes)} lotes · {lidas} linhas lidas · {len(corpus)} itens no corpus · {len(descartes)} descartes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
