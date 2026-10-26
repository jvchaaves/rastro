# ADR-0003 · Separar a API FastAPI do painel Next, com tipos TypeScript gerados do OpenAPI

- **Status:** aceita
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-30, REQ-14, REQ-43, REQ-51

## Contexto

- O jornalista e o pesquisador consomem a API diretamente. O cidadão e o controle social usam o painel.
- As duas superfícies precisam mostrar os mesmos dados com a mesma proveniência.
- O princípio do Trabalho 1 é que a tela é um contrato com a arquitetura.
- Domínio declarado: Python alto, TypeScript médio (FI-01 §6).

## Opções consideradas

1. **Templates no servidor** (FastAPI + Jinja), sem front separado.
2. **Next acessando o SQLite diretamente** (rotas de servidor do Next).
3. **API FastAPI como única porta para os dados, e painel Next que só consome a API**, com tipos gerados de `../contratos/openapi.yaml` (`openapi-typescript`).

## Decisão

Opção 3.

- O arquivo `../contratos/openapi.yaml` é a fonte da verdade. A API serve um `/openapi.json` equivalente (REQ-30) e o CI compara os dois.
- O painel gera `src/api/tipos.ts` a partir do contrato. Um campo que a tela usa e não existe no contrato quebra o typecheck.
- Componentes do painel: shadcn/ui (Radix), que já traz acessibilidade de teclado e ARIA (REQ-43).

## Consequências

- **(+)** A rastreabilidade tela ↔ contrato fica verificável pelo compilador.
- **(+)** A API pública e o painel não divergem: o painel é o primeiro cliente da API.
- **(+)** O professor e o PAUL recebem contratos precisos para as tasks (`files` e `verify`).
- **(−)** São dois processos para executar e dois toolchains (Python e Node).
- **(−)** Toda mudança de campo passa por três lugares (contrato, API, tipos gerados). O CI pega a divergência, mas exige disciplina.
