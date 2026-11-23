# Glossário (arc42 §12)

Vocabulário do sistema. Os termos de orçamento abaixo são **definições de trabalho** da equipe; o texto exibido ao cidadão vem da tabela `termo_traduzido`, sempre com fonte oficial (REQ-16).

## Domínio (orçamento público)

| Termo | Definição no Rastro | Nome no modelo |
|---|---|---|
| Emenda parlamentar | Indicação, feita por parlamentar, bancada, comissão ou relator, de parte do orçamento federal para uma finalidade e localidade | `emenda` |
| Autor da emenda | Quem indicou a emenda: parlamentar individual ou coletivo. Nunca chamado de "candidato" (REQ-27) | `autor`, `autor.tipo` |
| Emenda individual / de bancada / de comissão / de relator | Tipos de emenda segundo quem a indicou | `emenda.tipo_emenda` |
| Função | Área de governo da despesa (ex.: Saúde, Urbanismo) | `emenda.funcao` |
| Ação orçamentária | Programa específico no orçamento a que a emenda se vincula | `emenda.acao_orcamentaria` |
| Localidade do gasto | Local declarado de aplicação da despesa: município, estado, "MÚLTIPLO", "Nacional" ou "Exterior" | `emenda.localidade_gasto` |
| Empenho / valor empenhado | Reserva formal do dinheiro para a despesa; primeira fase | `valor_empenhado` |
| Liquidação / valor liquidado | Verificação, pelo governo, de que o credor tem direito a receber, o que autoriza o pagamento. Na fonte, só a do ano do empenho | `valor_liquidado` |
| Pagamento / valor pago | Saída do dinheiro do governo federal para o favorecido (prefeitura, fundo, entidade, empresa ou banco intermediário). **Não significa obra concluída.** Na fonte, `Valor Pago` registra só o que foi pago no ano do empenho | `valor_pago` |
| Restos a pagar | Valor empenhado num ano que ficou para ser pago em anos seguintes. A fonte traz o inscrito, o cancelado e o pago | `rp_inscrito`, `rp_cancelado`, `rp_pago` |
| Cancelamento de restos a pagar | Parte reservada que foi cancelada e não será paga | `rp_cancelado` |
| Transferência especial ("emenda Pix") | Emenda individual que transfere o dinheiro direto ao caixa do município ou do estado, sem finalidade definida antes; ação `0EC2` | `tipo_emenda = individual_transferencia_especial` |
| Favorecido | Quem recebeu o pagamento | `pagamento_favorecido` |
| Convênio | Acordo pelo qual a União repassa o dinheiro a quem vai executá-lo (prefeitura, entidade); traz o objeto e o convenente | `convenio` |
| Objeto do convênio | Descrição da finalidade escrita no convênio; exibida como está na fonte (REQ-72) | `convenio.objeto` |
| Convenente | Quem assinou o convênio para executar o dinheiro | `convenio.convenente` |
| Natureza jurídica | Classificação legal do favorecido (Município, Fundo Municipal, Associação Privada…) | `natureza_juridica` |

## Sistema

| Termo | Definição | Onde |
|---|---|---|
| Valor final | Empenhado menos o cancelado: o que ainda pode ser pago | `valor_final` |
| Valor pago total | Pago no ano mais pago em anos seguintes | `valor_pago_total` |
| Fase simples | Classificação derivada dos valores: `empenhada`, `liquidada`, `paga_parcial`, `paga`, `cancelada` (REQ-13) | view `emenda_ativa` |
| Termo traduzido | Linha da tabela de tradução: termo oficial, tradução curta, explicação e fonte oficial | `termo_traduzido` |
| Tradução | Texto curto, em linguagem simples, que descreve o que aconteceu **com o dinheiro** | `termo_traduzido.traducao` |
| Fonte oficial | Documento oficial que define o termo (Glossário do Portal da Transparência, Manual Técnico de Orçamento) | `fonte_titulo`, `fonte_url` |
| Abrangência | `municipal` (um município da PB), `estadual` ("PARAÍBA (UF)") ou `multiplo` ("MÚLTIPLO": várias localidades) | `emenda.abrangencia` |
| Emenda sem município único | Abrangência `estadual` ou `multiplo`; não entra no bloco "destinadas à cidade" (REQ-09) | A08 |
| Emendas destinadas à cidade | Bloco com emendas cuja localidade declarada é o município (REQ-08) | A03, A04 |
| Recebido de outras emendas | Bloco com pagamentos a prefeitura e fundos municipais vindos de emendas com outra localidade (REQ-54) | A03, A14 |
| Categoria do favorecido | `prefeitura_ou_fundo_municipal`, `estado`, `entidade_privada`, `intermediario_financeiro`, `pessoa_fisica`, `outro` | `categoria_favorecido` |
| Intermediário financeiro | Banco público que recebe para repassar (ex.: Banco do Brasil); o destino final não aparece | REQ-60 |
| ID da emenda | Identificador no Rastro: o código da fonte ou `SI-AAAA-hash` quando a fonte não traz código | `id_emenda` |
| Carga | Execução da rotina que, se a fonte mudou, baixa, filtra, valida e grava uma nova versão | `verificar_e_carregar` |
| Versão de carga | Conjunto de emendas e pagamentos gravado por uma carga | `versao_carga` |
| Versão ativa | A única versão concluída que as telas e a API leem | `versao_carga.ativa` |
| Troca atômica | Ativação da versão nova e desativação da anterior em uma única transação | `ativar_versao` |
| Verificação da fonte | Consulta diária ao arquivo do Portal: nova versão, sem mudança ou falha | `verificacao_fonte` |
| ETag | Assinatura do arquivo enviada pelo servidor; igual = arquivo não mudou | `fonte_etag` |
| Verificação atrasada | Última verificação bem-sucedida há mais de 48 h (REQ-38) | `verificacao_atrasada` |
| Fragmento | Pedaço de HTML devolvido para o HTMX substituir parte da tela | `/fragmentos/*` |
| Perfil do autor (visão B) | Tela A09, agregados por município em ordem alfabética, sem ranking; no MVP | ADR-0004 |
| Reserva antiga sem pagamento | Emenda de 2 ou mais anos atrás, não cancelada, sem nenhum pagamento; rótulo neutro "ainda sem pagamento" (REQ-76) | `reserva_antiga_sem_pagamento` |
| Primeiro pagamento | Mês do primeiro pagamento a favorecido; o tempo é dito em anos desde o ano da emenda (REQ-74) | `primeiro_pagamento` |
| Código IBGE | Identificador de 7 dígitos do município; na PB começa por `25` | `municipio.codigo_ibge` |
| Código da emenda | Identificador de 12 dígitos da fonte (ano + autor + número); pode faltar | `emenda.codigo_emenda` |

## Siglas

| Sigla | Significado |
|---|---|
| CGU | Controladoria-Geral da União (mantém o Portal da Transparência) |
| SIGA Brasil | Sistema de informações orçamentárias do Senado Federal |
| IBGE | Instituto Brasileiro de Geografia e Estatística |
| PB | Paraíba |
| LGPD | Lei Geral de Proteção de Dados (Lei 13.709/2018) |
| EARS | Easy Approach to Requirements Syntax |
| ADR / MADR | Architecture Decision Record / Markdown ADR |
| MVP | Produto mínimo viável: features 1 a 4 do FI-01 |
