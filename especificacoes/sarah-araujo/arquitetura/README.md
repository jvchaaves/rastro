# Arquitetura — Rastro

Autora: Sarah Fernanda Calixto de Araújo · DINF00071 · 2026.2
Base: FI-01 (Formulário de Ideação do Rastro, 24/09/2026)

> **Rastro**: aplicação web que mostra, para cada município da Paraíba, as emendas parlamentares federais destinadas a ele, com a fase de execução de cada uma traduzida para linguagem simples.

## 1. Padrão escolhido

**arc42 enxuto**: o arc42 serve de índice, e cada seção usa o padrão mais adequado.

| Peça | Padrão | Seção arc42 | Arquivo |
|---|---|---|---|
| Metas e restrições | texto | §1–2 | este README, seções 3 e 4 |
| Contexto | C4 nível 1 (Mermaid) | §3 | [`c4-contexto.md`](c4-contexto.md) |
| Contêineres | C4 nível 2 (Mermaid) | §5 | [`c4-conteineres.md`](c4-conteineres.md) |
| Decisões | ADR no formato MADR | §9 | [`adr/`](adr/) (9 ADRs) |
| Requisitos | EARS | — | [`requisitos.md`](requisitos.md) (REQ-01 a REQ-82) |
| Contratos e modelo de dados | OpenAPI 3.1 + contrato de comando + contrato da fonte externa | — | [`contratos/`](contratos/) |
| Qualidade | cenários de 6 partes (Bass, Clements, Kazman) | §10 | [`qualidade.md`](qualidade.md) |
| Glossário | texto | §12 | [`glossario.md`](glossario.md) |

As telas que consomem esta arquitetura estão em [`../telas/`](../telas/).

### Referências
- Starke, G.; Hruschka, P. *arc42 — template for documentation of software and system architecture*. https://arc42.org
- Brown, S. *The C4 model for visualising software architecture*. https://c4model.com
- Nygard, M. *Documenting Architecture Decisions* (2011); *MADR — Markdown Architectural Decision Records*. https://adr.github.io/madr/
- Mavin, A. et al. *Easy Approach to Requirements Syntax (EARS)*. IEEE RE 2009.
- Bass, L.; Clements, P.; Kazman, R. *Software Architecture in Practice*, 4. ed. Addison-Wesley, 2021 (cenários de qualidade).
- OpenAPI Initiative. *OpenAPI Specification 3.1*. https://spec.openapis.org/oas/v3.1.0

## 2. Justificativa: como o arc42 enxuto entrega as seis informações do PAUL

| O PAUL precisa de | Onde está nesta arquitetura | Por que este padrão serve |
|---|---|---|
| **Limites e vizinhos** → escopo no PROJECT.md e boundaries | §4 deste README (fora de escopo) + `c4-contexto.md` (quem está dentro e fora do sistema) + `c4-conteineres.md` | O C4 nível 1 desenha a fronteira de forma explícita: tudo que é caixa externa (Portal, SIGA, IBGE) é vizinho, não escopo. Isso vira boundary sem interpretação. |
| **Decisões e porquês** → decisão que o agente não reabre | `adr/0001` a `adr/0009` | O MADR obriga a registrar as opções descartadas. O agente lê "SPA foi considerada e descartada porque…" e não a propõe de novo. |
| **Contratos** → tasks com `files` e `verify` precisos | `contratos/openapi.yaml`, `contratos/rotas-html.md`, `contratos/carga.md`, `contratos/fonte-portal.md`, `contratos/modelo-dados.md` | O OpenAPI é verificável por máquina: o `verify` de uma task pode ser "a resposta valida contra o schema". O FastAPI gera o `/openapi.json`, e o teste compara com este arquivo. |
| **Requisitos testáveis** → ACs Given/When/Then | `requisitos.md` | Cada molde EARS mapeia direto para Given/When/Then: o QUANDO vira o When, o ENQUANTO/SE vira o Given, e o DEVE vira o Then. |
| **Qualidade com medida** → ACs do envelope | `qualidade.md` (persistência, API, concorrência, desempenho, testes) | O cenário de 6 partes força uma medida numérica por item do envelope; sem ela, o AC não é verificável. |
| **Restrições** → stack, hospedagem, LGPD | §3 deste README + ADR-0001, ADR-0005, ADR-0006 | Ficam num lugar só, citáveis pelo audit. |

