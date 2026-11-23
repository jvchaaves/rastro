# Regras da coleta e da normalização

Gerado por `coletor.py` a cada execução: as contagens são as da última execução, e o exemplo de cada regra é conferido pelo coletor (ele para se a linha citada não mostrar mais o caso).

Lotes: `2026-10-26` (bruto/2026-10-26_EmendasParlamentares.csv.gz), `2026-11-19` (bruto/2026-11-19_EmendasParlamentares.csv.gz).

| Regra | Passo | O que faz | Item do bruto que a motivou | Itens afetados |
| :-- | :-- | :-- | :-- | --: |
| R01 | extrair | Ler o CSV como Latin-1, separador `;`, todos os campos entre aspas, com o módulo `csv`; o número da linha física vira a proveniência | qualquer linha; ex. 2026-11-19:92156 | 189695 linhas lidas |
| R02 | extrair | Tirar espaços das pontas do nome da coluna | cabeçalho do lote 2026-11-19: `"Possui Apoiador/Solicitante? "` (espaço no fim) | 1 cabeçalhos com espaço |
| R03 | normalizar | Descartar linha com ano fora de 2025 e 2026 (`ano_fora_do_recorte`). É a primeira regra de descarte, para as seguintes dizerem respeito só ao recorte | 2026-10-26:2 (ano 2014) | 165366 linhas descartadas |
| R04 | normalizar | Descartar linha com `Código da Emenda` = "Sem informação" (`codigo_ausente`): sem código não há como parear lotes | 2026-10-26:2 traz o código "Sem informação"; nos lotes de 26/10 e 19/11 todas as linhas assim são de 2014 a 2020 e já saem pela R03 | 0 linhas descartadas |
| R05 | normalizar | Descartar linha cujo código não tem 12 dígitos (`codigo_invalido`) | nenhuma linha no recorte; regra de guarda do formato documentado | 0 linhas descartadas |
| R06 | normalizar | Descartar a segunda ocorrência de um código no mesmo lote (`codigo_duplicado_no_lote`) | nenhuma linha no recorte; regra de guarda da chave | 0 linhas descartadas |
| R07 | normalizar | Converter valor `250000,00` (vírgula decimal, sem milhar, sem `R$`) em centavos inteiros | 2026-11-19:92156, `Valor Liquidado` = `11044500,00` | 145974 valores convertidos |
| R08 | normalizar | Trocar UF por extenso pela sigla (`PARAÍBA` → `PB`); UF fora da lista das 27 vira descarte `uf_desconhecida` | 2026-11-19:94749, UF = `PARAÍBA` | 21447 linhas com UF |
| R09 | normalizar | `UF` = "Sem informação" e `Código UF IBGE` = `-1` viram nulo: emenda nacional, de uma região ou no exterior; `localidade_gasto` e `regiao` guardam qual | 2026-11-19:82700 (202542920009, localidade "Nacional") | 2630 linhas com UF nula |
| R10 | normalizar | `UF` = "Múltiplo" e `Código UF IBGE` = `-14` viram nulo: emenda em mais de uma UF (o modelo do Trabalho 1 só previa "Sem informação") | 2026-10-26:82849 (202536300010), descartada por `uf_desconhecida` na primeira execução | 252 linhas com UF múltipla |
| R11 | normalizar | `Código Município IBGE` = "Sem informação" vira nulo | 2026-11-19:94749 (MÚLTIPLO, PB) | 21362 linhas com município nulo |
| R12 | normalizar | `Município` = "Múltiplo" ou "Sem informação" vira nulo; a localidade original fica em `localidade_gasto` | 2026-11-19:94749, Município = `Múltiplo` | 21362 linhas com nome de município nulo |
| R13 | normalizar | `Possui Apoiador/Solicitante?`: "Sim" → `true`, "Não se aplica" → nulo; a coluna só existe a partir do lote 2026-11-19 | cabeçalho do lote 2026-11-19 (coluna 7) | 12265 linhas com a coluna |
| R14 | comparar | Parear os lotes pelo código da emenda, nunca pela posição: a mesma emenda muda de linha entre lotes | 202612460001: linha 92065 em 2026-10-26 e 92156 em 2026-11-19 | 12059 emendas pareadas |
| R15 | comparar | Não comparar campo que só existe em um dos lotes (`possui_apoiador`); ele fica no registro do lote novo | cabeçalho do lote 2026-11-19 (coluna 7) | 12059 emendas com o campo ignorado na comparação |
| R16 | comparar | Descartar emenda presente nos dois lotes sem nenhum campo diferente (`sem_mudanca`) | 202638970001: linha 88995 nos dois lotes, com todos os campos iguais | 9079 emendas descartadas |
| R17 | comparar | Emenda só no lote novo vira item `nova` | 202613390002 (2026-11-19:90420) | 206 itens |
| R18 | comparar | Emenda só no lote anterior vira item `removida`, com a proveniência do lote anterior | 202614110020 (2026-10-26:93641) | 5 itens |
| R19 | comparar | Emenda nos dois lotes com campo diferente vira item `alterada`, com a lista de campos (antes, depois e, para valor, a diferença em centavos) | 202612460001 (Liquidado e Pago) | 2980 itens |
| R20 | comparar | Derivar `estado_antes` e `estado_depois` pela regra do REQ-105 do Trabalho 1 (`sem_execucao` … `paga`), sem interpretar o motivo | 202612460001 | 3191 itens com estado |
| R21 | deduplicar | Chave = SHA-256 de `codigo\|lote_anterior\|lote_novo`; uma chave repetida não entra duas vezes | todas as linhas do corpus | 0 chaves repetidas descartadas |

## Resultado

- Itens no corpus: 3191 (alterada 2980, nova 206, removida 5).
- Descartes em `descartes.jsonl`: `ano_fora_do_recorte` 165366, `sem_mudanca` 9079.
- A soma das linhas lidas é igual à soma de registros pareáveis e descartes de linha (o coletor confere isso e para se não bater).
