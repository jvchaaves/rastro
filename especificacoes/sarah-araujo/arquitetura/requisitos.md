# Requisitos — Rastro (EARS)

Padrão: **EARS** (Easy Approach to Requirements Syntax, Mavin et al., 2009). Cada requisito tem um id estável `REQ-xx`, citado nas fichas de tela (`../telas/`), nos contratos (`contratos/`) e nos cenários de qualidade (`qualidade.md`).

Moldes: **U** ubíquo · **E** evento · **S** estado · **I** indesejado · **O** opcional.
Origem: seção do FI-01, ou **T1** quando o requisito vem da análise do arquivo real (`contratos/fonte-portal.md`).

> Convenções:
> - "Versão ativa" = a única `versao_carga` com `ativa = true` (`contratos/modelo-dados.md`).
> - "Município da PB" = registro de `municipio` (223, IBGE).
> - `valor_final = valor_empenhado − rp_cancelado`.
> - `valor_pago_total = valor_pago + rp_pago`.
> - Valores em reais com duas casas.

---

## 1. Acesso e privacidade

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-01 | U | O SISTEMA DEVE servir todas as telas e operações da API sem cadastro, login, senha ou token. | FI §3.1, §5 | todas |
| REQ-02 | U | O SISTEMA NÃO DEVE gravar cookies, identificadores de visitante nem usar análise de terceiros. Os logs de acesso DEVEM guardar o IP truncado (último octeto do IPv4 / últimos 80 bits do IPv6 zerados) e ser apagados após 30 dias. | FI §5, LGPD | todas |
| REQ-03 | U | O SISTEMA DEVE exibir no rodapé de todas as telas: "Dados do Portal da Transparência publicados em [`fonte_last_modified` da versão ativa]; verificado pela última vez em [`verificacao_fonte.verificada_em` mais recente]", com link para A10. | FI §3.1, T1 | todas com dados |

## 2. Busca e municípios

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-04 | E | QUANDO o cidadão tiver digitado ao menos 2 caracteres e parado de digitar por 300 ms, O SISTEMA DEVE sugerir até 8 municípios da PB cujo `nome_normalizado` contenha o texto normalizado (sem acentos, minúsculo). Primeiro vêm os que começam pelo texto; dentro de cada grupo, ordem alfabética. | FI §4.2 f2 | A01 |
| REQ-05 | I | SE o texto não corresponder a nenhum município da PB, ENTÃO O SISTEMA DEVE informar "Não encontramos município da Paraíba com esse nome" e oferecer link para A02. | FI §4.2 f2 | A01 |
| REQ-06 | U | O SISTEMA DEVE oferecer a lista completa dos 223 municípios da PB em ordem alfabética, agrupados pela letra inicial. | FI §2.1 | A02 |
| REQ-07 | I | SE for requisitado um `codigo_ibge` que não seja de município da PB, ENTÃO O SISTEMA DEVE responder HTTP 404 (API) ou exibir A12 (web). | FI §11.2 AC-2 | A03, A04, A14, A12 |