O arc42 completo e as visões 4+1 foram descartados porque exigem seções (visão de implantação detalhada, visão de processos, riscos técnicos) que, num MVP de um contêiner de aplicação + banco, seriam preenchidas com texto vazio. E o agente trata texto vazio como decisão.

## 3. Metas e restrições (arc42 §1–2)

### 3.1 Metas de qualidade (em ordem de prioridade)

| # | Meta | Cenário |
|---|---|---|
| 1 | **Correção da tradução**: a fase exibida nunca afirma algo que os dados não dizem | Q5 (testes), REQ-13, REQ-15 |
| 2 | **Consistência durante a atualização**: o leitor nunca vê uma carga pela metade | Q1 (persistência), Q3 (concorrência) |
| 3 | **Leveza no celular com conexão fraca** | Q4 (desempenho) |
| 4 | **Contrato estável para quem cita e confere**: URLs e API não mudam sem aviso | Q2 (API) |

### 3.2 Partes interessadas

| Quem | Expectativa |
|---|---|
| Morador de município da PB (persona principal) | Achar a cidade e entender a fase sem saber orçamento |
| Jornalista local (persona secundária) | Citar e conferir na fonte original |
| Parlamentares autores (afetados, não usuários) | Não ter atribuído a si o que não aconteceu |
| Prefeituras (afetadas) | Não ser acusadas de desvio por leitura errada de "pago" |
| Professor (implementa) e banca | Especificação verificável e ambiente reproduzível |

### 3.3 Restrições

| Tipo | Restrição | Origem |
|---|---|---|
| Técnica | Python 3.12 · FastAPI · Jinja + HTMX + Pico.css · PostgreSQL 16 · pytest · Locust · Docker Compose | FI §6, ADR-0001 |
| Técnica | Sem JavaScript escrito à mão; páginas funcionam sem JS (REQ-41) | FI §6 |
| Dados | Só dados públicos. Fonte: zip único de emendas do Portal da Transparência (CGU), sem chave, verificado diariamente pelo ETag (ADR-0007, `contratos/fonte-portal.md`); municípios pela API do IBGE. Contingência: SIGA Brasil (fora do MVP) | FI §10.4, T1 |
| Privacidade (LGPD) | Nenhum dado pessoal de visitante; sem contas, cookies ou analytics; favorecido pessoa física nunca identificado (REQ-01, REQ-02, REQ-53, ADR-0006) | FI §5, T1 |
| Conteúdo | Sem ranking ou nota de autores; nunca a palavra "candidato"; tradução descreve o dinheiro, não a obra (REQ-15, REQ-27, REQ-28) | FI §10.2 |
| Escopo | Só emendas federais, só PB | FI §5 |
| Organizacional | 60 h de disciplina; implementação pelo professor; hospedagem a definir | FI §10.3 |

## 4. Limites (fora de escopo)

O sistema **não**: ranqueia ou pontua parlamentares; informa se a obra ou o serviço foi executado; cobre emendas estaduais/municipais ou outros estados; tem contas, login, favoritos ou notificações; segue o dinheiro dentro da prefeitura (licitação, contrato, execução física), que está em outras fontes (ADR-0009). O perfil do autor está no MVP, sem ranking (ADR-0004).

## 5. O que a T1 decidiu e o que segue aberto

A T1 do FI-01 (baixar e analisar o arquivo real) foi feita em 27/10/2026. Os achados estão em `contratos/fonte-portal.md` e as decisões que eles provocaram estão abaixo.

