# UNIFY — Primeira fatia CGU

**Data:** 24/09/2026  
**Plano:** `../../../docs/superpowers/plans/2026-09-24-rastro-primeira-fatia.md`  
**Modo:** ciclo manual no Codex; comandos `/paul:*` não executados.

## Planejado e entregue

| Objetivo do PLAN | Resultado do APPLY |
| --- | --- |
| Ler ZIP oficial da CGU e selecionar códigos válidos de emendas de 2025 | Parser em fluxo, CSV Latin-1 com `;`, valores em centavos; 6.311 linhas de 2025 lidas do pacote examinado |
| Publicar lote SQLite sem expor importação parcial | Inserção e troca do lote ativo em transação; teste com consulta durante a importação |
| Reimportar sem duplicação | Hash SHA-256 identifica lote; reimportação não duplica e não reativa pacote antigo |
| Consultar emenda por código e mostrar proveniência | `GET /api/emendas/{codigo}` documentado no OpenAPI; fonte, URL, hash e data de importação na resposta |

## Critérios de aceitação

- **AC-1:** aprovado. O lote sintético foi importado e a API devolveu código, valores em centavos e proveniência. Em teste HTTP local com o lote oficial, `202538970001` retornou `200` e valores `1588000000`, `1572120000`, `1572120000` centavos, iguais aos do CSV examinado.
- **AC-2:** aprovado. Reimportar o mesmo ZIP conserva uma linha por código e um lote por hash. Um teste adicional impediu que a reimportação de um pacote antigo substituísse o lote ativo mais recente.
- **Segurança da publicação:** aprovado no escopo da fatia. Um teste suspendeu uma importação e confirmou que o leitor ainda via o lote anterior; após o commit, passou a ver o novo.

## Evidência reproduzível

- `.venv/bin/python -m pytest -q`: **13 passaram**, com um aviso de depreciação no `TestClient` do FastAPI/Starlette instalado; o aviso não alterou o resultado.
- `git diff --check`: sem erros.
- Importação do ZIP da CGU com SHA-256 `db34554b2207ef2a1a0a94a4c8ca26e3e9402729bb2a3797ee85a31d7fecf2d4`: 6.311 linhas aceitas, 17.810 sem código válido e 70.456 de outros anos.
- API local iniciada com Uvicorn e consultada por HTTP; servidor encerrado após a verificação.

O ZIP e o SQLite usados na verificação estão fora do Git. O pacote oficial pode mudar, por isso os números descrevem apenas o arquivo identificado pelo hash acima.

## Diferenças em relação ao PLAN

- `ParseStats` foi acrescentado ao parser para registrar motivos de exclusão de linha.
- A tabela `batches` registra as contagens de linhas aceitas e excluídas.
- A importação de um hash já conhecido não altera o lote ativo, após o teste mostrar que o comportamento anterior poderia publicar dados antigos.

## Decisões e pendências

- Permanece o recorte provisório por ano da emenda 2025.
- Python/FastAPI/SQLite continuam uma escolha técnica provisória; o domínio do estudante não foi informado.
- O Siga Brasil ainda não tem extração automatizada e chave de junção demonstradas.
- Painel, favorecidos, assinaturas, alertas e desempenho comparativo pertencem a ciclos seguintes do MVP.