## 3. Município

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-08 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE exibir, para o `ano` selecionado (padrão: todos), o bloco **"Emendas destinadas à cidade"**: quantidade e somas de `valor_final` e `valor_pago_total` das emendas da versão ativa com `abrangencia = 'municipal'` e `municipio_codigo_ibge` igual ao do município. | FI §4.2 f3, T1 | A03 |
| REQ-09 | U | O SISTEMA DEVE exibir na tela do município o aviso de que emendas da Paraíba sem município único (`abrangencia` `estadual` ou `multiplo`) não entram no bloco "Emendas destinadas à cidade", com a quantidade dessas emendas e link para A08. | FI §10.2, T1 | A03, A04 |
| REQ-10 | S | ENQUANTO não houver nenhum registro para o filtro aplicado, O SISTEMA DEVE exibir "Nenhuma emenda federal registrada para [nome] [no ano X]" (ou "Nenhum pagamento…" em A14), sem sugerir causa nem responsável. | FI §4.1 | A03, A04, A08, A09, A14 |
| REQ-11 | U | O SISTEMA DEVE listar emendas ordenadas por `ano` decrescente e, no mesmo ano, por `valor_final` decrescente, em páginas de 20 itens. | FI §4.2 f3 | A04, A08 |
| REQ-12 | E | QUANDO o cidadão alterar o filtro de `funcao`, `ano` ou `fase`, ou mudar de página, O SISTEMA DEVE substituir apenas a lista (fragmento) e refletir filtro, página e `versao` nos parâmetros da URL, de modo que a URL reproduza a mesma lista. | FI §6 | A04, A08, A14 |
| REQ-63 | I | SE a URL de uma lista trouxer um `versao` que não está mais disponível, ENTÃO O SISTEMA DEVE redirecionar (HTTP 303) para a mesma URL sem `versao`, na página 1, e exibir "Os dados foram atualizados; a lista recomeçou". | T1 (paginação estável) | A04, A08, A14 |
| REQ-54 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE exibir também o bloco **"Recebido de outras emendas"**: a soma de `valor_recebido` dos `pagamento_favorecido` com `municipio_codigo_ibge` igual ao do município e `categoria_favorecido = 'prefeitura_ou_fundo_municipal'`, de emendas cuja localidade **não** é esse município, e a quantidade dessas emendas, com link para A14. | T1 | A03, A14 |
| REQ-55 | U | O SISTEMA NÃO DEVE somar num mesmo total os valores do bloco "Emendas destinadas à cidade" (REQ-08) e do bloco "Recebido de outras emendas" (REQ-54). | T1 (evita dupla contagem) | A03 |
| REQ-56 | E | QUANDO a tela de recebidos de um município for requisitada, O SISTEMA DEVE listar os pagamentos de REQ-54 agrupados por emenda (`ano_mes` mais recente primeiro) e, em seção separada e sem soma no resumo, os pagamentos a entidades de outras categorias com o mesmo `municipio_codigo_ibge`, rotulados "Entidades com endereço em [nome]". | T1 | A14 |

## 4. Fase e tradução (aposta central)

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-13 | U | O SISTEMA DEVE derivar `fase_simples` de cada emenda só pelos valores, nesta ordem: `cancelada` se `valor_final ≤ 0`; `paga` se `valor_pago_total ≥ valor_final`; `paga_parcial` se `valor_pago_total > 0`; `liquidada` se `valor_liquidado > 0`; senão `empenhada`. | FI §4.4, T1 | A04, A05, A08, A09 |
| REQ-14 | U | O SISTEMA DEVE exibir a fase de cada emenda pelo texto `termo_traduzido.traducao` correspondente, nunca apenas por cor, ícone ou sigla. | FI §4.4, WCAG 1.4.1 | A04, A05, A08, A09 |
| REQ-15 | U | O SISTEMA DEVE exibir em `traducao` e `explicacao` de todo `termo_traduzido` apenas textos que descrevam o que aconteceu com o dinheiro, sem nenhuma das expressões da lista proibida: `obra`, `entrega`, `entregue`, `concluíd`, `pront`, `executad`, `inaugur`, `serviço prestado`, `desvio`. O teste ignora maiúsculas e acentos e casa por prefixo. | FI §10.2 | A05, A06, A07 |
| REQ-16 | I | SE um `termo_traduzido` não tiver `fonte_titulo` e `fonte_url` preenchidos, ENTÃO O SISTEMA DEVE recusar sua gravação (`NOT NULL` + `CHECK`) e, portanto, nunca exibi-lo. | FI §10.1 | A06, A07 |
| REQ-17 | E | QUANDO o cidadão acionar "O que isso quer dizer?" ao lado de uma fase ou valor, O SISTEMA DEVE mostrar `termo_oficial`, `traducao`, `explicacao`, `fonte_titulo` e `fonte_url` (A06) sem perder a posição na tela de origem, e o mesmo conteúdo DEVE estar disponível em URL própria. | FI §4.2 f4 | A05, A06 |
| REQ-18 | U | O SISTEMA DEVE exibir no detalhe da emenda o aviso fixo: "Pago quer dizer que o dinheiro saiu do governo federal para quem aparece em 'Para quem foi pago'. Não quer dizer que a obra ou o serviço foi feito." | FI §3.2, T1 | A05, A13 |
| REQ-19 | O | ONDE a emenda tiver `rp_pago > 0`, O SISTEMA DEVE exibir que parte do pagamento foi feita em anos seguintes ao da emenda, com o valor de `rp_pago` e link para o termo `restos-a-pagar`. ONDE tiver `rp_cancelado > 0`, O SISTEMA DEVE exibir o valor cancelado com link para o termo `cancelamento`. | FI §9, T1 | A04, A05 |
| REQ-20 | U | O SISTEMA DEVE oferecer o glossário com todos os `termo_traduzido`, em ordem alfabética de `termo_oficial`. | FI §4.4 | A07 |

