# ADR-0001 · Renderizar as telas no servidor com Jinja e HTMX

- **Status:** aceita (24/09/2026, FI-01 §6)
- **Contexto:** O usuário principal usa celular com conexão fraca, de forma eventual. A autora não domina frontend e precisa auditar o código gerado na camada que é o centro da proposta: a tradução exibida. A disciplina exige uma API com contrato. As telas são de leitura, sem edição.
- **Opções consideradas:**
  1. SPA em React/TypeScript consumindo a API JSON.
  2. HTML no servidor (FastAPI + Jinja) com HTMX para atualizações parciais e Pico.css para estilo.
  3. Site estático gerado a cada carga.
- **Decisão:** Opção 2. A aplicação FastAPI expõe a API JSON (`/api/v1`) e as rotas HTML. As duas chamam a mesma camada de serviço (`servicos.py`). O htmx e o Pico.css são servidos localmente. As páginas funcionam sem JS (REQ-41).
- **Consequências:**
  - \+ Primeira abertura leve: sem pacote JS de SPA (Q4).
  - \+ Código auditável em Python/Jinja; o contrato OpenAPI é gerado dos tipos.
  - \+ Um único lugar para a regra de tradução: a tela e a API não divergem.
  - − Interações ricas (gráficos interativos) ficam difíceis; aceito, porque o FI não pede gráficos.
  - − O estado offline depende do navegador; tratado só para falha de fragmento (REQ-42).
  - Opção 1 descartada: a responsividade vem do CSS, e o pacote JS pesa no 3G (FI §6.1). Opção 3 descartada: a busca com sugestões e os filtros exigiriam JS próprio ou índices pré-gerados para 223 municípios × anos × fases.
