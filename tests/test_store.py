import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event

import pytest

from conftest import VALID_ROW, make_cgu_zip
from rastro import store
from rastro.store import get_active_emenda, has_active_batch, import_zip


def test_import_is_idempotent_and_counts_skipped_rows(tmp_path: Path, cgu_zip: Path):
    db_path = tmp_path / "rastro.sqlite"

    first = import_zip(db_path, cgu_zip)
    second = import_zip(db_path, cgu_zip)

    assert first.sha256 == second.sha256
    assert first.imported_rows == 1
    assert first.skipped_missing_code == 1
    assert first.skipped_other_year == 1
    assert second.reused is True
    assert has_active_batch(db_path)
    assert get_active_emenda(db_path, "202500010001")[0].pago_centavos == 1_572_120_000
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM emendas").fetchone()[0] == 1


def test_failed_import_keeps_previous_active_batch(tmp_path: Path, cgu_zip: Path):
    db_path = tmp_path / "rastro.sqlite"
    first = import_zip(db_path, cgu_zip)
    bad_row = [*VALID_ROW]
    bad_row[-1] = "valor inválido"
    bad_zip = make_cgu_zip(tmp_path / "bad.zip", [bad_row])

    with pytest.raises(ValueError, match="Valor monetário inválido"):
        import_zip(db_path, bad_zip)

    current = get_active_emenda(db_path, "202500010001")
    assert current is not None
    assert current[1].sha256 == first.sha256


def test_duplicate_code_rejects_new_batch(tmp_path: Path):
    db_path = tmp_path / "rastro.sqlite"
    duplicate = [*VALID_ROW]
    duplicate[-1] = "1,00"
    zip_path = make_cgu_zip(tmp_path / "duplicates.zip", [VALID_ROW, duplicate])

    with pytest.raises(ValueError, match="Código duplicado"):
        import_zip(db_path, zip_path)

    assert not has_active_batch(db_path)


def test_empty_2025_slice_is_not_published(tmp_path: Path):
    db_path = tmp_path / "rastro.sqlite"
    previous_year = ["202400010001", "2024", *VALID_ROW[2:]]
    zip_path = make_cgu_zip(tmp_path / "previous.zip", [previous_year])

    with pytest.raises(ValueError, match="Nenhuma emenda de 2025"):
        import_zip(db_path, zip_path)

    assert not has_active_batch(db_path)


def test_readers_keep_old_batch_during_new_import(tmp_path: Path, cgu_zip: Path, monkeypatch):
    db_path = tmp_path / "rastro.sqlite"
    old_batch = import_zip(db_path, cgu_zip)
    updated_row = [*VALID_ROW]
    updated_row[-1] = "1,00"
    updated_zip = make_cgu_zip(tmp_path / "updated.zip", [updated_row])

    importing = Event()
    resume = Event()
    original_iterator = store.iter_emendas_2025

    def paused_iterator(zip_path, stats):
        for amendment in original_iterator(zip_path, stats):
            importing.set()
            if not resume.wait(timeout=5):
                raise TimeoutError("A importação não foi liberada pelo teste")
            yield amendment

    monkeypatch.setattr(store, "iter_emendas_2025", paused_iterator)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(import_zip, db_path, updated_zip)
        try:
            assert importing.wait(timeout=5)
            during = get_active_emenda(db_path, "202500010001")
            assert during is not None
            assert during[1].sha256 == old_batch.sha256
            assert during[0].pago_centavos == 1_572_120_000
        finally:
            resume.set()
        new_batch = future.result(timeout=5)

    after = get_active_emenda(db_path, "202500010001")
    assert after is not None
    assert after[1].sha256 == new_batch.sha256
    assert after[0].pago_centavos == 100