## 5. Detalhe, pagamentos e citação

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-21 | E | QUANDO o detalhe de uma emenda for requisitado, O SISTEMA DEVE exibir `codigo_emenda` (ou "Código não informado na fonte"), `ano`, `autor.nome` (ou "Autor não informado na fonte"), `autor.tipo`, `tipo_emenda`, `funcao`, `subfuncao`, `acao_orcamentaria`, `localidade_gasto`, `valor_empenhado`, `rp_cancelado`, `valor_final`, `valor_liquidado`, `valor_pago`, `rp_pago`, `valor_pago_total` e a `fase_simples` traduzida. | FI §4.2 f4, T1 | A05 |
| REQ-22 | I | SE o `id_emenda` requisitado não existir na versão ativa, ENTÃO O SISTEMA DEVE responder HTTP 404 (API) ou exibir A12 com "Essa emenda não está na versão atual dos dados". | — | A05, A12, A13 |
| REQ-23 | U | O SISTEMA DEVE exibir no detalhe da emenda com `codigo_emenda` o link para a consulta dessa emenda no Portal da Transparência. Sem `codigo_emenda`, DEVE exibir o link para a página de download da fonte. | FI §3.1 | A05, A13 |
| REQ-24 | E | QUANDO o cidadão pedir para citar uma emenda, O SISTEMA DEVE gerar um texto de citação com `codigo_emenda` (ou "sem código na fonte"), `autor.nome`, `ano`, `valor_final`, `valor_pago_total`, a data `fonte_last_modified` da versão ativa, a URL permanente da emenda no Rastro e a URL da fonte. | FI §3.1 | A13 |
| REQ-25 | U | O SISTEMA DEVE usar URLs permanentes de município, emenda e termo, formadas apenas por `codigo_ibge`, `id_emenda` e `slug`, respectivamente. | FI §3.1 | A03, A05, A06, A13 |
| REQ-57 | I | SE uma linha da fonte vier com `Código da Emenda = 'Sem informação'`, ENTÃO a carga DEVE gerar `id_emenda = 'SI-' + ano + '-' + 8 primeiros hexadecimais do SHA-256 de (ano, tipo, localidade, código da função, código da ação, código do plano orçamentário)` e gravar `codigo_emenda` nulo. | T1 | A05, A13 |
| REQ-58 | I | SE o mesmo `codigo_emenda` aparecer em mais de uma linha gravada, ENTÃO a carga DEVE usar `id_emenda = codigo_emenda + '-' + n` (n = 1, 2… pela ordem de `codigo_acao`, `localidade_gasto`) e contar o caso em `total_codigos_repetidos`. Nos demais casos, `id_emenda = codigo_emenda`. | T1 | A05 |
| REQ-59 | E | QUANDO o detalhe de uma emenda for requisitado, O SISTEMA DEVE listar em "Para quem foi pago" os `pagamento_favorecido` da emenda, agrupados por favorecido, com `favorecido_nome` (ou "Pessoa física"), `categoria_favorecido`, município e UF, soma de `valor_recebido` e o período (`ano_mes` mínimo e máximo). | T1 | A05 |
| REQ-60 | O | ONDE o favorecido for intermediário financeiro (`categoria_favorecido = 'intermediario_financeiro'`), O SISTEMA DEVE exibir: "Pago a banco público que repassa o dinheiro. O destino final não aparece nestes dados." | T1 | A05, A08, A14 |
| REQ-61 | O | ONDE a emenda for de transferência especial (`tipo_emenda = 'individual_transferencia_especial'`), O SISTEMA DEVE exibir: "Transferência especial: o dinheiro vai direto para o caixa da prefeitura ou do estado, sem finalidade definida antes. Depois do pagamento, o uso não aparece nos dados federais." | T1 | A04, A05 |

