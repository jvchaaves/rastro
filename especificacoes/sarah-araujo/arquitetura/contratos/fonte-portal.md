# Contrato da fonte externa — Portal da Transparência (emendas parlamentares)

Contrato de **entrada** da rotina de carga. Conferido na tarefa T1 do FI-01 em 27/10/2026, com o arquivo real baixado e analisado (números da seção 5). Decisão de usar este mecanismo: ADR-0007.

## 1. Acesso

| Item | Valor observado |
|---|---|
| Página | `https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares`, botão "Baixar arquivo único" → `/download-de-dados/emendas-parlamentares/UNICO` (redireciona) |
| Arquivo (destino do redirecionamento) | `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip` |
| Autenticação | nenhuma (a API alternativa exige chave; não usada, ver ADR-0007) |
| Servidor | Amazon S3 + CloudFront |
| Cabeçalhos úteis | `ETag` (ex.: `"1b84e550bf57fad7d16f1335bb3391bc-4"`), `Last-Modified` (ex.: `Tue, 27 Oct 2026 01:44:53 GMT`), `Content-Length` (32 530 367), `Accept-Ranges: bytes` |
| Frequência | Diária. Observado: `Last-Modified` do mesmo dia, às 22:44 (horário de Recife) do dia anterior. A carga confirma a frequência registrando cada verificação (REQ-49). |
| Cobertura | Arquivo **cumulativo**: todos os anos de 2014 a 2026 num só arquivo. Não há arquivo por ano. |

## 2. Conteúdo do zip

| Arquivo | Tamanho descompactado | Linhas | Uso no Rastro |
|---|---|---|---|
| `EmendasParlamentares.csv` | 47,4 MB | 94 747 | → `emenda` |
| `EmendasParlamentares_PorFavorecido.csv` | 182,9 MB | 828 478 | → `pagamento_favorecido` |
| `EmendasParlamentares_Convenios.csv` | 26,0 MB | 85 403 | → `convenio` |

## 3. Formato (REQ-48)

- Codificação **Windows-1252** (não é UTF-8; "Código" vem como byte `0xF3`).
- Separador `;`; todos os campos entre aspas `"`; fim de linha `\r\n`; primeira linha = cabeçalho.
- Números com **vírgula decimal e sem separador de milhar** (`250000,00`). Podem ser negativos (9 linhas no país, 0 na PB).
- Ausência de valor: o texto `Sem informação` ou `S/I`, **nunca campo vazio**.

### 3.1 `EmendasParlamentares.csv` (28 colunas, nesta ordem) → modelo

| # | Coluna da fonte | Campo no Rastro | Observação da T1 |
|---|---|---|---|
| 1 | Código da Emenda | `codigo_emenda` | 12 dígitos (ano + autor + número) **ou** `Sem informação` (660 linhas da PB). Pode repetir em mais de uma linha (58 casos no país, 0 na PB) |
| 2 | Ano da Emenda | `ano` | 2014–2026 |
| 3 | Tipo de Emenda | `tipo_emenda` | 5 valores (seção 4) |
| 4 | Código do Autor da Emenda | `autor.id` | `S/I` quando o autor não é identificado |
| 5 | Nome do Autor da Emenda | `autor.nome` | `Sem informação` quando `S/I` |
| 6 | Número da emenda | `numero_emenda` | |
| 7 | Localidade de aplicação do recurso | `localidade_gasto` | `"<MUNICÍPIO> - PB"`, `"PARAÍBA (UF)"`, `"MÚLTIPLO"`, `"Nacional"`, `"Exterior"` |
| 8 | Código Município IBGE | `municipio_codigo_ibge` | 7 dígitos ou `Sem informação` |
| 9 | Município | (conferência) | |
| 10 | Código UF IBGE | (filtro) | `2500000` = PB |
| 11 | UF | (filtro) | `PARAÍBA`; nas linhas `MÚLTIPLO`, é a UF associada à emenda, não a um destino |
| 12 | Região | — | |
| 13–14 | Código/Nome Função | `funcao` | |
| 15–16 | Código/Nome Subfunção | `subfuncao` | |
| 17–18 | Código/Nome Programa | `programa` | |
| 19–20 | Código/Nome Ação | `codigo_acao`, `acao_orcamentaria` | Transferência especial ("Pix") = ação `0EC2` |
| 21–22 | Código/Nome Plano Orçamentário | `plano_orcamentario` | |
| 23 | Valor Empenhado | `valor_empenhado` | |
| 24 | Valor Liquidado | `valor_liquidado` | só do ano do empenho |
| 25 | Valor Pago | `valor_pago` | **só do ano do empenho** |
| 26 | Valor Restos A Pagar Inscritos | `rp_inscrito` | inconsistente com 23−25 em 61% das linhas da PB; **não usado em regra** |
| 27 | Valor Restos A Pagar Cancelados | `rp_cancelado` | |
| 28 | Valor Restos A Pagar Pagos | `rp_pago` | **pagamentos feitos em anos seguintes** |

