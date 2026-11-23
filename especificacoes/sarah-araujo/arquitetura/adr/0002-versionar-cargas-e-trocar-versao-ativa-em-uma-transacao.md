# ADR-0002 · Versionar cada carga e trocar a versão ativa em uma única transação

- **Status:** aceita (FI-01 §9.1)
- **Contexto:** Os valores empenhados e pagos mudam com o tempo, e a carga roda com o sistema no ar. Um leitor que consulte durante a carga não pode ver metade dos dados de ontem misturada com metade dos de hoje (REQ-34). Se a carga falhar, os dados anteriores precisam continuar no ar (REQ-35).
- **Opções consideradas:**
  1. `UPDATE`/`UPSERT` em uma tabela única de emendas, linha a linha.
  2. Carga em tabela de staging + `ALTER TABLE … RENAME` ao final.
  3. Tabela `versao_carga`; cada emenda pertence a uma versão; flag `ativa` com índice único parcial; troca da flag em uma transação; leitura sempre pela view `emenda_ativa`.
- **Decisão:** Opção 3, com os passos em `contratos/carga.md`. Mantém-se a versão ativa e uma anterior (REQ-37).
- **Consequências:**
  - \+ Atomicidade garantida pelo PostgreSQL; nenhum código de aplicação precisa coordenar leitores.
  - \+ Histórico das cargas visível em A10 (REQ-40); rollback manual possível reativando a anterior.
  - \+ "No máximo uma ativa" vira restrição do banco, não convenção.
  - − Os dados ficam duplicados durante a carga (≈ 2× o volume da PB); aceito (FI §9.1).
  - − Toda consulta precisa passar pela view; mitigado concedendo ao usuário `rastro_leitura` acesso **só** à view.
  - Opção 1 descartada: o leitor vê o estado intermediário. Opção 2 descartada: o `RENAME` exige lock exclusivo e perde o histórico.