## 6. Emendas sem município único e autor

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-26 | E | QUANDO a lista de emendas sem município único for requisitada, O SISTEMA DEVE listar as emendas da versão ativa com `abrangencia` `estadual` ou `multiplo`, com os mesmos campos, ordem e paginação de REQ-11. Cada item DEVE mostrar quantos municípios da PB aparecem entre os seus favorecidos. | FI §10.2, T1 | A08 |
| REQ-27 | U | O SISTEMA DEVE usar "autor da emenda" ou "parlamentar" e NÃO DEVE usar a palavra "candidato" em nenhum texto de interface. | FI §10.2 | todas |
| REQ-28 | U | O SISTEMA NÃO DEVE exibir nota, pontuação ou ranking, nem ordenar ou comparar autores entre si por qualquer valor. | FI §5 | A05, A09 |
| REQ-29 | E | QUANDO o perfil de um autor for requisitado, O SISTEMA DEVE exibir `nome`, `tipo`, o período (primeiro e último `ano`) e, das emendas gravadas, as somas de `valor_final` e `valor_pago_total` por município (municípios em ordem alfabética) e um bloco "Sem município único". | FI §4.2 f5, T1 (a fonte não traz UF de eleição); no MVP desde 27/10/2026 (ADR-0004) | A09 |
| REQ-30 | I | SE o autor for `S/I` (não informado na fonte), ENTÃO O SISTEMA DEVE exibir o nome do autor sem link e responder HTTP 404 em `/autores/S/I`. | FI §4.3, T1 | A05, A09 |

