from pathlib import Path

import pytest

from conftest import HEADERS, VALID_ROW, make_cgu_zip
from rastro.cgu import iter_emendas_2025, parse_brl_amount


def test_parse_brl_amount_exactly():
    assert parse_brl_amount("15880000,00") == 1_588_000_000
    assert parse_brl_amount("1.234,56") == 123_456


def test_iter_emendas_restricts_year_and_missing_codes(cgu_zip: Path):
    rows = list(iter_emendas_2025(cgu_zip))
    assert [row.codigo for row in rows] == ["202500010001"]
    assert rows[0].pago_centavos == 1_572_120_000
    assert rows[0].uf_aplicacao == "CE"


def test_invalid_money_rejects_batch(tmp_path: Path):
    invalid = [*VALID_ROW]
    invalid[-1] = "12,345"
    zip_path = make_cgu_zip(tmp_path / "invalid.zip", [invalid])
    with pytest.raises(ValueError, match="Valor monetário inválido"):
        list(iter_emendas_2025(zip_path))


def test_missing_required_column_rejects_batch(tmp_path: Path):
    zip_path = make_cgu_zip(tmp_path / "missing.zip", [VALID_ROW[:-1]], HEADERS[:-1])
    with pytest.raises(ValueError, match="Valor Pago"):
        list(iter_emendas_2025(zip_path))
