import csv
import io
from pathlib import Path
from zipfile import ZipFile

import pytest


HEADERS = [
    "Código da Emenda",
    "Ano da Emenda",
    "Tipo de Emenda",
    "Nome do Autor da Emenda",
    "UF",
    "Nome Função",
    "Valor Empenhado",
    "Valor Liquidado",
    "Valor Pago",
]

VALID_ROW = [
    "202500010001",
    "2025",
    "Individual",
    "Autora Exemplo",
    "CE",
    "Saúde",
    "15880000,00",
    "15721200,00",
    "15721200,00",
]


def make_cgu_zip(path: Path, rows: list[list[str]], headers: list[str] | None = None) -> Path:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_ALL)
    writer.writerow(headers or HEADERS)
    writer.writerows(rows)
    with ZipFile(path, "w") as archive:
        archive.writestr("EmendasParlamentares.csv", buffer.getvalue().encode("latin-1"))
    return path


@pytest.fixture
def cgu_zip(tmp_path: Path) -> Path:
    missing_code = ["Sem informação", "2025", *VALID_ROW[2:]]
    previous_year = ["202400010001", "2024", *VALID_ROW[2:]]
    return make_cgu_zip(tmp_path / "emendas.zip", [VALID_ROW, missing_code, previous_year])
