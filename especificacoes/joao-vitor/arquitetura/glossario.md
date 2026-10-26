# Glossário

Vocabulário do Rastro (seção 12 do arc42). A primeira coluna é o termo usado na interface. Entre crases está o nome no modelo de dados e no contrato. A interface usa só estes termos.

## Domínio orçamentário

| Termo | No modelo | Definição |
| :-- | :-- | :-- |
| Emenda parlamentar | `Emenda` | Proposta de deputados, senadores, bancadas ou comissões para destinar parte do orçamento federal. No Rastro, uma emenda federal de 2025 identificada por um código válido. |
| Código da emenda | `Emenda.codigo` | Identificador de 12 dígitos publicado pela CGU (os 4 primeiros são o ano). Fora desse padrão, a linha é rejeitada (`codigo_invalido`). |
| Tipo de emenda | `Emenda.tipo` | Classificação da CGU: individual (transferência especial ou com finalidade definida), de bancada, de comissão ou de relator. |
| Autor | `Autor` | Quem apresentou a emenda. É **autor parlamentar** quando `Autor.tipo = parlamentar`. Bancada, comissão e relator são **autores coletivos** e nunca são atribuídos a uma pessoa. |
| Função | `Emenda.funcao_codigo`, `funcao_nome` | Área de governo da despesa (Saúde, Educação…), conforme a classificação orçamentária. |
| Localidade do gasto | `Emenda.localidade_gasto` | Onde a despesa foi programada, segundo a CGU. **Não** é o endereço do favorecido. |
| UF do gasto | `Emenda.uf_gasto` | UF derivada da localidade do gasto. Fica vazia quando a localidade é nacional ou abrange várias UFs; na API e nos filtros essas emendas aparecem com a sigla reservada `NM` ("Nacional ou múltiplas UFs") (REQ-78). |
| Município do gasto | `Emenda.municipio_gasto` | Município derivado da localidade do gasto quando ela tem a forma "MUNICÍPIO - UF". Guarda o identificador (`joao-pessoa`) e o nome como publicado (`municipio_nome`). Fica vazio quando a localidade é uma UF, uma região ou nacional; essas emendas aparecem na UF, não num município (REQ-66, REQ-88). |
| Etapa | `RegistroExecucao.etapa` | Fase da despesa com valor próprio. As etapas nunca são somadas entre si. |
| Valor empenhado | `etapa = empenhado` | Valor reservado no orçamento para a despesa (compromisso). Não significa que o dinheiro saiu. |
| Valor liquidado | `etapa = liquidado` | Valor reconhecido como devido depois de verificada a entrega do bem ou serviço. |
| Valor pago | `etapa = pago` | Valor efetivamente pago no exercício. |
| Restos a pagar | `etapa = rap_inscrito`, `rap_cancelado`, `rap_pago` | Despesas empenhadas num ano e transferidas para os anos seguintes, com valores inscritos, cancelados e pagos. |
| Valor recebido por favorecido | `RegistroFavorecido.valor_recebido_centavos` | Quanto um favorecido recebeu num mês, segundo o arquivo por favorecido da CGU. É uma grandeza distinta de "pago" e não comprova a aplicação final. |
| Favorecido | `Favorecido` | Pessoa física, pessoa jurídica ou ente público que recebeu pagamento ligado à emenda. |
| Pessoas físicas (favorecidos) | `RegistroFavorecido` com `favorecido_id` nulo | Recebimentos de pessoas físicas somados por emenda e mês, com a quantidade de pessoas e sem nome nem CPF (REQ-25, ADR-0007). |
| Aplicação final | — | Uso concreto do recurso (obra, compra, serviço). **O Rastro não tem esse dado e não afirma nada sobre ele.** |
| Estado de execução | `estado_execucao` | Etapa mais avançada com valor positivo: sem execução, empenhada, liquidada ou paga (ADR-0006). |
| Estado em linguagem simples | `estado_texto`; `TabelaTraducao.texto_simples` | Frase para o morador que traduz o estado ("A entrega foi conferida; falta pagar"). Vem da versão vigente da tabela de tradução (ADR-0008). |
| Tabela de tradução | `TabelaTraducao` | Tabela versionada, só com inserção, com um texto simples e uma explicação por estado. Cada resposta diz a versão usada (`traducao_versao`). |
| Empenhado e ainda não pago (pendente) | `pendentes=true`; `MunicipioDetalhe.quantidade_pendentes` | Emenda em que `pago` + `rap_pago` é menor que `empenhado` − `rap_cancelado`, inclusive as pagas em parte. É o recorte que o gestor municipal acompanha (REQ-68). |

## Dados e proveniência

