"""Leitura do CSV de emendas publicado pela CGU."""

import csv
import io
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile


CSV_MEMBER = "EmendasParlamentares.csv"
VALID_CODE = re.compile(r"[0-9]{12}\Z")
VALID_MONEY = re.compile(r"-?(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+),[0-9]{2}\Z")
REQUIRED_COLUMNS = {
    "Código da Emenda",
    "Ano da Emenda",
    "Tipo de Emenda",
    "Nome do Autor da Emenda",
    "UF",
    "Nome Função",
    "Valor Empenhado",
    "Valor Liquidado",
    "Valor Pago",
}


@dataclass(frozen=True)
class Emenda:
    codigo: str
    ano: int
    tipo: str
    autor: str
    uf_aplicacao: str
    funcao: str
    empenhado_centavos: int
    liquidado_centavos: int
    pago_centavos: int


@dataclass
class ParseStats:
    accepted: int = 0
    skipped_missing_code: int = 0
    skipped_other_year: int = 0


def parse_brl_amount(value: str) -> int:
    text = value.strip()
    if not VALID_MONEY.fullmatch(text):
        raise ValueError(f"Valor monetário inválido: {value!r}")
    amount = Decimal(text.replace(".", "").replace(",", "."))
    cents = amount * 100
    return int(cents)


def iter_emendas_2025(zip_path: Path, stats: ParseStats | None = None) -> Iterator[Emenda]:
    stats = stats if stats is not None else ParseStats()
    try:
        with ZipFile(zip_path) as archive:
            with archive.open(CSV_MEMBER) as raw:
                text = io.TextIOWrapper(raw, encoding="latin-1", newline="")
                reader = csv.DictReader(text, delimiter=";")
                missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
                if missing:
                    raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")
                for row in reader:
                    code = row["Código da Emenda"].strip()
                    if not VALID_CODE.fullmatch(code):
                        stats.skipped_missing_code += 1
                        continue
                    if not code.startswith("2025"):
                        stats.skipped_other_year += 1
                        continue
                    year = row["Ano da Emenda"].strip()
                    if year != "2025":
                        raise ValueError(f"Ano incoerente para a emenda {code}: {year!r}")
                    emenda = Emenda(
                        codigo=code,
                        ano=2025,
                        tipo=row["Tipo de Emenda"].strip(),
                        autor=row["Nome do Autor da Emenda"].strip(),
                        uf_aplicacao=row["UF"].strip(),
                        funcao=row["Nome Função"].strip(),
                        empenhado_centavos=parse_brl_amount(row["Valor Empenhado"]),
                        liquidado_centavos=parse_brl_amount(row["Valor Liquidado"]),
                        pago_centavos=parse_brl_amount(row["Valor Pago"]),
                    )
                    stats.accepted += 1
                    yield emenda
    except KeyError as exc:
        raise ValueError(f"Arquivo obrigatório ausente no ZIP: {CSV_MEMBER}") from exc
