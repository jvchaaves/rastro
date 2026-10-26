# Arquitetura do Rastro — índice

Especificação arquitetural do sistema completo **Rastro: para onde vão as emendas parlamentares**, feita a partir do FI-01 (24/09/2026). É a entrada do PAUL (`/paul:init`, `/paul:plan`) e o contrato das telas em `../telas/`.

## Padrão escolhido: arc42 enxuto

O padrão é o **arc42** (Starke e Hruschka) como índice. Cada seção usa a notação mais adequada:

| Seção arc42 | Conteúdo | Notação | Arquivo |
| :-- | :-- | :-- | :-- |
| §1 Introdução e metas | Metas, partes interessadas | texto | este README |
| §2 Restrições | Stack, execução, dados, prazo | texto | este README |
| §3 Contexto | Atores, sistemas externos, limites | C4 nível 1 (Mermaid) | [c4-contexto.md](c4-contexto.md) |
| §5 Blocos de construção | Contêineres e módulos | C4 nível 2 (Mermaid) | [c4-conteineres.md](c4-conteineres.md) |
| §9 Decisões | 7 decisões com o porquê | ADR (MADR) | [adr/](adr/) |
| §10 Qualidade | 5 cenários, um por item do envelope | Bass, Clements e Kazman (6 partes) | [qualidade.md](qualidade.md) |
| §12 Glossário | Vocabulário do domínio e do sistema | texto | [glossario.md](glossario.md) |
| — Requisitos | 65 requisitos testáveis | EARS | [requisitos.md](requisitos.md) |
| — Contratos | API HTTP, eventos internos, CLI e modelo de dados | OpenAPI 3.1, AsyncAPI 3.0, Markdown, Mermaid ER | [contratos/](contratos/) |
| — Rastreabilidade | Tela ↔ requisito ↔ contrato | matriz gerada por script | [rastreabilidade.md](rastreabilidade.md) |

As seções §4 (estratégia de solução), §6 (visão de execução), §7 (implantação) e §8 (conceitos transversais) não têm arquivo próprio, porque o conteúdo delas já está em outros documentos:

- a estratégia está nas ADR-0001 a 0004;
- a execução está em `contratos/cli.md` e `contratos/eventos.asyncapi.yaml`;
- a implantação está no fim de `c4-conteineres.md`;
- os conceitos transversais (proveniência, etapas distintas, estados de interface) estão em `requisitos.md` (grupos B e D) e em `../telas/diretrizes.md`.

### Por que este padrão: as seis informações que o PAUL consome

| O PAUL precisa de | Onde está nesta especificação | Como vira entrada do PAUL |
| :-- | :-- | :-- |
| **Limites e vizinhos** | `c4-contexto.md` (atores, CGU, Siga, agendador; seção "Limites") e `c4-conteineres.md` (quem escreve no banco) | Escopo do `PROJECT.md` e *boundaries* de cada plano. Exemplo: "a API não escreve dados de fonte", "nenhum canal externo de alerta" |
| **Decisões e porquês** | `adr/0001`–`0007`, com opções descartadas e consequências | Decisões que o agente não reabre a cada sessão (lote imutável, SQLite WAL, chave anônima…) |
| **Contratos** | `contratos/openapi.yaml` (18 operações), `contratos/eventos.asyncapi.yaml`, `contratos/cli.md`, `contratos/modelo-de-dados.md` | Tasks com `files` e `verify` precisos. Exemplo: "`obter_emenda` responde 422/404/503 conforme o contrato" |
| **Requisitos testáveis** | `requisitos.md`: 65 REQ em EARS, cada um com o teste que o verifica e a origem no FI-01 | Critérios de aceite Given/When/Then. O molde EARS traduz direto: QUANDO → *When*, SE … ENTÃO → *Given/Then*. A tabela final liga AC-1…AC-4 do FI-01 aos REQ |
| **Qualidade com medida** | `qualidade.md`: QA-01 persistência, QA-02 API, QA-03 concorrência, QA-04 desempenho medido, QA-05 testes | ACs do envelope com número e ferramenta de medida (0 mistura de lotes em 100 execuções, p95 < 100 ms, cobertura ≥ 80%) |
| **Restrições** | §2 abaixo, ADR-0002 (execução local), ADR-0005 e ADR-0007 (dados pessoais) | Stack, hospedagem e LGPD que o *audit* cobra |