## 7. Carga e versão dos dados (ator: rotina de carga)

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-31 | E | QUANDO o horário agendado chegar (diariamente às 04:00, America/Recife), a rotina DEVE fazer `GET` condicional (`If-None-Match` com o `fonte_etag` da versão ativa) na URL do arquivo definida em `contratos/fonte-portal.md` §1 e gravar o resultado em `verificacao_fonte`. | FI §4.2 f1, T1 | A10 |
| REQ-49 | E | QUANDO a fonte responder `304` ou o `ETag` recebido for igual ao da versão ativa, a rotina DEVE registrar `verificacao_fonte.resultado = 'sem_mudanca'` e NÃO DEVE criar `versao_carga`. | T1 | A10 |
| REQ-48 | I | SE o zip não contiver `EmendasParlamentares.csv`, `EmendasParlamentares_PorFavorecido.csv` e `EmendasParlamentares_Convenios.csv`, ou o cabeçalho de qualquer um deles diferir, em nomes ou ordem, do definido em `contratos/fonte-portal.md` §3, ou alguma linha não tiver o número de colunas do cabeçalho, ou algum valor monetário não seguir `^-?\d+,\d{2}$`, ENTÃO a carga DEVE falhar com `motivo = 'formato_inesperado'`, informando o arquivo e a linha. | T1 | A10 |
| REQ-32 | U | O SISTEMA DEVE, na rotina de carga, gravar em `emenda` só as linhas com `Código UF IBGE = 2500000`, com `abrangencia`: `municipal` quando o código IBGE do município começar por `25`, `estadual` quando a localidade for `PARAÍBA (UF)` e `multiplo` quando for `MÚLTIPLO`. As demais linhas são apenas contadas em `total_descartados`. | FI §11.2 AC-1, T1 | A10 |
| REQ-52 | U | O SISTEMA DEVE, na rotina de carga, gravar em `pagamento_favorecido` as linhas de favorecido cuja emenda foi gravada **ou** cuja `UF Favorecido = 'PB'`. Para cada uma, O SISTEMA DEVE resolver `municipio_codigo_ibge` pelo nome normalizado + `nomes_alternativos` (só quando a UF for PB) e `categoria_favorecido` pela tabela de `contratos/modelo-dados.md`. | T1 | A05, A08, A14 |
| REQ-82 | U | O SISTEMA DEVE, na rotina de carga, gravar em `convenio` as linhas de `EmendasParlamentares_Convenios.csv` cuja emenda foi gravada, ligadas por `codigo_emenda`, resolvendo `municipio_codigo_ibge` pela localidade (`"<MUNICÍPIO> - PB"`) quando houver. | T1-b | A05 |
| REQ-53 | I | SE o `Tipo Favorecido` for pessoa física, ENTÃO O SISTEMA NÃO DEVE gravar `codigo_favorecido` nem `favorecido_nome` e DEVE gravar `categoria_favorecido = 'pessoa_fisica'`. | LGPD, T1 | A05, A14 |
| REQ-62 | I | SE o nome de município de um favorecido da PB não for resolvido, ENTÃO a rotina DEVE gravar `municipio_codigo_ibge` nulo e contar o caso em `total_municipios_nao_resolvidos`. A carga DEVE falhar se esse total for maior que 0,5% dos pagamentos da PB. | T1 | A10 |
| REQ-50 | I | SE a quantidade de emendas gravadas for menor que 90% da quantidade da versão ativa, ENTÃO a rotina NÃO DEVE ativar a nova versão e DEVE marcá-la `falhou` com `motivo = 'queda_de_volume'`. | T1 | A10 |
| REQ-33 | E | QUANDO a gravação e as verificações de REQ-48, REQ-50 e REQ-62 terminarem sem erro, O SISTEMA DEVE, numa única transação, marcar a versão nova como `concluida` e ativa e desativar a anterior. | FI §9.1 | A10 |
| REQ-34 | S | ENQUANTO uma carga estiver em andamento, toda leitura (telas e API) DEVE retornar exclusivamente dados da versão ativa. | FI §7.1 | todas com dados |
| REQ-35 | I | SE a carga falhar em qualquer etapa, ENTÃO O SISTEMA DEVE marcar a versão como `falhou`, gravar `motivo` e `mensagem_erro`, manter a versão ativa anterior e não exibir nenhum dado da versão que falhou. | FI §9.1 | A10 |
| REQ-36 | I | SE uma execução da carga for disparada enquanto outra estiver em andamento, ENTÃO O SISTEMA DEVE recusar a segunda sem criar `versao_carga` e registrar a recusa no log. | FI §7.1 | A10 |
| REQ-37 | E | QUANDO uma nova versão for ativada, O SISTEMA DEVE apagar, depois de 24 h, os dados das versões anteriores à imediatamente anterior. Ficam a ativa e uma anterior, que continua servindo as URLs com `versao` fixada (REQ-12). | FI §9.1, T1 | A10 |
| REQ-38 | S | ENQUANTO a verificação bem-sucedida mais recente (`resultado` `nova_versao` ou `sem_mudanca`) tiver mais de 48 h, O SISTEMA DEVE exibir no rodapé e em A10: "Não conseguimos verificar a fonte desde [data]. Os dados podem estar desatualizados." | T1 | todas com dados, A10 |
| REQ-39 | I | SE não houver nenhuma versão ativa, ENTÃO as telas de dados DEVEM exibir "Os dados ainda não foram carregados" e a API DEVE responder HTTP 503. | — | todas com dados |
| REQ-40 | U | O SISTEMA DEVE exibir em A10 a fonte, a versão ativa (`fonte_last_modified`, totais) e as 10 últimas verificações, com `verificada_em`, `resultado` e, quando houver versão, os totais. | FI §3.1 | A10 |
| REQ-51 | O | ONDE a variável `ALERTA_WEBHOOK_URL` estiver configurada, QUANDO duas verificações seguidas terminarem em `falhou`, a rotina DEVE enviar um `POST` JSON com `versao_carga_id`, `motivo` e `mensagem_erro` para essa URL. Sem a variável, DEVE registrar o alerta no log com nível `ERROR`. | T1 | — |

