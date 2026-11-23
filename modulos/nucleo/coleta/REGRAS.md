# Regras da coleta e da normalização

Gerado por `coletor.py` a cada execução. As contagens são as da última execução. O item citado em cada regra é conferido pelo coletor (`conferir_exemplos`), que para se a linha citada deixar de mostrar o caso. "Guarda" é a regra para um caso que o formato permite e os lotes atuais não trazem no recorte.

Lotes: `2026-10-26` (bruto/2026-10-26_EmendasParlamentares.csv.gz), `2026-11-19` (bruto/2026-11-19_EmendasParlamentares.csv.gz). Uma referência `AAAA-MM-DD:N` é a linha N do CSV descomprimido desse lote (a linha 1 é o cabeçalho).

| Regra | Passo | O que faz | Item do bruto que a motivou | Itens afetados |
| :-- | :-- | :-- | :-- | --: |
| R01 | extrair | Ler o CSV como Latin-1, separador `;`, campos entre aspas, com o módulo `csv`; o número da linha física do CSV descomprimido vira a proveniência | 2026-11-19:92156 (202612460001) | 189695 linhas lidas |
| R02 | extrair | Tirar espaços das pontas do nome da coluna | cabeçalho do lote 2026-11-19, coluna 7: `"Possui Apoiador/Solicitante? "` | 1 nomes de coluna corrigidos |
| R03 | extrair | Coluna que o coletor não conhece é ignorada e contada aqui, sem parar a execução | guarda: entre 26/10 e 19/11 a CGU acrescentou a coluna 7 (`Possui Apoiador/Solicitante?`), hoje mapeada | 0 colunas ignoradas |
| R04 | extrair | Linha com número de campos diferente do cabeçalho é descartada (`linha_malformada`) | guarda: nenhuma linha assim nos dois lotes | 0 linhas descartadas |
| R05 | normalizar | Descartar linha com ano fora de 2025 e 2026 (`ano_fora_do_recorte`). É a primeira regra de descarte, para as seguintes dizerem respeito só ao recorte | 2026-10-26:2 (ano 2014) | 165366 linhas descartadas |
| R06 | normalizar | Descartar linha com `Código da Emenda` = "Sem informação" (`codigo_ausente`): sem código não há como parear lotes | 2026-10-26:2 traz o código "Sem informação"; nos dois lotes todas as linhas assim são de 2014 a 2020 e já saem pela R05 | 0 linhas descartadas |
| R07 | normalizar | Descartar linha cujo código não tem 12 dígitos (`codigo_invalido`) | guarda: o código documentado tem 12 dígitos (ano + autor + sequência); nenhuma linha fora disso nos dois lotes | 0 linhas descartadas |
| R08 | normalizar | Descartar a segunda ocorrência de um código no mesmo lote (`codigo_duplicado_no_lote`) | 2026-11-19:48631 e 48632 repetem o código 202030410010 (2020, já fora pela R05); são 58 códigos repetidos, todos de 2020, 2023 e 2024 | 0 linhas descartadas |
| R09 | normalizar | Em campo de texto, trocar quebra de linha e espaços repetidos por um espaço e tirar espaços das pontas | guarda do esqueleto do tutorial: nenhum campo do recorte precisou | 0 campos alterados |
| R10 | normalizar | Converter valor `250000,00` (vírgula decimal, sem milhar, sem `R$`) em centavos inteiros; fora desse formato, descartar (`valor_malformado`, o nome do Trabalho 1) | 2026-11-19:92156, `Valor Liquidado` = `11044500,00` | 145974 valores convertidos |
| R11 | normalizar | Trocar UF por extenso pela sigla (`PARAÍBA` → `PB`); UF fora das 27 e dos dois valores das R12 e R13 é descartada (`uf_desconhecida`) | 2026-11-19:94749 (202612770004), UF = `PARAÍBA` | 21447 linhas com sigla |
| R12 | normalizar | `UF` = "Sem informação" (`Código UF IBGE` = `-1`) vira nulo: emenda nacional, de uma região ou no exterior; `localidade_gasto` e `regiao` dizem qual | 2026-11-19:82700 (202542920009), localidade "Nacional" | 2630 linhas com UF nula |
| R13 | normalizar | `UF` = "Múltiplo" (`Código UF IBGE` = `-14`) vira nulo: emenda em mais de uma UF. O modelo do Trabalho 1 só previa "Sem informação" | 2026-10-26:82849 (202536300010), que a primeira execução descartou como `uf_desconhecida` | 252 linhas com UF múltipla |
| R14 | normalizar | `Código Município IBGE` = "Sem informação" vira nulo | 2026-11-19:94749 (202612770004), localidade MÚLTIPLO | 21362 linhas com código de município nulo |
| R15 | normalizar | `Município` = "Múltiplo" ou "Sem informação" vira nulo; o texto original continua em `localidade_gasto` e na comparação (R19) | 2026-11-19:94749 (202612770004), Município = `Múltiplo` | 21362 linhas com nome de município nulo |
| R16 | normalizar | "Múltiplo" em `Região`, `Nome Subfunção` e `Nome Ação` fica como está: ali é um valor do domínio, não um identificador que o módulo usa para filtrar | 2026-11-19:82930 (202527960009), Região = `Múltiplo` | 233 campos mantidos |
| R17 | normalizar | `Possui Apoiador/Solicitante?`: "Sim" → `true`, "Não" → `false`, "Não se aplica" → nulo; lote sem a coluna → nulo, para todo registro ter o campo | cabeçalho do lote 2026-11-19, coluna 7; o lote 2026-10-26 não tem a coluna; "Não" aparece em 2026-11-19:19764 (2016) | 24329 registros |
| R18 | comparar | Parear os lotes pelo código da emenda, nunca pela posição: a mesma emenda muda de linha entre lotes | 202612460001: linha 92065 em 2026-10-26 e 92156 em 2026-11-19 | 12059 emendas pareadas |
| R19 | comparar | Comparar campos de texto pelo valor original da CGU, não pelo normalizado: "Sem informação" → "Múltiplo" é uma mudança, embora os dois virem nulo | 202612770004: Município "Sem informação" em 2026-10-26:94554 e "Múltiplo" em 2026-11-19:94749 | 12 alterações que o valor normalizado esconderia |
| R20 | comparar | Não comparar campo que só existe em um dos lotes (`possui_apoiador`) | cabeçalho do lote 2026-11-19, coluna 7 | 12059 emendas pareadas com o campo fora da comparação |
| R21 | comparar | Descartar emenda presente nos dois lotes sem nenhum campo diferente (`sem_mudanca`) | 202638970001: linha 88995 nos dois lotes, com todos os campos iguais | 9079 emendas descartadas |
| R22 | comparar | Emenda só no lote novo vira item `nova` | 202613390002 (2026-11-19:90420) | 206 itens |
| R23 | comparar | Emenda só no lote anterior vira item `removida`, com a proveniência do lote anterior | 202614110020 (2026-10-26:93641) | 5 itens |
| R24 | comparar | Emenda nos dois lotes com campo diferente vira item `alterada`, com cada campo antes e depois (normalizado e, em texto, também o original) e, em valor, a diferença em centavos | 202612460001 (Liquidado e Pago) | 2980 itens |
| R25 | comparar | Derivar `estado_antes` e `estado_depois` pela regra do REQ-105 do Trabalho 1 (`sem_execucao` … `paga`), sem interpretar o motivo | 202612460001: `paga_em_parte` → `paga` | 3191 itens com estado |
| R26 | comparar | Listar as `MudancaLote` do modelo do Trabalho 1 que a mudança gera: `nova_emenda`, `valor_alterado` (uma por etapa) e `estado_alterado`. Emenda removida e troca de local não têm tipo no modelo do Trabalho 1 | 202612460001: `valor_alterado` liquidado e pago, mais `estado_alterado` | 6682 linhas de MudancaLote |
| R27 | deduplicar | Chave = SHA-256 de `codigo\|lote_anterior\|lote_novo`; chave repetida não entra duas vezes | guarda: `comparar` já gera um item por código e par de lotes | 0 chaves repetidas descartadas |

## Resultado

- Itens no corpus: 3191 (alterada 2980, nova 206, removida 5).
- Descartes em `descartes.jsonl`: `ano_fora_do_recorte` 165366, `sem_mudanca` 9079.
- Linhas lidas (189695) = registros do recorte + descartes de linha. O coletor confere a soma e para se não bater.
