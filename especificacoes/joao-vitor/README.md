# Trabalho 1 — Telas e arquitetura · João Vitor Chaves

Especificação individual do sistema completo **Rastro**, feita a partir do FI-01 (Formulário de Ideação do Rastro, 24/09/2026) e alinhada ao brief do repositório do grupo (`README.md` de `ddea-ufpb/rastro`): consulta por município, estado traduzido para linguagem simples por tabela versionada, nenhum ranking de parlamentares, os três papéis do brief (morador, jornalista ou controle social, gestor municipal) e os quatro módulos (`ingestao`, `nucleo`, `consulta`, `saida`). As telas estão em [`telas/`](telas/) e a arquitetura em [`arquitetura/`](arquitetura/).

| Parte | Comece por | Conteúdo |
| :-- | :-- | :-- |
| (a) Interface | [telas/diretrizes.md](telas/diretrizes.md) → [telas/inventario.md](telas/inventario.md) | 19 telas (P01–P11, D01, S01–S05, O01–O02), 5 atores, 3 superfícies, mapa de navegação e 10 fluxos |
| (b) Arquitetura | [arquitetura/README.md](arquitetura/README.md) | arc42 enxuto: C4 1 e 2, mapa dos 4 módulos do grupo, 10 ADRs, 112 REQ em EARS (com módulo e telas), OpenAPI 3.1 (20 operações) + AsyncAPI 3.0 + CLI + modelo de dados, 5 cenários de qualidade, glossário |
| Rastreabilidade | [arquitetura/rastreabilidade.md](arquitetura/rastreabilidade.md) | Tela ↔ requisito ↔ contrato, gerada por [`verificar.py`](verificar.py) |

Mockups de referência (anexo opcional): [`telas/anexos/`](telas/anexos/), exportados do canvas "Rastro — telas" no Claude Design, com um arquivo por id de tela.

## Checklist do enunciado

**Parte (a), seção 2:**

- [x] `diretrizes.md`: público, plataforma e orientação, tom, 5 princípios verificáveis (3 a 5), referência visual, pt-BR e WCAG 2.2 AA.
- [x] `inventario.md`: 19 telas (≥ 10) com id, nome, ator e superfície; mapa de navegação; cobertura de atores, superfícies, funcionalidades do FI-01 e exigências do brief.
- [x] Uma ficha por tela, com os 11 campos do template (nomes exatos), objetivo em uma frase e os 6 estados.

**Diretivas da seção 2.4:**

| # | Diretiva | Como foi atendida | Conferida por |
| :-: | :-- | :-- | :-- |
| 1 | Id estável citado na ficha, no inventário e nos requisitos | Título de cada ficha, quadro do inventário e coluna "Telas" de `requisitos.md` | `verificar.py` (gera e confere a coluna) |
| 2 | Uma intenção por tela | Campo "Objetivo" em uma frase | `verificar.py` (objetivo com uma frase) |
| 3 | Todos os estados | Os 6 estados em todas as fichas, mais estados próprios (sem lote, fonte indisponível, já importado) | `verificar.py` |
| 4 | Campos com nomes do modelo de dados | `Entidade.campo` e `Schema.campo` em Mostra e Coleta; campos só de interface marcados como "campo local" | `verificar.py` (todo `Entidade.campo` existe no modelo ou no OpenAPI) |
| 5 | Toda ação aponta um contrato; todo estado aponta um requisito | Cada ação termina em (`operação`), → Pxx (`operação`), `cli:` ou "ação local · sem chamada à API (REQ-74)"; cada estado cita REQ ou ADR | `verificar.py` (ação, navegação e estado) |
| 6 | Diretrizes escritas uma vez | `diretrizes.md` traz estados comuns, cabeçalho e convenção de ações; as fichas só registram o que é próprio | revisão |
| 7 | Intenção, não pixel | Fichas descrevem dados e comportamento; layout fino é do shadcn/ui (`diretrizes.md`, "Layout fino") | revisão |
| 8 | Mock como anexo | Campo "Anexo" aponta `anexos/<ID>.png`, exportado do canvas | `verificar.py` (o arquivo existe) |

**Parte (b), seção 3.3:**

- [x] `README.md`: padrão, referência e justificativa pelas 6 informações da seção 3.1.
- [x] `c4-contexto.md` e `c4-conteineres.md`.
- [x] `adr/`: 10 ADRs (≥ 3) no formato MADR.
- [x] `requisitos.md`: REQ-01…REQ-112 em EARS, usando os cinco moldes, todos com o sujeito "O SISTEMA", uma obrigação, verificação, módulo e telas.
- [x] `contratos/`: `openapi.yaml` (20 operações, todas usadas por telas), `eventos.asyncapi.yaml`, `cli.md`, `modelo-de-dados.md`.
- [x] `qualidade.md`: 5 cenários de 6 partes (persistência, API, concorrência, desempenho medido, testes).
- [x] `glossario.md`.

## Como conferir

```bash
pip install pyyaml openapi-spec-validator
python3 especificacoes/joao-vitor/verificar.py
```

Saída esperada: `OK · 19 telas · 119 ações com contrato · 112 requisitos · 20 operações HTTP · 5 comandos CLI · 10 ADRs · matriz gerada`.