**Alternativas consideradas:**

- **arc42 completo** duplicaria seções vazias num MVP de 60 horas.
- **4+1 / ISO 42010** exigiria visões (por exemplo, a física) com pouco conteúdo aqui.
- **Spec Kit / Kiro** cobrem bem requisitos e tarefas, mas não têm lugar natural para C4 nem para cenários de qualidade.

O arc42 enxuto dá um índice reconhecível e deixa cada peça na notação que o próprio enunciado pede (C4, MADR, EARS, OpenAPI, cenários de 6 partes).

## §1 Metas

**Missão:** permitir que cidadãos, jornalistas e organizações de controle social acompanhem o caminho dos recursos de emendas parlamentares federais. O caminho vai da indicação ao pagamento, sem confundir valor empenhado, liquidado, pago e recebido por favorecido, e sempre com a origem de cada dado.

| Meta de qualidade (prioridade) | Por quê | Onde é medida |
| :-- | :-- | :-- |
| 1. **Confiabilidade da atribuição** (proveniência em todo valor) | Risco alto de atribuição incorreta (brief, FI-01 §3.2) | REQ-14, REQ-15, princípio 1 das diretrizes, QA-02 |
| 2. **Consistência sob atualização** (nenhuma mistura de lotes, alertas sem duplicata) | Gancho de concorrência do brief | REQ-09, REQ-36, QA-01, QA-03 |
| 3. **Desempenho medido** (consulta e ETL) | Gancho de desempenho do brief | REQ-49, REQ-50, QA-04 |
| 4. **Acessibilidade** (WCAG 2.2 AA) | Público cidadão, inclusive no celular | REQ-43, `../telas/diretrizes.md` |

| Parte interessada | Expectativa |
| :-- | :-- |
| Cidadão | Saber quanto foi para onde e de quem, em linguagem simples |
| Jornalista ou pesquisador | Números exatos, reproduzíveis e citáveis, com API |
| Controle social | Acompanhar mudanças sem consultar tudo de novo manualmente |
| Operador de dados | Publicar só lotes válidos e saber por que um lote foi recusado |
| Favorecidos e parlamentares (afetados) | Não ser associados a irregularidade nem expostos além da fonte (ADR-0007) |
| Professor e grupo (consolidação) | Ids estáveis, contratos explícitos e decisões com o porquê |

## §2 Restrições

| Restrição | Origem |
| :-- | :-- |
| Back-end Python 3.12 + FastAPI + SQLite; front-end Next + TypeScript + shadcn/ui | FI-01 §6 e §10.2 |
| Execução local em macOS, dois processos (API, painel) mais a CLI; sem servidor dedicado | FI-01 §10.3 |
| Apenas dados públicos baixados (CGU; Siga Brasil sujeito a validação); arquivos de dados fora do Git | FI-01 §10.3, §10.4 |
| Recorte do MVP: emendas federais de 2025 com código válido | FI-01 §4.3 |
| Alerta só no painel, sem envio externo e sem dado pessoal do assinante | FI-01 §10.2, ADR-0005 |
| Nenhum julgamento de irregularidade e nenhuma afirmação sobre aplicação final | FI-01 §5 |
| Disciplina de 60 horas; conta Claude Pro; modelo local parcial a partir da semana 8 | FI-01 §10.3 |
| LGPD: só o que a fonte publica; favorecido pessoa física sem busca; nenhum dado pessoal de usuários | ADR-0005, ADR-0007 |

## Lacunas do FI-01 fechadas por esta especificação

