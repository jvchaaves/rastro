"""Lotes versionados da CGU em SQLite."""

import hashlib
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rastro.cgu import Emenda, ParseStats, iter_emendas_2025


SOURCE_URL = "https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares"

SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    sha256 TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    accepted_rows INTEGER NOT NULL,
    skipped_missing_code INTEGER NOT NULL,
    skipped_other_year INTEGER NOT NULL
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
CREATE TABLE IF NOT EXISTS state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class BatchInfo:
    sha256: str
    source_url: str
    imported_at: str


@dataclass(frozen=True)
class ImportResult:
    sha256: str
    imported_rows: int
    skipped_missing_code: int
    skipped_other_year: int
    reused: bool
    imported_at: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _open_database(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def _set_active_batch(conn: sqlite3.Connection, sha256: str) -> None:
    conn.execute(
        "INSERT INTO state(key, value) VALUES('active_batch', ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (sha256,),
    )


def import_zip(db_path: Path, zip_path: Path) -> ImportResult:
    sha256 = _sha256_file(zip_path)
    with closing(_open_database(db_path)) as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            existing = conn.execute("SELECT * FROM batches WHERE sha256=?", (sha256,)).fetchone()
            if existing is not None:
                conn.commit()
                return ImportResult(
                    sha256=sha256,
                    imported_rows=existing["accepted_rows"],
                    skipped_missing_code=existing["skipped_missing_code"],
                    skipped_other_year=existing["skipped_other_year"],
                    reused=True,
                    imported_at=existing["imported_at"],
                )

            imported_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            conn.execute(
                "INSERT INTO batches VALUES (?, ?, ?, 0, 0, 0)",
                (sha256, SOURCE_URL, imported_at),
            )
            stats = ParseStats()
            seen_codes: set[str] = set()
            for amendment in iter_emendas_2025(zip_path, stats):
                if amendment.codigo in seen_codes:
                    raise ValueError(f"Código duplicado no recorte de 2025: {amendment.codigo}")
                seen_codes.add(amendment.codigo)
                conn.execute(
                    "INSERT INTO emendas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        sha256,
                        amendment.codigo,
                        amendment.ano,
                        amendment.tipo,
                        amendment.autor,
                        amendment.uf_aplicacao,
                        amendment.funcao,
                        amendment.empenhado_centavos,
                        amendment.liquidado_centavos,
                        amendment.pago_centavos,
                    ),
                )
            if stats.accepted == 0:
                raise ValueError("Nenhuma emenda de 2025 encontrada no ZIP")
            conn.execute(
                "UPDATE batches SET accepted_rows=?, skipped_missing_code=?, skipped_other_year=? "
                "WHERE sha256=?",
                (
                    stats.accepted,
                    stats.skipped_missing_code,
                    stats.skipped_other_year,
                    sha256,
                ),
            )
            _set_active_batch(conn, sha256)
            conn.commit()
            return ImportResult(
                sha256=sha256,
                imported_rows=stats.accepted,
                skipped_missing_code=stats.skipped_missing_code,
                skipped_other_year=stats.skipped_other_year,
                reused=False,
                imported_at=imported_at,
            )
        except Exception:
            conn.rollback()
            raise


def has_active_batch(db_path: Path) -> bool:
    if not db_path.exists():
        return False
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute("SELECT value FROM state WHERE key='active_batch'").fetchone()
        return row is not None


def get_active_emenda(db_path: Path, codigo: str) -> tuple[Emenda, BatchInfo] | None:
    if not db_path.exists():
        return None
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT e.*, b.sha256, b.source_url, b.imported_at "
            "FROM state s JOIN emendas e ON e.batch_sha256=s.value "
            "JOIN batches b ON b.sha256=e.batch_sha256 "
            "WHERE s.key='active_batch' AND e.codigo=?",
            (codigo,),
        ).fetchone()
        if row is None:
            return None
        amendment = Emenda(
            codigo=row["codigo"],
            ano=row["ano"],
            tipo=row["tipo"],
            autor=row["autor"],
            uf_aplicacao=row["uf_aplicacao"],
            funcao=row["funcao"],
            empenhado_centavos=row["empenhado_centavos"],
            liquidado_centavos=row["liquidado_centavos"],
            pago_centavos=row["pago_centavos"],
        )
        batch = BatchInfo(
            sha256=row["sha256"],
            source_url=row["source_url"],
            imported_at=row["imported_at"],
        )
        return amendment, batch
