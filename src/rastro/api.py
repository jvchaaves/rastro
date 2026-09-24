"""Contrato HTTP de consulta da primeira fatia do Rastro."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path as PathParam
from pydantic import BaseModel

from rastro.store import get_active_emenda, has_active_batch


class ValoresCentavos(BaseModel):
    empenhado: int
    liquidado: int
    pago: int


class Proveniencia(BaseModel):
    fonte: str
    url: str
    sha256_lote: str
    importado_em: str


class EmendaResponse(BaseModel):
    codigo: str
    ano: int
    tipo: str
    autor: str
    uf_aplicacao: str
    funcao: str
    valores_centavos: ValoresCentavos
    proveniencia: Proveniencia


def create_app(db_path: Path) -> FastAPI:
    application = FastAPI(title="Rastro", version="0.1.0")

    @application.get("/api/emendas/{codigo}", response_model=EmendaResponse)
    def read_emenda(codigo: Annotated[str, PathParam(pattern=r"^[0-9]{12}$")]) -> EmendaResponse:
        if not has_active_batch(db_path):
            raise HTTPException(status_code=503, detail="Nenhum lote publicado")
        result = get_active_emenda(db_path, codigo)
        if result is None:
            raise HTTPException(status_code=404, detail="Emenda não encontrada no lote publicado")
        emenda, batch = result
        return EmendaResponse(
            codigo=emenda.codigo,
            ano=emenda.ano,
            tipo=emenda.tipo,
            autor=emenda.autor,
            uf_aplicacao=emenda.uf_aplicacao,
            funcao=emenda.funcao,
            valores_centavos=ValoresCentavos(
                empenhado=emenda.empenhado_centavos,
                liquidado=emenda.liquidado_centavos,
                pago=emenda.pago_centavos,
            ),
            proveniencia=Proveniencia(
                fonte="Portal da Transparência / CGU",
                url=batch.source_url,
                sha256_lote=batch.sha256,
                importado_em=batch.imported_at,
            ),
        )

    return application


app = create_app(Path(os.environ.get("RASTRO_DB", "data/rastro.sqlite")))