| Lacuna (FI-01 §12) | Decisão |
| :-- | :-- |
| Identidade do assinante | Chave anônima de 128 bits ([ADR-0005](adr/0005-identificar-assinantes-por-chave-anonima.md)) |
| Definição de mudança de status | Estado derivado da etapa mais avançada ([ADR-0006](adr/0006-derivar-estado-de-execucao-da-etapa-mais-avancada.md), status *proposta*) |
| Exibição de favorecidos pessoa física | Como publicado pela CGU, sem busca ([ADR-0007](adr/0007-exibir-favorecido-pf-como-publicado-sem-busca-por-pessoa.md)) |
| Limites de uso da API | 60 req/min por IP (REQ-28) |
| Carga do ensaio de desempenho | 20 usuários virtuais por 60 s, com alvos provisórios até o baseline (QA-04) |

Lacunas que continuam abertas:

- **Extração e chave de vínculo do Siga Brasil:** REQ-13 é *opcional* e entra na fase 6.
- **Frequência da sincronização:** será definida depois de observar duas atualizações da CGU. A especificação só exige que `rastro sincronizar` seja idempotente.

## Decisões (ADR)

| ADR | Decisão | Status |
| :-- | :-- | :-- |
| [0001](adr/0001-publicar-por-lote-imutavel-com-troca-atomica.md) | Publicar por lote imutável com troca atômica do lote ativo | aceita |
| [0002](adr/0002-usar-sqlite-wal-com-escritor-unico.md) | SQLite em WAL, escritor único, leitura em snapshot | aceita |
| [0003](adr/0003-separar-api-fastapi-e-painel-next-com-tipos-gerados.md) | API FastAPI separada do painel Next, tipos gerados do OpenAPI | aceita |
| [0004](adr/0004-calcular-mudancas-na-publicacao-e-gerar-alertas-idempotentes.md) | MudancaLote na publicação; alertas idempotentes por (assinatura, mudança) | aceita |
| [0005](adr/0005-identificar-assinantes-por-chave-anonima.md) | Assinante identificado por chave anônima | aceita |
| [0006](adr/0006-derivar-estado-de-execucao-da-etapa-mais-avancada.md) | Estado de execução derivado da etapa mais avançada | proposta |
| [0007](adr/0007-exibir-favorecido-pf-como-publicado-sem-busca-por-pessoa.md) | Favorecido PF como publicado, sem busca por pessoa | aceita |

## Como verificar a coerência

```bash
pip install pyyaml
python3 especificacoes/joao-vitor/verificar.py
```

O script confere e regenera a matriz [`rastreabilidade.md`](rastreabilidade.md). O que ele confere:

- os 11 campos e os 6 estados de cada ficha;
- que todo estado cita um REQ ou uma ADR;
- que todo `REQ-xx` citado existe;
- que toda operação citada existe no `openapi.yaml`;
- que todo `Entidade.campo` existe no modelo de dados ou num schema do contrato;
- que todo requisito é citado por alguma tela, ADR ou cenário;
- que toda operação HTTP é usada por alguma tela.

Além disso, o `openapi.yaml` valida com `openapi-spec-validator` e o `eventos.asyncapi.yaml` com `@asyncapi/parser`.

## Referências

- Starke, G.; Hruschka, P. *arc42 — template for architecture communication and documentation*. https://arc42.org
- Brown, S. *The C4 model for visualising software architecture*. https://c4model.com
- Nygard, M. *Documenting Architecture Decisions*, 2011; *MADR — Markdown Architectural Decision Records*. https://adr.github.io/madr/
- Mavin, A. et al. *Easy Approach to Requirements Syntax (EARS)*. IEEE RE, 2009.
- Bass, L.; Clements, P.; Kazman, R. *Software Architecture in Practice*, 4. ed. Addison-Wesley/SEI, 2021.
- OpenAPI Specification 3.1 (https://spec.openapis.org/oas/v3.1.0); AsyncAPI 3.0 (https://www.asyncapi.com); RFC 9457 (*Problem Details for HTTP APIs*).
- W3C. *Web Content Accessibility Guidelines (WCAG) 2.2*.
- CGU. Portal da Transparência — download de dados e dicionário de dados de emendas parlamentares.
