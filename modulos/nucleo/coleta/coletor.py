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
  python3 coletor.py --baixar              # pede à CGU o lote vigente (requisição condicional) e recalcula
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
TEXTOS = [c for c in COLUNAS.values() if c not in VALORES and c not in ("ano", "possui_apoiador")]
ETAPA = {  # campo -> etapa do RegistroExecucao do Trabalho 1
    "empenhado_centavos": "empenhado", "liquidado_centavos": "liquidado", "pago_centavos": "pago",
    "rap_inscrito_centavos": "rap_inscrito", "rap_cancelado_centavos": "rap_cancelado", "rap_pago_centavos": "rap_pago",
}

SIGLA_UF = {
    "ACRE": "AC", "ALAGOAS": "AL", "AMAPÁ": "AP", "AMAZONAS": "AM", "BAHIA": "BA", "CEARÁ": "CE",
    "DISTRITO FEDERAL": "DF", "ESPÍRITO SANTO": "ES", "GOIÁS": "GO", "MARANHÃO": "MA",
    "MATO GROSSO": "MT", "MATO GROSSO DO SUL": "MS", "MINAS GERAIS": "MG", "PARÁ": "PA",
    "PARAÍBA": "PB", "PARANÁ": "PR", "PERNAMBUCO": "PE", "PIAUÍ": "PI", "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN", "RIO GRANDE DO SUL": "RS", "RONDÔNIA": "RO", "RORAIMA": "RR",
    "SANTA CATARINA": "SC", "SÃO PAULO": "SP", "SERGIPE": "SE", "TOCANTINS": "TO",
}