### 3.2 `EmendasParlamentares_PorFavorecido.csv` (13 colunas) → `pagamento_favorecido`

| Coluna da fonte | Campo | Observação |
|---|---|---|
| Código da Emenda | `codigo_emenda` | liga com `emenda` |
| Código/Nome do Autor, Número, Tipo de Emenda | — | redundantes |
| Ano/Mês | `ano_mes` | `AAAAMM`, de 201406 a 202610 |
| Código do Favorecido | `codigo_favorecido` | CNPJ; para pessoa física vem mascarado (`***.###.###-**`) |
| Favorecido | `favorecido_nome` | |
| Natureza Jurídica | `natureza_juridica` | define `categoria_favorecido` (REQ-52) |
| Tipo Favorecido | `tipo_favorecido` | `Pessoa Jurídica`, `Pessoa Fisica` (sem acento), `Sem informação`, `Inválido` |
| UF Favorecido | `uf_favorecido` | sigla (`PB`) |
| Município Favorecido | `municipio_favorecido_nome` | **só nome, sem código IBGE** → resolvido pelo nome (REQ-52) |
| Valor Recebido | `valor_recebido` | |

### 3.3 `EmendasParlamentares_Convenios.csv` (12 colunas) → `convenio`

| Coluna da fonte | Campo | Observação (T1-b) |
|---|---|---|
| Código da Emenda | `codigo_emenda` | liga com `emenda`; uma emenda pode ter vários convênios |
| Código/Nome Função, Código/Nome Subfunção, Tipo de Emenda | — | redundantes |
| Localidade do gasto | `localidade_gasto` | `"<MUNICÍPIO> - PB"` ou `"PARAÍBA (UF)"`; pode diferir da localidade da emenda (emendas `MÚLTIPLO` têm convênios em municípios diferentes) |
| Data Publicação Convênio | `data_publicacao` | `DD/MM/AAAA` |
| Convenente | `convenente` | ex.: "FUNDACAO NAPOLEAO LAUREANO", "MUNICIPIO DE JOAO PESSOA" |
| Objeto Convênio | `objeto` | texto livre; às vezes específico ("Obras de Infraestrutura Viaria… Ciclovias e Ciclofaixas"), muitas vezes genérico ("AQUISICAO DE EQUIPAMENTO E MATERIAL PERMANENTE…") |
| Número Convênio | `numero_convenio` | |
| Valor Convênio | `valor_convenio` | parte federal |

## 4. Valores de `Tipo de Emenda` e mapeamento

