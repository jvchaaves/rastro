# Fonte e recorte — Trabalho 2, João Vitor (módulo `nucleo`)

**Fonte:** Portal da Transparência (CGU), download de dados "Emendas parlamentares", arquivo `EmendasParlamentares.csv` do pacote único.
**Recorte:** dois lotes da mesma fonte, em datas diferentes, com proveniência por registro. O item do corpus é a **mudança de uma emenda de 2025 ou 2026 entre um lote e o seguinte** (nova, removida ou alterada). A Etapa 2 descreve em uma frase o que mudou e classifica o tipo de mudança.

| Campo | Valor |
| :-- | :-- |
| URL | https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO, que redireciona para `https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/emendas-parlamentares/EmendasParlamentares.zip` |
| Dicionário de dados | Link "dicionário de dados" na página https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares |
| Lote 1 | Data de referência 26/10/2026 (data do arquivo dentro do ZIP), baixado em 27/10/2026. ZIP com 3 arquivos, SHA-256 `cee4e775…aebc` |
| Lote 2 | Data de referência 19/11/2026, baixado em 23/11/2026. `Last-Modified: Thu, 19 Nov 2026 22:36:28 GMT`. ZIP com 6 arquivos, SHA-256 `221c0a3e…6faf0` |
| Itens | 94 747 linhas no lote 1 e 94 948 no lote 2; 12 064 e 12 265 delas são de 2025 ou 2026. O corpus tem 3 191 mudanças |
| Licença | A página de download não traz licença própria (conferido em 23/11/2026). Vale a Política de Dados Abertos do Poder Executivo federal (Decreto 8.777/2016): os dados "são de livre utilização pelos Poderes Públicos e pela sociedade" (art. 4º, redação do Decreto 9.903/2019), com permissão irrestrita de reuso (art. 3º, IV), e a única condição é creditar a fonte (art. 2º, III). Toda linha do corpus traz a fonte |
| Acesso | Público, sem login, sem credencial, sem aceitar termo |
| Limite de requisição | A CGU não documenta limite. O coletor faz no máximo uma requisição por execução, e só com `--baixar`; ela é condicional (`If-None-Match` com o ETag do último lote), e a CGU responde 304 sem corpo quando o lote não mudou. A execução padrão não acessa a rede |
| Dado pessoal | Nenhum dado de pessoa física beneficiária. O único nome de pessoa no arquivo de emendas é o do parlamentar autor, publicado pela própria CGU como parte do dado da emenda e ligado ao exercício do mandato; não há CPF, endereço nem contato. O arquivo por favorecido, que tem pessoas físicas, não é usado |

## Por que este recorte é o do módulo `nucleo`

O brief do grupo dá ao `nucleo` o cálculo da "diferença entre lotes e o estado de execução consolidado de cada emenda". O corpus é exatamente essa diferença, com o estado de execução antes e depois (regra do REQ-105 do Trabalho 1). Ele não se sobrepõe ao recorte da Sarah (emendas destinadas à PB com valor e fase, um retrato de um lote) nem ao do João Rafael (pagamentos a favorecidos): aqui o item é a mudança entre dois retratos.

## Por que 2025 e 2026, e não só 2025

O recorte do Rastro no FI-01 é o ano de 2025. Entre os dois lotes, as 6 310 emendas de 2025 só mudaram em restos a pagar (462 mudanças, todas nas três colunas de restos a pagar), porque o exercício de 2025 está fechado. As de 2026 têm as mudanças que o módulo precisa reconhecer: empenho, liquidação, pagamento, anulação, troca de local de aplicação, emenda nova e emenda que some do arquivo. Com só 2025, o corpus teria praticamente um tipo de mudança: restos a pagar que foram pagos ou cancelados.

## Proveniência do lote 1: o que dá e o que não dá para provar

O lote de 26/10/2026 foi baixado em 27/10/2026, para conferir o Trabalho 1, antes de existir este coletor. Por isso, no manifesto, ele não tem a URL final nem os cabeçalhos HTTP: só o SHA-256 do ZIP e do CSV. A CGU publica apenas o lote vigente, e não há como baixá-lo de novo. O ZIP original não está no repositório, por tamanho; o aluno guarda os dois ZIPs, e o SHA-256 do manifesto permite conferir qualquer cópia. O lote 2 foi baixado pelo próprio coletor (`--baixar`), com URL final, `Last-Modified` e `ETag` registrados.

## Registro de datas

- **Escolha da fonte:** o cronograma pedia esta linha no repositório até 19/11/2026. Ela entrou em 23/11/2026, com atraso, junto com a Etapa 1.
- **Recorte de anos:** o Trabalho 1 fixa `ano = 2025` no MVP; este corpus inclui 2026 pela razão acima. A mudança precisa ser comunicada ao professor, conforme pede a seção 2 do enunciado para troca de recorte.
