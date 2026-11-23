# C4 · Nível 2 — Contêineres (arc42 §5)

```mermaid
C4Container
    title Rastro — contêineres

    Person(cidadao, "Cidadão", "Morador ou jornalista")
    System_Ext(portal, "Portal da Transparência", "Fonte das emendas")

    System_Boundary(rastro, "Rastro (Docker Compose)") {
        Container(nav, "Navegador", "HTML + Pico.css + htmx (servidos pelo app)", "Renderiza as telas; funciona sem JS")
        Container(web, "Aplicação web", "Python 3.12, FastAPI, Jinja, Uvicorn", "Rotas HTML, fragmentos HTMX e API JSON /api/v1; só leitura")
        Container(carga, "Rotina de carga", "Python 3.12, mesmo pacote rastro, agendador APScheduler", "GET condicional do zip; se mudou, lê em streaming, filtra a PB, resolve favorecidos e convênios, valida e troca a versão ativa")
        ContainerDb(db, "Banco", "PostgreSQL 16", "municipio, autor, emenda, pagamento_favorecido, convenio, versao_carga, verificacao_fonte, termo_traduzido; views emenda_ativa e pagamento_ativo")
    }

    Rel(cidadao, nav, "Usa")
    Rel(nav, web, "GET páginas e fragmentos", "HTTPS")
    Rel(cidadao, web, "GET /api/v1/*", "HTTPS / JSON")
    Rel(web, db, "Lê só as views emenda_ativa e pagamento_ativo", "SQL, usuário rastro_leitura (somente SELECT)")
    Rel(carga, portal, "Baixa o zip só se o ETag mudou", "HTTPS")
    Rel(carga, db, "Grava versão nova; troca a ativa em uma transação", "SQL, usuário rastro_carga")
```

## Contêineres

| Contêiner | Tecnologia | Responsabilidade | Contratos | Decisões |
|---|---|---|---|---|
| Navegador | HTML gerado no servidor, Pico.css, htmx (arquivos locais, sem CDN) | Exibir as telas A01–A15; trocar fragmentos sem recarregar a página | `contratos/rotas-html.md` | ADR-0001 |
| Aplicação web | FastAPI + Jinja, Uvicorn com N workers | Atender páginas, fragmentos e a API JSON; aplicar a tradução da fase; nunca escrever no banco | `contratos/openapi.yaml`, `contratos/rotas-html.md` | ADR-0001, ADR-0003, ADR-0004, ADR-0006, ADR-0008, ADR-0009 |
| Rotina de carga | Mesmo pacote Python, processo separado; APScheduler (`BlockingScheduler`) | Executar `verificar_e_carregar` no horário; lock consultivo; validar; ativar a versão; alertar | `contratos/carga.md`, `contratos/fonte-portal.md` | ADR-0002, ADR-0005, ADR-0007 |
| Banco | PostgreSQL 16 (imagem oficial) | Persistência; garantir uma versão ativa (índice único parcial); isolar o leitor pela view | `contratos/modelo-dados.md` | ADR-0002 |

## Componentes da aplicação web (visão rápida, nível 3 parcial)

```mermaid
flowchart LR
    R1[rotas_html.py<br/>páginas e fragmentos] --> S[servicos.py<br/>uma função por operationId]
    R2[api.py<br/>/api/v1] --> S
    S --> T[traducao.py<br/>fase_simples → termo_traduzido]
    S --> Q[consultas.py<br/>SQL sobre emenda_ativa]
    Q --> DB[(PostgreSQL)]
    C[carga/<br/>fonte_portal.py · leitura_csv.py · filtro_pb.py · favorecidos.py · versao.py] --> DB
```

- `servicos.py` é o ponto único: as rotas HTML e a API chamam a mesma função. Isso garante que todo dado exibido em tela existe no contrato.
- `fonte_portal.py` isola o acesso à fonte (URL, ETag, download); trocar para a API ou para o SIGA só mexe nele. `favorecidos.py` concentra a resolução de município e de categoria (REQ-52, REQ-62).

## Implantação (mínima)

`docker-compose.yml` com três serviços: `web` (porta 8000), `carga` (sem porta; precisa de saída HTTPS para `dadosabertos-download.cgu.gov.br`) e `db` (volume persistente). Variáveis: `FONTE_URL` e `ALERTA_WEBHOOK_URL` (opcional). Hospedagem a definir com o professor (FI §12); o compose roda igual em qualquer máquina com Docker.