# Regras, na ordem de REGRAS.md: (id, passo, o que faz, item do bruto que a motivou, unidade da contagem).
# "Guarda" = regra para um caso que o formato documentado permite e os lotes atuais não trazem no recorte.
# Cada exemplo citado é conferido a cada execução por conferir_exemplos(); o coletor para se algum deixar de valer.
REGRAS_DEF = [
    ("R01", "extrair", "Ler o CSV como Latin-1, separador `;`, campos entre aspas, com o módulo `csv`; o número da linha física do CSV descomprimido vira a proveniência",
     "2026-11-19:92156 (202612460001)", "linhas lidas"),
    ("R02", "extrair", "Tirar espaços das pontas do nome da coluna",
     "cabeçalho do lote 2026-11-19, coluna 7: `\"Possui Apoiador/Solicitante? \"`", "nomes de coluna corrigidos"),
    ("R03", "extrair", "Coluna que o coletor não conhece é ignorada e contada aqui, sem parar a execução",
     "guarda: entre 26/10 e 19/11 a CGU acrescentou a coluna 7 (`Possui Apoiador/Solicitante?`), hoje mapeada", "colunas ignoradas"),
    ("R04", "extrair", "Linha com número de campos diferente do cabeçalho é descartada (`linha_malformada`)",
     "guarda: nenhuma linha assim nos dois lotes", "linhas descartadas"),
    ("R05", "normalizar", "Descartar linha com ano fora de 2025 e 2026 (`ano_fora_do_recorte`). É a primeira regra de descarte, para as seguintes dizerem respeito só ao recorte",
     "2026-10-26:2 (ano 2014)", "linhas descartadas"),
    ("R06", "normalizar", "Descartar linha com `Código da Emenda` = \"Sem informação\" (`codigo_ausente`): sem código não há como parear lotes",
     "2026-10-26:2 traz o código \"Sem informação\"; nos dois lotes todas as linhas assim são de 2014 a 2020 e já saem pela R05", "linhas descartadas"),
    ("R07", "normalizar", "Descartar linha cujo código não tem 12 dígitos (`codigo_invalido`)",
     "guarda: o código documentado tem 12 dígitos (ano + autor + sequência); nenhuma linha fora disso nos dois lotes", "linhas descartadas"),
    ("R08", "normalizar", "Descartar a segunda ocorrência de um código no mesmo lote (`codigo_duplicado_no_lote`)",
     "2026-11-19:48631 e 48632 repetem o código 202030410010 (2020, já fora pela R05); são 58 códigos repetidos, todos de 2020, 2023 e 2024", "linhas descartadas"),
    ("R09", "normalizar", "Em campo de texto, trocar quebra de linha e espaços repetidos por um espaço e tirar espaços das pontas",
     "guarda do esqueleto do tutorial: nenhum campo do recorte precisou", "campos alterados"),
    ("R10", "normalizar", "Converter valor `250000,00` (vírgula decimal, sem milhar, sem `R$`) em centavos inteiros; fora desse formato, descartar (`valor_malformado`, o nome do Trabalho 1)",
     "2026-11-19:92156, `Valor Liquidado` = `11044500,00`", "valores convertidos"),
    ("R11", "normalizar", "Trocar UF por extenso pela sigla (`PARAÍBA` → `PB`); UF fora das 27 e dos dois valores das R12 e R13 é descartada (`uf_desconhecida`)",
     "2026-11-19:94749 (202612770004), UF = `PARAÍBA`", "linhas com sigla"),
    ("R12", "normalizar", "`UF` = \"Sem informação\" (`Código UF IBGE` = `-1`) vira nulo: emenda nacional, de uma região ou no exterior; `localidade_gasto` e `regiao` dizem qual",
     "2026-11-19:82700 (202542920009), localidade \"Nacional\"", "linhas com UF nula"),
    ("R13", "normalizar", "`UF` = \"Múltiplo\" (`Código UF IBGE` = `-14`) vira nulo: emenda em mais de uma UF. O modelo do Trabalho 1 só previa \"Sem informação\"",
     "2026-10-26:82849 (202536300010), que a primeira execução descartou como `uf_desconhecida`", "linhas com UF múltipla"),
    ("R14", "normalizar", "`Código Município IBGE` = \"Sem informação\" vira nulo",
     "2026-11-19:94749 (202612770004), localidade MÚLTIPLO", "linhas com código de município nulo"),
    ("R15", "normalizar", "`Município` = \"Múltiplo\" ou \"Sem informação\" vira nulo; o texto original continua em `localidade_gasto` e na comparação (R19)",
     "2026-11-19:94749 (202612770004), Município = `Múltiplo`", "linhas com nome de município nulo"),
    ("R16", "normalizar", "\"Múltiplo\" em `Região`, `Nome Subfunção` e `Nome Ação` fica como está: ali é um valor do domínio, não um identificador que o módulo usa para filtrar",
     "2026-11-19:82930 (202527960009), Região = `Múltiplo`", "campos mantidos"),
    ("R17", "normalizar", "`Possui Apoiador/Solicitante?`: \"Sim\" → `true`, \"Não\" → `false`, \"Não se aplica\" → nulo; lote sem a coluna → nulo, para todo registro ter o campo",
     "cabeçalho do lote 2026-11-19, coluna 7; o lote 2026-10-26 não tem a coluna; \"Não\" aparece em 2026-11-19:19764 (2016)", "registros"),
    ("R18", "comparar", "Parear os lotes pelo código da emenda, nunca pela posição: a mesma emenda muda de linha entre lotes",
     "202612460001: linha 92065 em 2026-10-26 e 92156 em 2026-11-19", "emendas pareadas"),
    ("R19", "comparar", "Comparar campos de texto pelo valor original da CGU, não pelo normalizado: \"Sem informação\" → \"Múltiplo\" é uma mudança, embora os dois virem nulo",
     "202612770004: Município \"Sem informação\" em 2026-10-26:94554 e \"Múltiplo\" em 2026-11-19:94749", "alterações que o valor normalizado esconderia"),
    ("R20", "comparar", "Não comparar campo que só existe em um dos lotes (`possui_apoiador`)",
     "cabeçalho do lote 2026-11-19, coluna 7", "emendas pareadas com o campo fora da comparação"),
    ("R21", "comparar", "Descartar emenda presente nos dois lotes sem nenhum campo diferente (`sem_mudanca`)",
     "202638970001: linha 88995 nos dois lotes, com todos os campos iguais", "emendas descartadas"),
    ("R22", "comparar", "Emenda só no lote novo vira item `nova`", "202613390002 (2026-11-19:90420)", "itens"),
    ("R23", "comparar", "Emenda só no lote anterior vira item `removida`, com a proveniência do lote anterior", "202614110020 (2026-10-26:93641)", "itens"),
    ("R24", "comparar", "Emenda nos dois lotes com campo diferente vira item `alterada`, com cada campo antes e depois (normalizado e, em texto, também o original) e, em valor, a diferença em centavos",
     "202612460001 (Liquidado e Pago)", "itens"),
    ("R25", "comparar", "Derivar `estado_antes` e `estado_depois` pela regra do REQ-105 do Trabalho 1 (`sem_execucao` … `paga`), sem interpretar o motivo",
     "202612460001: `paga_em_parte` → `paga`", "itens com estado"),
    ("R26", "comparar", "Listar as `MudancaLote` do modelo do Trabalho 1 que a mudança gera: `nova_emenda`, `valor_alterado` (uma por etapa) e `estado_alterado`. Emenda removida e troca de local não têm tipo no modelo do Trabalho 1",
     "202612460001: `valor_alterado` liquidado e pago, mais `estado_alterado`", "linhas de MudancaLote"),
    ("R27", "deduplicar", "Chave = SHA-256 de `codigo|lote_anterior|lote_novo`; chave repetida não entra duas vezes",
     "guarda: `comparar` já gera um item por código e par de lotes", "chaves repetidas descartadas"),
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

def extrair(lote: dict, contagem: Counter, descartes: list):
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
    desconhecidas = [c for c in cabecalho if c not in COLUNAS]                 # R03
    contagem["R03"] += len(desconhecidas)
    for c in desconhecidas:
        print(f"aviso: lote {lote['data_referencia']} tem a coluna {c!r}, que o coletor não conhece; ela foi ignorada (R03)", file=sys.stderr)
    for linha in leitor:
        contagem["R01"] += 1
        if len(linha) != len(cabecalho):                                       # R04
            contagem["R04"] += 1
            descartes.append({"lote": lote["data_referencia"], "fonte": _fonte(lote, leitor.line_num), "codigo": None,
                              "motivo": "linha_malformada", "detalhe": f"{len(linha)} campos, cabeçalho tem {len(cabecalho)}"})
            continue
        yield leitor.line_num, {k: v for k, v in zip(cabecalho, linha) if k in COLUNAS}


# ───────────────────────── 3. NORMALIZAR ─────────────────────────

class Descarte(Exception):
    def __init__(self, motivo: str, detalhe: str | None = None):
        super().__init__(motivo)
        self.motivo, self.detalhe = motivo, detalhe


def _centavos(valor: str) -> int:
    inteiro, sep, frac = valor.partition(",")
    digitos = inteiro[1:] if inteiro.startswith("-") else inteiro
    if not sep or len(frac) != 2 or not digitos.isdigit() or not frac.isdigit():
        raise Descarte("valor_malformado", valor)
    sinal = -1 if inteiro.startswith("-") else 1
    return sinal * (int(digitos) * 100 + int(frac))


def normalizar(bruto: dict, contagem: Counter) -> tuple[dict, dict]:
    """Uma regra com nome por transformação. Devolve (registro normalizado, texto original por campo) ou levanta Descarte."""
    ano = int(bruto["Ano da Emenda"]) if bruto["Ano da Emenda"].isdigit() else None
    if ano not in RECORTE_ANOS:                                                # R05
        contagem["R05"] += 1
        raise Descarte("ano_fora_do_recorte", bruto["Ano da Emenda"])
    codigo = bruto["Código da Emenda"]
    if codigo == "Sem informação":                                             # R06
        contagem["R06"] += 1
        raise Descarte("codigo_ausente", f"ano {ano}")
    if not (len(codigo) == 12 and codigo.isdigit()):                           # R07
        contagem["R07"] += 1
        raise Descarte("codigo_invalido", codigo)

    original: dict = {}
    for coluna, nome in COLUNAS.items():
        if coluna in bruto:
            v = bruto[coluna]
            limpo = " ".join(v.split())                                        # R09
            if limpo != v:
                contagem["R09"] += 1
            original[nome] = limpo
    reg = dict(original)
    reg["ano"] = ano
    for nome in VALORES:                                                       # R10
        reg[nome] = _centavos(reg[nome])
        contagem["R10"] += 1
    uf = reg["uf_gasto"]
    if uf == "Sem informação":                                                 # R12
        reg["uf_gasto"] = None
        contagem["R12"] += 1
    elif uf == "Múltiplo":                                                     # R13
        reg["uf_gasto"] = None
        contagem["R13"] += 1
    elif uf in SIGLA_UF:                                                       # R11
        reg["uf_gasto"] = SIGLA_UF[uf]
        contagem["R11"] += 1
    else:
        raise Descarte("uf_desconhecida", uf)
    if reg["uf_ibge"] in ("-1", "-14"):                                        # R12, R13
        reg["uf_ibge"] = None
    if reg["municipio_ibge"] == "Sem informação":                              # R14
        reg["municipio_ibge"] = None
        contagem["R14"] += 1
    if reg["municipio_nome"] in ("Múltiplo", "Sem informação"):                # R15
        reg["municipio_nome"] = None
        contagem["R15"] += 1
    for campo in ("regiao", "subfuncao_nome", "acao_nome"):                    # R16
        if reg[campo] == "Múltiplo":
            contagem["R16"] += 1
    apoio = reg.get("possui_apoiador")                                         # R17
    reg["possui_apoiador"] = {"Sim": True, "Não": False, "Não se aplica": None, None: None}.get(apoio, apoio)
    contagem["R17"] += 1
    return reg, original


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
    """extrair + normalizar de um lote inteiro. Devolve {codigo: (linha, registro, original)}."""
    registros: dict[str, tuple[int, dict, dict]] = {}
    ref = lote["data_referencia"]
    for linha, bruto in extrair(lote, contagem, descartes):
        try:
            reg, original = normalizar(bruto, contagem)
            if reg["codigo"] in registros:                                     # R08
                raise Descarte("codigo_duplicado_no_lote", f"primeira em {_fonte(lote, registros[reg['codigo']][0])}")
            registros[reg["codigo"]] = (linha, reg, original)
        except Descarte as d:
            if d.motivo == "codigo_duplicado_no_lote":
                contagem["R08"] += 1
            descartes.append({"lote": ref, "fonte": _fonte(lote, linha), "codigo": bruto.get("Código da Emenda"),
                              "motivo": d.motivo, "detalhe": d.detalhe})
    return registros


def _fonte(lote: dict, linha: int) -> str:
    """Arquivo em bruto/ e linha do CSV descomprimido (a linha 1 é o cabeçalho)."""
    return f"{lote['arquivo_bruto']}:{linha}"


# ───────────────────────── 3b. COMPARAR ─────────────────────────

def _brl(c: int) -> str:
    s = f"{abs(c) / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("-R$ " if c < 0 else "R$ ") + s


def _data_br(iso: str) -> str:
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def _contexto(o: dict, ano: int) -> str:
    return (f"Emenda {o['codigo']} ({ano}), de {o['autor_nome']}, {o['tipo']}, "
            f"função {o['funcao_nome']}, local de aplicação {o['localidade_gasto']}")


def comparar(lote_a: dict, regs_a: dict, lote_b: dict, regs_b: dict, contagem: Counter, descartes: list) -> list[dict]:
    """Pareia pelo código (R18) e monta um item por emenda nova, removida ou alterada."""
    ref_a, ref_b = lote_a["data_referencia"], lote_b["data_referencia"]
    campos_a = {c for _, _, o in regs_a.values() for c in o}
    campos_b = {c for _, _, o in regs_b.values() for c in o}
    comuns = [c for c in COLUNAS.values() if c in campos_a and c in campos_b]
    itens = []
    for codigo in sorted(set(regs_a) | set(regs_b)):
        em_a, em_b = regs_a.get(codigo), regs_b.get(codigo)
        base = {"codigo_emenda": codigo, "lote_anterior": ref_a, "lote_novo": ref_b}
        if em_a and em_b:
            contagem["R18"] += 1
            if campos_a ^ campos_b:
                contagem["R20"] += 1                                           # R20
            (la, ra, oa), (lb, rb, ob) = em_a, em_b
            alteracoes = []
            for campo in comuns:
                if campo in VALORES:
                    if ra[campo] == rb[campo]:
                        continue
                    alteracoes.append({"campo": campo, "antes": ra[campo], "depois": rb[campo],
                                       "diferenca_centavos": rb[campo] - ra[campo]})
                    continue
                if oa[campo] == ob[campo]:                                     # R19: compara o original
                    continue
                if ra[campo] == rb[campo]:
                    contagem["R19"] += 1
                alteracoes.append({"campo": campo, "antes": ra[campo], "depois": rb[campo],
                                   "antes_cgu": oa[campo], "depois_cgu": ob[campo]})
            if not alteracoes:                                                 # R21
                contagem["R21"] += 1
                descartes.append({"lote": ref_b, "fonte": _fonte(lote_b, lb), "codigo": codigo, "motivo": "sem_mudanca",
                                  "detalhe": f"igual a {_fonte(lote_a, la)}"})
                continue
            contagem["R24"] += 1                                               # R24
            partes = []
            for alt in alteracoes:
                if "diferenca_centavos" in alt:
                    d = alt["diferenca_centavos"]
                    partes.append(f"{ROTULO[alt['campo']]} passou de {_brl(alt['antes'])} para {_brl(alt['depois'])} "
                                  f"({'+' if d > 0 else '-'}{_brl(abs(d))})")
                else:
                    partes.append(f"{ROTULO[alt['campo']]} passou de \"{alt['antes_cgu']}\" para \"{alt['depois_cgu']}\"")
            texto = (f"{_contexto(ob, rb['ano'])}. Entre o lote de {_data_br(ref_a)} e o de {_data_br(ref_b)}: "
                     + "; ".join(partes) + ".")
            antes, depois = estado_execucao(ra), estado_execucao(rb)
            mudancas = [{"tipo": "valor_alterado", "etapa": ETAPA[a["campo"]]} for a in alteracoes if a["campo"] in ETAPA]
            if antes != depois:
                mudancas.append({"tipo": "estado_alterado", "etapa": None})
            item = {**base, "presenca": "alterada", "alteracoes": alteracoes, "estado_antes": antes, "estado_depois": depois,
                    "mudancas_lote": mudancas, "emenda": rb, "fonte_anterior": _fonte(lote_a, la)}
            fonte, lote_fonte = _fonte(lote_b, lb), lote_b
        elif em_b:                                                             # R22
            contagem["R22"] += 1
            lb, rb, ob = em_b
            texto = (f"{_contexto(ob, rb['ano'])}. Aparece pela primeira vez no lote de {_data_br(ref_b)} (não estava no de {_data_br(ref_a)}), com "
                     + ", ".join(f"{ROTULO[c]} {_brl(rb[c])}" for c in VALORES) + ".")
            item = {**base, "presenca": "nova", "alteracoes": [], "estado_antes": None, "estado_depois": estado_execucao(rb),
                    "mudancas_lote": [{"tipo": "nova_emenda", "etapa": None}], "emenda": rb, "fonte_anterior": None}
            fonte, lote_fonte = _fonte(lote_b, lb), lote_b
        else:                                                                  # R23
            contagem["R23"] += 1
            la, ra, oa = em_a
            texto = (f"{_contexto(oa, ra['ano'])}. Estava no lote de {_data_br(ref_a)}, com "
                     + ", ".join(f"{ROTULO[c]} {_brl(ra[c])}" for c in VALORES)
                     + f", e não aparece no lote de {_data_br(ref_b)}.")
            item = {**base, "presenca": "removida", "alteracoes": [], "estado_antes": estado_execucao(ra), "estado_depois": None,
                    "mudancas_lote": [], "emenda": ra, "fonte_anterior": _fonte(lote_a, la)}
            fonte, lote_fonte = _fonte(lote_a, la), lote_a
        contagem["R25"] += 1                                                   # R25
        contagem["R26"] += len(item["mudancas_lote"])                          # R26
        itens.append({"texto": texto, "campos": item, "fonte": fonte, "coletado_em": lote_fonte["coletado_em"]})
    return itens


# ───────────────────────── 4. DEDUPLICAR ─────────────────────────

def chave(item: dict) -> str:
    c = item["campos"]
    return hashlib.sha256(f"{c['codigo_emenda']}|{c['lote_anterior']}|{c['lote_novo']}".encode()).hexdigest()


def deduplicar(itens: list[dict], contagem: Counter, descartes: list) -> list[dict]:
    vistos: dict[str, dict] = {}
    for it in itens:
        k = chave(it)
        if k in vistos:                                                        # R27
            contagem["R27"] += 1
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


def _ordem_fonte(d: dict) -> tuple:
    arquivo, _, linha = d["fonte"].rpartition(":")
    return (arquivo, int(linha))


def gravar(corpus: list[dict], descartes: list[dict], contagem: Counter, lotes: list[dict]) -> None:
    """Reescreve os arquivos inteiros, em ordem estável: rodar duas vezes dá bytes iguais e não duplica item."""
    _gravar_atomico(CORPUS, _jsonl(corpus))
    descartes = sorted(descartes, key=lambda d: (d["lote"], d["motivo"], _ordem_fonte(d)))
    _gravar_atomico(DESCARTES, _jsonl(descartes))
    _gravar_atomico(REGRAS, _regras_md(contagem, corpus, descartes, lotes))


def _regras_md(contagem: Counter, corpus: list[dict], descartes: list[dict], lotes: list[dict]) -> str:
    por_motivo = Counter(d["motivo"] for d in descartes)
    por_presenca = Counter(i["campos"]["presenca"] for i in corpus)
    linhas = [
        "# Regras da coleta e da normalização",
        "",
        "Gerado por `coletor.py` a cada execução. As contagens são as da última execução. O item citado em cada regra é "
        "conferido pelo coletor (`conferir_exemplos`), que para se a linha citada deixar de mostrar o caso. "
        "\"Guarda\" é a regra para um caso que o formato permite e os lotes atuais não trazem no recorte.",
        "",
        "Lotes: " + ", ".join(f"`{l['data_referencia']}` ({l['arquivo_bruto']})" for l in lotes)
        + ". Uma referência `AAAA-MM-DD:N` é a linha N do CSV descomprimido desse lote (a linha 1 é o cabeçalho).",
        "",
        "| Regra | Passo | O que faz | Item do bruto que a motivou | Itens afetados |",
        "| :-- | :-- | :-- | :-- | --: |",
    ]
    cel = lambda t: t.replace("|", "\\|")
    for rid, passo, texto, exemplo, unidade in REGRAS_DEF:
        linhas.append(f"| {rid} | {passo} | {cel(texto)} | {cel(exemplo)} | {contagem.get(rid, 0)} {unidade} |")
    linhas += ["", "## Resultado", "",
               f"- Itens no corpus: {len(corpus)} (" + ", ".join(f"{k} {v}" for k, v in sorted(por_presenca.items())) + ").",
               "- Descartes em `descartes.jsonl`: " + ", ".join(f"`{k}` {v}" for k, v in sorted(por_motivo.items())) + ".",
               f"- Linhas lidas ({contagem['R01']}) = registros do recorte + descartes de linha. O coletor confere a soma e para se não bater.",
               ""]
    return "\n".join(linhas)


# ───────────────────────── conferências ─────────────────────────

def conferir_exemplos(lotes: list[dict], regs: dict[str, dict], descartes: list[dict], cabecalhos: dict[str, list[str]]) -> None:
    """Confere que cada item citado em REGRAS_DEF ainda mostra o caso. Para (SystemExit) na primeira falha."""
    a, b = regs.get("2026-10-26"), regs.get("2026-11-19")
    if a is None or b is None:  # outro par de lotes: os exemplos citados não se aplicam
        return
    desc = {d["fonte"]: d for d in descartes}
    fa = lambda n: desc.get(f"bruto/2026-10-26_{MEMBRO}.gz:{n}", {})
    fb = lambda n: desc.get(f"bruto/2026-11-19_{MEMBRO}.gz:{n}", {})
    checks = {
        "R01": b["202612460001"][0] == 92156,
        "R02": "Possui Apoiador/Solicitante? " in cabecalhos["2026-11-19"],
        "R05": fa(2).get("motivo") == "ano_fora_do_recorte" and fa(2).get("detalhe") == "2014",
        "R06": fa(2).get("codigo") == "Sem informação",
        "R08": fb(48631).get("codigo") == fb(48632).get("codigo") == "202030410010",
        "R10": b["202612460001"][1]["liquidado_centavos"] == 1104450000,
        "R11": b["202612770004"][0] == 94749 and b["202612770004"][2]["uf_gasto"] == "PARAÍBA" and b["202612770004"][1]["uf_gasto"] == "PB",
        "R12": b["202542920009"][0] == 82700 and b["202542920009"][1]["uf_gasto"] is None and b["202542920009"][2]["localidade_gasto"] == "Nacional",
        "R13": a["202536300010"][0] == 82849 and a["202536300010"][2]["uf_gasto"] == "Múltiplo" and a["202536300010"][1]["uf_gasto"] is None,
        "R14": b["202612770004"][1]["municipio_ibge"] is None and b["202612770004"][2]["localidade_gasto"] == "MÚLTIPLO",
        "R15": b["202612770004"][2]["municipio_nome"] == "Múltiplo" and b["202612770004"][1]["municipio_nome"] is None,
        "R16": b["202527960009"][0] == 82930 and b["202527960009"][1]["regiao"] == "Múltiplo",
        "R17": "possui_apoiador" not in a["202612460001"][2] and "possui_apoiador" in b["202612460001"][2]
               and fb(19764).get("motivo") == "ano_fora_do_recorte",
        "R18": a["202612460001"][0] == 92065 and b["202612460001"][0] == 92156,
        "R19": a["202612770004"][0] == 94554 and a["202612770004"][2]["municipio_nome"] == "Sem informação"
               and b["202612770004"][2]["municipio_nome"] == "Múltiplo",
        "R20": "Possui Apoiador/Solicitante?" not in cabecalhos["2026-10-26"],
        "R21": a["202638970001"][0] == b["202638970001"][0] == 88995 and a["202638970001"][2] == {
               k: v for k, v in b["202638970001"][2].items() if k != "possui_apoiador"},
        "R22": b["202613390002"][0] == 90420 and "202613390002" not in a,
        "R23": a["202614110020"][0] == 93641 and "202614110020" not in b,
        "R24": {k for k in COLUNAS.values() if a["202612460001"][1][k] != b["202612460001"][1][k]}
               == {"liquidado_centavos", "pago_centavos"},
        "R25": (estado_execucao(a["202612460001"][1]), estado_execucao(b["202612460001"][1])) == ("paga_em_parte", "paga"),
    }
    falhas = [r for r, ok in checks.items() if not ok]
    if falhas:
        raise SystemExit(f"os exemplos de {', '.join(falhas)} em REGRAS_DEF não valem mais nestes lotes; revise as regras")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baixar", action="store_true", help="pede à CGU o lote vigente antes de recalcular")
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
    regs, cabecalhos = {}, {}
    for l in lotes:
        with gzip.open(AQUI / l["arquivo_bruto"], "rt", encoding="latin-1", newline="") as f:
            cabecalhos[l["data_referencia"]] = next(csv.reader(f, delimiter=";"))
        regs[l["data_referencia"]] = carregar_lote(l, contagem, descartes)
    conferir_exemplos(lotes, regs, descartes, cabecalhos)

    lidas, registros = contagem["R01"], sum(len(r) for r in regs.values())
    if lidas != registros + len(descartes):
        raise SystemExit(f"contagem não fecha: {lidas} linhas lidas, {registros} registros e {len(descartes)} descartes")

    itens = []
    for anterior, novo in zip(lotes, lotes[1:]):
        itens += comparar(anterior, regs[anterior["data_referencia"]], novo, regs[novo["data_referencia"]], contagem, descartes)
    corpus = deduplicar(itens, contagem, descartes)
    gravar(corpus, descartes, contagem, lotes)
    print(f"OK: {len(lotes)} lotes, {lidas} linhas lidas, {len(corpus)} itens no corpus, {len(descartes)} descartes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