| Pergunta do FI-01 §12 | Resposta | Onde ficou |
|---|---|---|
| CSV ou API? Limites? | Zip único, sem chave; `GET` condicional pelo ETag | ADR-0007, REQ-31, REQ-48, REQ-49 |
| Quais anos? | Todos (2014–2026): o arquivo é cumulativo e pequeno para a PB (2 780 linhas) | ADR-0007, filtro `ano` |
| Que fração não tem município, e como exibir? | 49% das linhas (estado: 454; `MÚLTIPLO`: 917) e 86% do valor empenhado | ADR-0008, REQ-09, REQ-26, REQ-54–56, A08, A14 |
| Autores coletivos | Bancada e comissão têm código próprio; relator e 2014 vêm sem autor | REQ-21, REQ-30, REQ-57 |
| Frequência | Diária (`Last-Modified`); verificação diária com histórico | REQ-31, REQ-38, REQ-40 |
| Restos a pagar | Três campos; o pago em anos seguintes muda a fase de 63% das linhas | ADR-0003, REQ-13, REQ-19 |
| Para que era o dinheiro? (T1-b) | Objeto do convênio em 31% das emendas da PB; mostrado como texto da fonte | ADR-0009, REQ-71–73, REQ-82 |
| Quanto tempo levou? (T1-b) | A fonte não tem a data do empenho; o tempo é dito em anos desde o ano da emenda | REQ-74, REQ-75 |
| Perfil dos parlamentares (T1-b) | No MVP, sem ranking; mesma pessoa pode ter dois códigos | ADR-0004, REQ-29, REQ-80, REQ-81 |

Continua aberto, com responsável e momento:

| Item | Quando |
|---|---|
| Validação de compreensão da tabela de tradução (versão 1, com fontes oficiais, em `modelo-dados.md`) | Teste com 5 pessoas antes de publicar a feature 3 (FI §10.1) |
| Meta numérica de compreensão | Depois da 1ª rodada com 5 pessoas |
| Metas de desempenho (⟨ ⟩ em `qualidade.md`) | Depois do baseline do Q4 |
| Hospedagem, e se o servidor alcança o domínio do arquivo | Com o professor, antes da fatia de empacotamento |

## 6. Índice de arquivos

```
arquitetura/
├── README.md               ← este arquivo (padrão, justificativa, §1–2)
├── c4-contexto.md          ← C4 nível 1
├── c4-conteineres.md       ← C4 nível 2
├── adr/
│   ├── 0001-renderizar-no-servidor-com-jinja-e-htmx.md
│   ├── 0002-versionar-cargas-e-trocar-versao-ativa-em-uma-transacao.md
│   ├── 0003-derivar-fase-dos-valores-e-traduzir-com-fonte-obrigatoria.md
│   ├── 0004-entrar-pela-cidade-e-nao-ranquear-autores.md
│   ├── 0005-separar-rotina-de-carga-em-conteiner-proprio.md
│   ├── 0006-nao-coletar-dados-pessoais-de-visitantes.md
│   ├── 0007-coletar-do-arquivo-unico-com-requisicao-condicional.md
│   ├── 0008-atribuir-dinheiro-a-cidade-por-dois-caminhos-separados.md
│   └── 0009-mostrar-a-finalidade-pelo-objeto-do-convenio.md
├── requisitos.md           ← REQ-01 … REQ-82 (EARS)
├── contratos/
│   ├── openapi.yaml        ← API JSON (operações usadas pelas telas)
│   ├── rotas-html.md       ← páginas/fragmentos → operação
│   ├── carga.md            ← contrato da rotina de carga
│   ├── fonte-portal.md     ← contrato da fonte externa (formato real, T1)
│   └── modelo-dados.md     ← entidades, campos, restrições, ER
├── qualidade.md            ← Q1–Q5
└── glossario.md
```