## 8. Interface, API e robustez

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-41 | U | O SISTEMA DEVE manter toda tela funcionando com o JavaScript desligado: busca, filtros e paginação DEVEM ter equivalente em formulário `GET` e link. O HTMX é apenas melhoria progressiva. | FI §6 | todas |
| REQ-42 | I | SE uma requisição de fragmento falhar por falta de conexão ou exceder 10 s, ENTÃO a tela DEVE manter o conteúdo já exibido e mostrar "Sem conexão. Tente de novo." com um botão que repete a requisição. | FI §3.1 | A01, A03, A04, A05, A08, A09, A14 |
| REQ-43 | U | O SISTEMA DEVE publicar o contrato da API em `/openapi.json` e responder apenas JSON válido contra esse schema. | FI §6, AC-2 | — |
| REQ-44 | U | O SISTEMA DEVE exibir valores monetários no formato pt-BR completo (`R$ 1.234.567,89`). Quando houver forma abreviada (`R$ 1,2 mi`), a forma completa DEVE estar disponível ao leitor de tela. | WCAG | todas com valores |
| REQ-45 | U | O SISTEMA DEVE atender WCAG 2.2 nível AA em todas as telas. | Trabalho 1 §2.1 | todas |
| REQ-46 | I | SE ocorrer erro interno, ENTÃO O SISTEMA DEVE responder HTTP 500 com A12 (web) ou corpo `Erro` (API) contendo um código de referência, sem detalhes técnicos. | — | A12 |
| REQ-47 | U | O SISTEMA DEVE exibir A11 com o que o Rastro mostra, o que não mostra (FI §5), os limites dos dados (pagamentos a intermediários, emendas sem código, pessoas físicas não identificadas) e a ausência de julgamento sobre autores. | FI §4.1, §5, T1 | A11 |

## 9. Resposta direta, área, linha do tempo, compartilhamento e busca por código

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-64 | E | QUANDO o detalhe de uma emenda for requisitado, O SISTEMA DEVE exibir no topo, antes de qualquer outro dado, uma frase-resposta (`resposta`) montada pela primeira regra que se aplicar: **(a)** `fase_simples = 'cancelada'`: "A reserva desta emenda foi cancelada. Nenhum valor foi pago." (ou "…foi cancelada depois de pagar R$ X." se `valor_pago_total > 0`); **(b)** `valor_pago_total = 0`: "R$ {valor_final} estão reservados para esta emenda, mas nada foi pago até {mês de `fonte_last_modified`}."; **(c)** com favorecidos: "R$ {valor_pago_total} desta emenda já foram pagos a {favorecido de maior valor}{' e mais N' se houver outros}, {em {mês} \| entre {mês inicial} e {mês final}}." e, se `paga_parcial`, "Faltam R$ {valor_final − valor_pago_total}."; **(d)** sem favorecidos: "R$ {valor_pago_total} desta emenda já foram pagos. A fonte não informa a quem." | FI §10.1 (métrica de compreensão) | A05, A13 |
| REQ-70 | O | ONDE o favorecido de maior valor da frase de REQ-64 for `intermediario_financeiro`, a frase DEVE nomeá-lo como "{nome}, banco que repassa o dinheiro" e terminar com "O destino final não aparece nos dados." Pessoa física aparece como "uma pessoa física" (REQ-53). | T1 | A05 |
| REQ-65 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE abrir a tela com a manchete "Desde {ano mínimo}, {n} emendas tiveram {nome} como destino: R$ {valor_final} reservados, R$ {valor_pago_total} já pagos." (com `ano` filtrado: "Em {ano}, …"), calculada sobre o bloco de REQ-08. | FI §2.1 | A03 |
| REQ-66 | U | O SISTEMA DEVE oferecer, como primeiro filtro das listas de emendas, a `funcao` (rótulo "Área"), com as áreas presentes no conjunto filtrado, a quantidade de emendas de cada uma e ordem decrescente de quantidade. | FI §3.1 | A04, A08 |
| REQ-67 | E | QUANDO o detalhe de uma emenda for requisitado, O SISTEMA DEVE exibir a linha do tempo (`linha_do_tempo`): primeiro o marco "{ano}: emenda indicada e R$ {valor_empenhado} reservados"; depois um marco por `ano_mes` com pagamentos a favorecidos ("{mês/ano}: R$ {soma} pagos a {favorecidos}"); se `rp_cancelado > 0`, o marco "R$ {rp_cancelado} cancelados (a fonte não informa quando)"; e, se `valor_final − valor_pago_total > 0`, o marco final "Falta pagar R$ {diferença}" ("Aguardando pagamento" quando nada foi pago). A linha do tempo NÃO DEVE inventar datas que a fonte não traz. | T1 | A05 |
| REQ-68 | E | QUANDO o cidadão acionar "Compartilhar" no detalhe de uma emenda, O SISTEMA DEVE oferecer, sem JavaScript, o link `https://wa.me/?text=` com a frase de REQ-64 e a URL permanente (codificados) e a opção "Copiar link". As páginas de emenda DEVEM ter `og:title` = "Emenda {código} · {destino}" e `og:description` = frase de REQ-64. A URL compartilhada NÃO DEVE conter parâmetros de rastreamento (REQ-02). | FI §2.4 (o anúncio chega por rede social) | A05 |
| REQ-69 | E | QUANDO o texto de busca tiver exatamente 12 dígitos, O SISTEMA DEVE procurar `codigo_emenda` na versão ativa em vez de municípios: com uma emenda encontrada, sugeri-la (ano, autor, destino) e, ao buscar, redirecionar (303) para A05; com mais de uma (REQ-58), listá-las; sem nenhuma, exibir "Não encontramos essa emenda entre as destinadas à Paraíba", com link para a consulta do Portal. | FI §3.1 (jornalista) | A01 |

