# Arquitetura do Rastro — índice

Especificação arquitetural do sistema completo **Rastro: para onde vão as emendas parlamentares**, feita a partir do FI-01 (24/09/2026) e alinhada ao brief do repositório do grupo (`ddea-ufpb/rastro`, README): consulta por município, estado traduzido por tabela versionada, nenhum ranking de parlamentares e os quatro módulos `ingestao`, `nucleo`, `consulta` e `saida`. É a entrada do PAUL (`/paul:init`, `/paul:plan`) e o contrato das telas em `../telas/`.

## Padrão escolhido: arc42 enxuto

O padrão é o **arc42** (Starke e Hruschka) como índice. Cada seção usa a notação mais adequada:

| Seção arc42 | Conteúdo | Notação | Arquivo |
| :-- | :-- | :-- | :-- |
| §1 Introdução e metas | Metas, partes interessadas | texto | este README |
| §2 Restrições | Stack, execução, dados, prazo | texto | este README |
| §3 Contexto | Atores, sistemas externos, limites | C4 nível 1 (Mermaid) | [c4-contexto.md](c4-contexto.md) |
| §5 Blocos de construção | Contêineres e os quatro módulos do grupo | C4 nível 2 (Mermaid) + mapa de módulos | [c4-conteineres.md](c4-conteineres.md) e [abaixo](#mapa-para-os-quatro-módulos-do-grupo) |
| §9 Decisões | 9 decisões com o porquê | ADR (MADR) | [adr/](adr/) |
| §10 Qualidade | 5 cenários, um por item do envelope | Bass, Clements e Kazman (6 partes) | [qualidade.md](qualidade.md) |
| §12 Glossário | Vocabulário do domínio e do sistema | texto | [glossario.md](glossario.md) |
| — Requisitos | 98 requisitos testáveis, cada um com módulo e telas | EARS | [requisitos.md](requisitos.md) |
| — Contratos | API HTTP, eventos internos, CLI e modelo de dados | OpenAPI 3.1, AsyncAPI 3.0, Markdown, Mermaid ER | [contratos/](contratos/) |
| — Rastreabilidade | Tela ↔ requisito ↔ contrato | matriz gerada por script | [rastreabilidade.md](rastreabilidade.md) |

As seções §4 (estratégia de solução), §6 (visão de execução), §7 (implantação) e §8 (conceitos transversais) não têm arquivo próprio, porque o conteúdo delas já está em outros documentos:

- a estratégia está nas ADR-0001 a 0004 e na ADR-0009 (módulos);
- a execução está em `contratos/cli.md` e `contratos/eventos.asyncapi.yaml`;
- a implantação está no fim de `c4-conteineres.md`;
- os conceitos transversais (proveniência, etapas distintas, estados de interface) estão em `requisitos.md` (grupos B e D) e em `../telas/diretrizes.md`.

### Por que este padrão: as seis informações que o PAUL consome

| O PAUL precisa de | Onde está nesta especificação | Como vira entrada do PAUL |
| :-- | :-- | :-- |
| **Limites e vizinhos** | `c4-contexto.md` (atores, CGU, Siga, agendador; seção "Limites"), `c4-conteineres.md` (quem escreve no banco) e o mapa de módulos abaixo (o que cada módulo possui e consome) | Escopo do `PROJECT.md` e *boundaries* de cada plano. Exemplo: "a API não escreve dados de fonte", "nenhum canal externo de alerta" |
| **Decisões e porquês** | `adr/0001`–`0009`, com opções descartadas e consequências | Decisões que o agente não reabre a cada sessão (lote imutável, SQLite WAL, chave anônima…) |
| **Contratos** | `contratos/openapi.yaml` (20 operações, cada uma com o módulo dono em `x-modulo`), `contratos/eventos.asyncapi.yaml`, `contratos/cli.md`, `contratos/modelo-de-dados.md` | Tasks com `files` e `verify` precisos. Exemplo: "`obter_emenda` responde 422/404/503 conforme o contrato" |
| **Requisitos testáveis** | `requisitos.md`: 98 REQ em EARS, cada um com o teste que o verifica, a origem (FI-01 ou brief), o módulo e as telas | Critérios de aceite Given/When/Then, um por molde: U → *Then* válido em qualquer cenário; E (QUANDO) → *When*; S (ENQUANTO) → *Given* um estado; I (SE … ENTÃO) → *Given* a condição indesejada + *When* a operação; O (ONDE) → *Given* a característica habilitada. A resposta (O SISTEMA DEVE …) é sempre o *Then*. A tabela final liga AC-1…AC-4 do FI-01 aos REQ |
| **Qualidade com medida** | `qualidade.md`: QA-01 persistência, QA-02 API, QA-03 concorrência, QA-04 desempenho medido, QA-05 testes | ACs do envelope com número e ferramenta de medida (0 mistura de lotes em 100 execuções, p95 < 100 ms, cobertura ≥ 80%) |
| **Restrições** | §2 abaixo, ADR-0002 (execução local), ADR-0005 e ADR-0007 (dados pessoais) | Stack, hospedagem e LGPD que o *audit* cobra |

**Alternativas consideradas:**

- **arc42 completo** duplicaria seções vazias num MVP de 60 horas.
- **4+1 / ISO 42010** exigiria visões (por exemplo, a física) com pouco conteúdo aqui.
- **Spec Kit / Kiro** cobrem bem requisitos e tarefas, mas não têm lugar natural para C4 nem para cenários de qualidade.

O arc42 enxuto dá um índice reconhecível e deixa cada peça na notação que o próprio enunciado pede (C4, MADR, EARS, OpenAPI, cenários de 6 partes).

## §1 Metas

**Missão:** permitir que o morador saiba o que foi destinado à cidade dele e em que pé está, em linguagem simples, e que jornalistas, controle social e gestores municipais acompanhem o caminho dos recursos de emendas parlamentares federais. O caminho vai da indicação ao pagamento, sem confundir valor empenhado, liquidado, pago e recebido por favorecido, e sempre com a fonte, o lote e a data de extração de cada dado.

| Meta de qualidade (prioridade) | Por quê | Onde é medida |
| :-- | :-- | :-- |
| 1. **Confiabilidade da atribuição** (proveniência em todo valor, tradução auditável, nenhum ranking) | O risco do Rastro é de atribuição, não de privacidade (brief; FI-01 §3.2) | REQ-14, REQ-15, REQ-69, REQ-70, REQ-71, ADR-0008, princípio 1 das diretrizes, QA-02 |
| 2. **Consistência sob atualização** (nenhuma mistura de lotes, alertas sem duplicata) | Gancho de concorrência do brief | REQ-09, REQ-36, QA-01, QA-03 |
| 3. **Desempenho medido** (consulta e ETL) | Gancho de desempenho do brief | REQ-49, REQ-50, QA-04 |
| 4. **Acessibilidade** (WCAG 2.2 AA) | Público cidadão, inclusive no celular | REQ-43, `../telas/diretrizes.md` |

| Parte interessada | Expectativa |
| :-- | :-- |
| Cidadão (morador) | Saber o que foi destinado à cidade dele e em que pé está, sem vocabulário técnico |
| Gestor municipal | Acompanhar o que está empenhado e ainda não foi pago no município |
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
| Nenhum julgamento de irregularidade e nenhuma afirmação sobre aplicação final | FI-01 §5; brief (fora de escopo) |
| Nenhuma classificação, pontuação ou ranking de parlamentares | Brief (dados e privacidade), REQ-71 |
| Quatro módulos independentes (`ingestao`, `nucleo`, `consulta`, `saida`), cada um com persistência, API, concorrência, desempenho medido e testes | Brief (módulos), ADR-0009 |
| Disciplina de 60 horas; conta Claude Pro; modelo local parcial a partir da semana 8 | FI-01 §10.3 |
| LGPD: só o que a fonte publica; favorecido pessoa física agregado, sem nome nem CPF; nenhum dado pessoal de usuários | ADR-0005, ADR-0007; brief (dado agregado, sem titular identificado) |

## Lacunas do FI-01 fechadas por esta especificação

| Lacuna do FI-01 | Decisão |
| :-- | :-- |
| Identidade do assinante | Chave anônima de 128 bits ([ADR-0005](adr/0005-identificar-assinantes-por-chave-anonima.md)) |
| Definição de mudança de status | Fechada provisoriamente: estado derivado da etapa mais avançada ([ADR-0006](adr/0006-derivar-estado-de-execucao-da-etapa-mais-avancada.md), status *proposta* até conferir dois lotes reais) |
| Exibição de favorecidos pessoa física | Agregados por emenda e mês, sem nome nem CPF ([ADR-0007](adr/0007-agregar-favorecidos-pessoa-fisica-sem-identificar.md)) |
| Limites de uso da API (FI-01 §3.1, "limites a definir") | 60 req/min por IP de cliente, com o IP do navegador repassado pelo painel (REQ-28, REQ-84, REQ-85) |
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
| [0007](adr/0007-agregar-favorecidos-pessoa-fisica-sem-identificar.md) | Favorecidos pessoa física agregados por emenda e mês, sem identificação | aceita |
| [0008](adr/0008-traduzir-estado-por-tabela-versionada.md) | Estado traduzido por tabela versionada no banco, nunca por regra no código | aceita |
| [0009](adr/0009-dividir-em-quatro-modulos-com-o-lote-publicado-como-contrato.md) | Quatro módulos do grupo, com o lote publicado como contrato central | aceita |

## Mapa para os quatro módulos do grupo

O brief do grupo divide o Rastro em quatro módulos, e o contrato principal é **o lote publicado**: a ingestão publica; núcleo, consulta e saída leem, sem saber como o CSV da origem é lido (ADR-0009). A tabela abaixo diz o que cada módulo recebe desta especificação. A coluna "Módulo" de [requisitos.md](requisitos.md) e o campo `x-modulo` de cada operação em [contratos/openapi.yaml](contratos/openapi.yaml) seguem este mapa.

| Módulo | O que faz (brief) | Contêineres | Requisitos | Contratos | Telas |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `ingestao` | Baixa, valida e normaliza os lotes; guarda proveniência; publica de forma atômica | CLI de dados, Arquivos brutos, Banco | REQ-01–07, 10–13, 21, 27, 50, 52–54, 56, 57, 59, 66, 73, 78, 82, 88, 90, 95, 97, 98 | `cli:importar`, `cli:publicar`, `cli:sincronizar`, `cli:lotes`; `listar_lotes`, `obter_lote`; evento `lote.publicado` | O01, O02, P09 (lotes) |
| `nucleo` | Diferença entre lotes e estado de execução consolidado | CLI (dentro da publicação), API, Banco | REQ-08, 24, 61, 69, 70, 75, 86, 93 | porta `calcular_mudancas`; `listar_mudancas`, `listar_traducoes`; `cli:traducao`; view `v_emenda_estado` | P08, P11 |
| `consulta` | API e busca por município, parlamentar e função; agregações; contrato versionado | API, Painel | REQ-09, 14–18, 20, 22, 23, 25, 26, 28–30, 49, 65, 67, 68, 71, 72, 76, 77, 79, 84, 85, 91, 92 | `obter_status`, `listar_opcoes_filtro`, `listar_emendas`, `obter_emenda`, `obter_linha_do_tempo`, `listar_favorecidos`, `obter_agregacoes`, `obter_autor`, `obter_municipio`, `obter_contrato` | P01–P07, P10, D01 |
| `saida` | Assinaturas por filtro e limiar; alerta com entrega única por assinante | API, CLI (despachante), Painel | REQ-31–42, 58, 62–64, 80, 81, 87, 94, 96 | `criar_assinatura`, `listar_assinaturas`, `atualizar_assinatura`, `excluir_assinatura`, `listar_alertas`, `atualizar_alerta`; consome `lote.publicado`, emite `alertas.gerados` | S01–S05 |
| todos | Requisitos transversais do painel e da engenharia | — | REQ-19, 43–48, 51, 55, 60, 74, 83, 89 | — | todas as telas do painel |

### Envelope de cada módulo (persistência, API, concorrência, desempenho, testes)

O brief exige os cinco itens em cada módulo, sozinho. Os cenários de [qualidade.md](qualidade.md) medem o sistema; esta tabela diz qual parte de cada medida cabe a cada módulo.

| Módulo | Persistência (tabelas que só ele escreve) | API | Componente concorrente | Desempenho medido | Testes |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `ingestao` | `Fonte`, `LoteImportacao`, `RejeicaoLote`, `PublicacaoAtiva`, `Autor`, `Emenda`, `RegistroExecucao`, `Favorecido`, `RegistroFavorecido` | CLI (`contratos/cli.md`) + `listar_lotes`, `obter_lote` | Downloads em paralelo com publicação serial e trava de escritor único (REQ-11, REQ-56; QA-03) | ETL ≤ 10 min, por etapa em `duracao_etl_ms` (REQ-50, REQ-82; QA-04) | `test_cgu.py`, `test_store.py`, `test_sincronizar.py`, `test_cli.py`; QA-01 |
| `nucleo` | `MudancaLote`, `TabelaTraducao` | porta `calcular_mudancas`, `listar_mudancas`, `listar_traducoes`, `cli:traducao` | Cálculo das mudanças dentro da transação `BEGIN IMMEDIATE`, com leitores em snapshot durante a troca (REQ-08, REQ-09; QA-03) | Cálculo das mudanças da base 2025 completa ≤ 5 s, em `duracao_etl_ms.publicacao` (REQ-93; QA-03) | `test_mudancas.py`, `test_traducao.py` |
| `consulta` | `CacheConsulta` (respostas de agregação por lote, REQ-91); lê as tabelas do lote sem escrevê-las | 10 operações HTTP de leitura, com cache por lote | Leituras simultâneas em WAL durante a publicação; limite de taxa por IP de cliente (REQ-09, REQ-28; QA-03) | `obter_emenda` p95 < 100 ms, `obter_agregacoes` p95 < 300 ms (REQ-49; QA-04); p95 < 150 ms durante publicação (REQ-92; QA-03) | `test_api.py`, `test_contrato.py`, e2e das telas P/D; QA-02 |
| `saida` | `Assinante`, `Assinatura`, `Alerta` | 6 operações HTTP com `X-Chave-Assinante` + evento `alertas.gerados` | Despachante com `ThreadPoolExecutor` e `INSERT … ON CONFLICT DO NOTHING` (REQ-35, REQ-36; QA-03) | Fan-out de 500 assinaturas × 300 mudanças ≤ 2 s, em `alertas.gerados.duracao_ms` (REQ-94; QA-03) | `test_assinaturas.py`, `test_alertas.py`, e2e das telas S |

## Como verificar a coerência

```bash
pip install pyyaml
python3 especificacoes/joao-vitor/verificar.py
```

O script confere e regenera a matriz [`rastreabilidade.md`](rastreabilidade.md). O que ele confere:

- os 11 campos (com os nomes exatos do template) e os 6 estados de cada ficha;
- que todo estado cita um REQ ou uma ADR;
- que todo `REQ-xx` citado existe;
- que toda operação citada existe no `openapi.yaml`;
- que todo `Entidade.campo` existe no modelo de dados ou num schema do contrato;
- que todo requisito é citado por alguma tela, ADR ou cenário;
- que toda operação HTTP é usada por alguma tela;
- que toda ação de cada ficha aponta uma operação do contrato, um comando `cli:`, um evento ou a marca "ação local" (diretiva 5);
- que a coluna "Telas" de `requisitos.md` é igual às citações das fichas (diretiva 1). `python3 verificar.py --escrever` regenera a coluna.

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
