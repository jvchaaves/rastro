from pathlib import Path

from fastapi.testclient import TestClient

from rastro.api import create_app
from rastro.store import import_zip


def test_api_returns_values_and_batch_provenance(tmp_path: Path, cgu_zip: Path):
    db_path = tmp_path / "rastro.sqlite"
    batch = import_zip(db_path, cgu_zip)
    client = TestClient(create_app(db_path))

    response = client.get("/api/emendas/202500010001")

    assert response.status_code == 200
    payload = response.json()
    assert payload["codigo"] == "202500010001"
    assert payload["uf_aplicacao"] == "CE"
    assert payload["valores_centavos"] == {
        "empenhado": 1_588_000_000,
        "liquidado": 1_572_120_000,
        "pago": 1_572_120_000,
    }
    assert payload["proveniencia"]["sha256_lote"] == batch.sha256
    assert payload["proveniencia"]["fonte"] == "Portal da Transparência / CGU"
    assert payload["proveniencia"]["url"].startswith("https://portaldatransparencia.gov.br/")
    assert "Favorecido" not in str(payload)


def test_api_distinguishes_no_batch_missing_code_and_malformed_code(tmp_path: Path, cgu_zip: Path):
    db_path = tmp_path / "rastro.sqlite"
    client = TestClient(create_app(db_path))

    assert client.get("/api/emendas/202500010001").status_code == 503
    import_zip(db_path, cgu_zip)
    assert client.get("/api/emendas/202500010002").status_code == 404
    assert client.get("/api/emendas/invalido").status_code == 422


def test_api_contract_is_published_in_openapi(tmp_path: Path):
    client = TestClient(create_app(tmp_path / "rastro.sqlite"))
    schema = client.get("/openapi.json").json()

    assert "/api/emendas/{codigo}" in schema["paths"]
    assert "EmendaResponse" in schema["components"]["schemas"]