## 10. Finalidade, tempo, reservas antigas, áreas, favorecidos e autores

| ID | Molde | Requisito | Origem | Telas |
|---|---|---|---|---|
| REQ-71 | E | QUANDO o detalhe de uma emenda for requisitado e houver `convenio` ligado a ela, O SISTEMA DEVE exibir a seção "Para que era o dinheiro", com, para cada convênio: `objeto` (rotulado "Descrição informada no convênio"), `convenente`, `numero_convenio`, `data_publicacao`, `valor_convenio` e `localidade_gasto`. | T1-b (convênios) | A05 |
| REQ-72 | U | O SISTEMA DEVE exibir o `objeto` do convênio com o texto da fonte, mudando apenas maiúsculas e minúsculas, sem resumir, reescrever nem completar. | ADR-0009 | A05 |
| REQ-73 | I | SE a emenda não tiver convênio, ENTÃO a seção de REQ-71 DEVE dizer "A fonte não registra convênio para esta emenda, por isso não há uma descrição da finalidade além da área e da ação do orçamento." | T1-b (69% sem convênio) | A05 |
| REQ-74 | E | QUANDO a emenda tiver pagamentos a favorecidos, O SISTEMA DEVE exibir o primeiro pagamento como "Primeiro pagamento em {mês/ano}, {no mesmo ano da emenda \| N ano(s) depois do ano da emenda}", com N = ano do menor `ano_mes` − `ano`. O SISTEMA NÃO DEVE expressar esse tempo em meses nem em dias, porque a fonte não traz a data do empenho. | T1-b | A05, A13 |
| REQ-75 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE exibir "Quando o dinheiro chegou": a quantidade de emendas destinadas com primeiro pagamento no mesmo ano, 1 ano depois, 2 anos depois, 3 anos ou mais depois, e ainda sem pagamento (não canceladas); emendas pagas sem data de pagamento na fonte são contadas à parte como "sem data na fonte". | T1-b | A03 |
| REQ-76 | S | ENQUANTO uma emenda tiver `ano ≤ ano atual − 2`, fase diferente de `cancelada` e `valor_pago_total = 0`, O SISTEMA DEVE exibir junto dela o rótulo "Reservada em {ano}, ainda sem pagamento"; o resumo do município DEVE mostrar quantas emendas destinadas estão nessa situação, com link para A04 filtrado (`sem_pagamento_antigo=true`). | T1-b | A03, A04, A05, A09 |
| REQ-77 | U | O SISTEMA NÃO DEVE, em nenhum texto de interface, qualificar emendas, pagamentos ou autores com as palavras `parada`, `atrasada`, `abandonada`, `esquecida`, `travada` ou `desvio`. | FI §4.1, §10.2 | todas |
| REQ-78 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE exibir "Para quais áreas": barras horizontais com o `valor_final` das emendas destinadas por `funcao` (as 5 maiores mais "Outras áreas"), cada uma com valor e quantidade em texto e com link para A04 filtrado pela área. As barras DEVEM ser HTML e CSS gerados no servidor, com a mesma informação em lista acessível. | FI §3.1 | A03 |
| REQ-79 | E | QUANDO o resumo de um município for requisitado, O SISTEMA DEVE exibir "Quem mais recebeu": os 5 favorecidos com maior soma de `valor_recebido` nos pagamentos das emendas destinadas à cidade, cada um com `categoria_favorecido` em texto; pessoas físicas aparecem somadas como "Pessoas físicas" (REQ-53) e intermediários com o aviso de REQ-60. | T1-b | A03 |
| REQ-80 | U | O SISTEMA DEVE oferecer a lista de autores com emendas gravadas, em ordem alfabética de `nome`, mostrando apenas `nome`, `tipo` e o período (primeiro e último `ano`), sem valores nem quantidades. | ADR-0004 (revisto) | A15 |
| REQ-81 | O | ONDE houver outros autores com o mesmo nome normalizado, o perfil DEVE exibir "Este nome também aparece como autor com outro código ({período})", com link para cada um; O SISTEMA NÃO DEVE juntar os perfis automaticamente. | T1-b (ex.: dois códigos para Efraim Filho) | A09, A15 |