| Fonte | `tipo_emenda` | `autor.tipo` | Linhas na PB |
|---|---|---|---|
| Emenda Individual - Transferências com Finalidade Definida | `individual_finalidade_definida` | `individual` | 2 280 |
| Emenda Individual - Transferências Especiais | `individual_transferencia_especial` | `individual` | 129 |
| Emenda de Relator | `relator` | `relator` | 161 (160 sem autor) |
| Emenda de Bancada | `bancada` | `bancada` (ex.: "BANCADA DA PARAIBA", código 7116) | 110 |
| Emenda de Comissão | `comissao` | `comissao` | 100 |

Linhas com autor `S/I` → `autor.tipo = 'nao_informado'`.

## 5. Números da T1 (Paraíba, arquivo de 27/10/2026)

| Medida | Valor |
|---|---|
| Linhas com `Código UF IBGE = 2500000` | 2 780 |
| com município (código IBGE 25xxxxx) | 1 409 · empenhado R$ 0,95 bi |
| `PARAÍBA (UF)` | 454 · empenhado R$ 1,12 bi |
| `MÚLTIPLO` | 917 · empenhado R$ 4,82 bi |
| Sem código de emenda | 660 (todas as de 2014; emendas de relator, comissão e bancada de 2016–2020) |
| Pagamentos (favorecido) a entidades da PB | 14 893 linhas ligadas a emendas da PB + 16 622 linhas (R$ 1,75 bi) de emendas fora do filtro de UF (ex.: `MÚLTIPLO` de outros autores) |
| `MÚLTIPLO` da PB pagos a prefeituras ou fundos municipais da PB | R$ 2,48 bi de R$ 4,49 bi recebidos; R$ 1,83 bi pagos ao Banco do Brasil (DF) |
| Soma dos favorecidos = `valor_pago + rp_pago` | 1 978 de 2 120 emendas com código (93%) |
| Nomes de município do favorecido que não batem com o IBGE | 1 (`SERIDÓ` → IBGE 2515401 "São Vicente do Seridó") |
| Empenhado = 0 | 1 linha (cancelada) |

## 5-b. Números da segunda análise (T1-b, mesmo arquivo)

| Medida | Valor |
|---|---|
| Linhas de convênio de emendas da PB | 1 445 |
| Emendas da PB (com código) que têm convênio | 663 de 2 120 (31%); 0 das 129 transferências especiais; mais comum até 2019 |
| Emendas destinadas a João Pessoa com convênio | 94 de 260 (36%) |
| Objeto mais frequente em João Pessoa | "Aquisição de equipamento e material permanente para unidade de atenção especializada em saúde" (51) |
| Ano do primeiro pagamento − ano da emenda (PB, 1 949 emendas pagas) | mesmo ano 1 182 · 1 ano 575 · 2 anos 120 · 3 ou mais 72 |
| Idem, João Pessoa (229 pagas) | 129 · 67 · 15 · 18 |
| Reservadas até 2024, sem cancelamento e sem nenhum pagamento | 59 na PB; 8 em João Pessoa |
| Maiores favorecidos das emendas destinadas a João Pessoa | Banco do Brasil (DF, intermediário) R$ 29,1 mi; Fundação Napoleão Laureano R$ 16,5 mi; Município de João Pessoa R$ 16,4 mi; Fundo Municipal de Saúde R$ 8,9 mi; Fundo Municipal de Assistência Social R$ 8,0 mi |
| Autores com emendas na PB | 45 códigos; o mesmo nome aparece com dois códigos em 3 casos (Efraim Filho, Nilda Gondim, Veneziano Vital do Rêgo) e "RELATOR GERAL" com dois códigos |
| Data do empenho | **não existe** na fonte: só o ano da emenda e o mês de cada pagamento |

## 6. Lista de municípios (IBGE)

`GET https://servicodados.ibge.gov.br/api/v1/localidades/estados/25/municipios` → 223 municípios (`id`, `nome`). É gerada uma vez e versionada no repositório como `data/municipios_pb.csv`, com a coluna `nomes_alternativos` (`SERIDÓ` para 2515401).