| Termo | No modelo | Definição |
| :-- | :-- | :-- |
| Fonte | `Fonte` | Origem pública de dados: `cgu` (Portal da Transparência) ou `siga` (Siga Brasil, opcional). |
| Lote | `LoteImportacao` | Uma importação de um arquivo de uma fonte, identificada pelo hash. O mesmo arquivo não gera dois lotes, salvo quando a importação anterior falhou (REQ-05, REQ-53). Exibido como "Lote #n". |
| Hash | `LoteImportacao.hash_sha256` | Impressão digital SHA-256 do arquivo. Mesmo hash significa mesmo arquivo, e a reimportação não muda nada. |
| Data de referência | `LoteImportacao.data_referencia` | Data de atualização dos dados informada pela fonte. É a data mostrada ao usuário ("dados de 20/10/2026"). |
| Data de extração | `LoteImportacao.importado_em` | Momento em que o Rastro baixou ou recebeu o arquivo da fonte e começou a importá-lo. Aparece na proveniência ao lado da data de referência ("extraídos em 21/10") (REQ-14). |
| Lote ativo | `PublicacaoAtiva` | O lote que as consultas leem para uma fonte. Só muda numa publicação. |
| Publicação atômica | — | Troca do lote ativo numa única transação: quem consulta vê o lote antigo inteiro ou o novo inteiro, nunca uma mistura. |
| Proveniência | `Proveniencia` (contrato) | Fonte, lote, data de referência, hash e link do download oficial que acompanham cada valor. |
| Rejeição | `RejeicaoLote` | Linha descartada na validação, contada por motivo: `codigo_invalido`, `ano_fora_do_recorte`, `valor_malformado`, `linha_malformada`, `emenda_sem_cadastro`. |
| Mudança | `MudancaLote` | Diferença de uma emenda entre o lote anterior e o novo: `nova_emenda`, `valor_alterado` ou `estado_alterado`. |
| Linha do tempo | — | Sequência dos valores de cada etapa de uma emenda ao longo dos lotes publicados. |
| Sincronização | `rastro sincronizar` | Download concorrente das fontes seguido de importação e publicação em série. |

## Pessoas que usam o Rastro

| Termo | Definição |
| :-- | :-- |
| Morador (cidadão) | Quem quer saber o que foi destinado à própria cidade e em que pé está, sem vocabulário técnico. Nas fichas aparece como "Cidadão". |
| Jornalista ou pesquisador | Quem rastreia um valor da indicação ao pagamento e precisa citar a fonte de cada afirmação. |
| Pessoa de controle social | Quem acompanha um conjunto de emendas por semanas, com assinaturas e alertas. |
| Gestor municipal | Quem acompanha, pelo município, o que está empenhado e ainda não foi pago (tela P10). |
| Operador de dados | Quem roda a CLI para importar e publicar lotes e versões da tabela de tradução. |

## Assinaturas

| Termo | No modelo | Definição |
| :-- | :-- | :-- |
| Assinante | `Assinante` | Quem acompanha emendas no painel. Identificado só por uma chave, sem dado pessoal. |
| Chave de assinante | `X-Chave-Assinante`; `Assinante.chave_hash` | Segredo de 32 caracteres mostrado uma única vez. Quem perde a chave perde as assinaturas. |
| Assinatura | `Assinatura` | Um filtro (emenda, autor, UF do gasto, município do gasto e/ou função) mais uma condição, criados por um assinante. |
| Condição | `Assinatura.condicao` | `limiar_valor` (o valor da etapa cruza o limiar) ou `mudanca_estado` (o estado de execução muda). |
| Limiar | `Assinatura.limiar_centavos` | Valor em centavos que, ao ser cruzado de baixo para cima numa etapa, gera alerta. |
| Lote base | `Assinatura.lote_base_id` | Lote ativo quando a assinatura foi criada. Só mudanças de lotes publicados depois da criação geram alertas (REQ-37). |
| Alerta | `Alerta` | Aviso no painel de que uma mudança de um lote publicado satisfez uma assinatura. No máximo um por mudança e assinatura. |
| Pausar | `Assinatura.estado = pausada` | Suspende a geração de alertas sem apagar a assinatura. |

## Arquitetura e processo

| Termo | Definição |
| :-- | :-- |
| arc42 | Modelo de documentação de arquitetura usado como índice desta especificação. |
| C4 | Modelo de diagramas em níveis (contexto, contêineres, componentes, código). |
| ADR | Registro de decisão de arquitetura no formato MADR. |
| EARS | Sintaxe controlada de requisitos (ubíquo, evento, estado, indesejado, opcional). |
| PAUL | Ferramenta da disciplina que gera `PROJECT.md` e planos a partir destas especificações (`/paul:init`, `/paul:plan`). |
| Despachante de alertas | Parte da CLI (módulo `saida`) que, após cada publicação, avalia as assinaturas e grava os alertas. |
| Módulo | Uma das quatro partes do sistema definidas no brief do grupo (`ingestao`, `nucleo`, `consulta`, `saida`), cada uma com persistência, API, concorrência, desempenho medido e testes (ADR-0009). |
| Lote publicado (contrato) | O contrato principal entre os módulos: a ingestão publica o lote e os demais módulos só o leem. |
| Ranking | Ordenação de pessoas por valor. O Rastro não faz: autores aparecem em ordem alfabética (REQ-71). |