---

## Rastreabilidade inversa (requisito → contrato)

| Requisitos | Contrato principal |
|---|---|
| REQ-04, 05, 06 | `listar_municipios` (`GET /api/v1/municipios`) |
| REQ-69 | `buscar_emendas_por_codigo` (`GET /api/v1/emendas?codigo=`) |
| REQ-07, 08, 09, 10, 54, 55, 65, 66 | `obter_municipio` (`GET /api/v1/municipios/{codigo_ibge}`) |
| REQ-11, 12, 13, 14, 19, 61, 63, 66 | `listar_emendas_municipio` (`GET /api/v1/municipios/{codigo_ibge}/emendas`) |
| REQ-75, 76, 78, 79 | `obter_municipio` (campos `quando_chegou`, `reservas_antigas_sem_pagamento`, `areas`, `principais_favorecidos`) |
| REQ-71 a 74, 76 | `obter_emenda` (campos `convenios`, `primeiro_pagamento`, `reserva_antiga_sem_pagamento`) |
| REQ-80, 81 | `listar_autores`, `obter_autor` |
| REQ-56, 60 | `listar_recebidos_municipio` (`GET /api/v1/municipios/{codigo_ibge}/recebidos`) |
| REQ-18, 21, 22, 23, 25, 57, 58, 59, 60, 61, 64, 67, 68, 70 | `obter_emenda` (`GET /api/v1/emendas/{id_emenda}`) |
| REQ-24 | `obter_citacao_emenda` |
| REQ-15, 16, 17, 20 | `listar_termos`, `obter_termo` |
| REQ-26 | `listar_emendas_sem_municipio` |
| REQ-28, 29, 30 | `obter_autor` |
| REQ-03, 38, 39, 40 | `obter_versao_ativa`, `listar_verificacoes` |
| REQ-31 a 37, 48 a 53, 62, 82 | `verificar_e_carregar`, `ativar_versao` (`contratos/carga.md`), `contratos/fonte-portal.md` |
| REQ-43 | `/openapi.json` |
