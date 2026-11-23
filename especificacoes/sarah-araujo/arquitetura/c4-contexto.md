# C4 · Nível 1 — Contexto do sistema (arc42 §3)

```mermaid
C4Context
    title Rastro — contexto

    Person(morador, "Morador de município da PB", "Cidadão sem formação em orçamento; celular, conexão fraca, uso eventual")
    Person(jornalista, "Jornalista local", "Cidadão que cita e confere os dados; celular ou computador, uso recorrente")

    System(rastro, "Rastro", "Mostra as emendas federais por município da PB, com a fase traduzida para linguagem simples")

    System_Ext(portal, "Portal da Transparência (CGU)", "Zip único de emendas, favorecidos e convênios, atualizado diariamente")
    System_Ext(siga, "SIGA Brasil (Senado)", "Fonte de contingência — não integrada no MVP")
    System_Ext(ibge, "IBGE (API de localidades)", "Lista oficial dos 223 municípios da PB (semente única)")
    System_Ext(defs, "Glossário do Portal / Manual Técnico de Orçamento", "Definições oficiais citadas por cada termo traduzido")

    Rel(morador, rastro, "Busca a cidade e lê as emendas", "HTTPS / HTML")
    Rel(jornalista, rastro, "Lê, cita e consulta a API", "HTTPS / HTML, JSON")
    Rel(rastro, portal, "GET condicional diário do zip", "HTTPS, If-None-Match")
    Rel(rastro, ibge, "Importa municípios da PB", "arquivo, uma vez")
    Rel(jornalista, portal, "Confere a emenda na fonte", "link a partir de A05/A13")
    Rel(morador, defs, "Abre a fonte oficial de um termo", "link a partir de A06")
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Atores e vizinhos

| Elemento | Tipo | Relação com o Rastro | Telas |
|---|---|---|---|
| Morador | pessoa (cidadão) | usuário principal; sem autenticação | A01–A12, A14, A15 |
| Jornalista | pessoa (cidadão) | mesmas telas + citação, perfis de autores e API | A01–A15, API |
| Rotina de carga | ator não humano **interno** (ver nível 2) | escreve os dados; resultado visível em A10 | A10 |
| Portal da Transparência | sistema externo | fonte dos dados (`contratos/fonte-portal.md`); se cair ou mudar o formato, a carga falha e a versão anterior continua no ar (REQ-35, REQ-48) | — |
| SIGA Brasil | sistema externo | contingência documentada; fora do MVP | — |
| IBGE | sistema externo | lista de municípios, importada uma vez | — |
| Fontes de definição oficial | documentos externos | só são linkados; o Rastro não os copia | A06, A07 |

## Afetados que não são usuários (FI §3.2)
Parlamentares autores e prefeituras não interagem com o sistema, mas suas consequências viram restrição: REQ-15, REQ-18, REQ-27 e REQ-28.

## Fronteira
Dentro: coleta, armazenamento versionado, tradução da fase, telas, API de leitura.
Fora: qualquer escrita por usuários, autenticação, outras UFs, emendas estaduais/municipais, execução física de obras.
