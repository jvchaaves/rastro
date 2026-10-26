# Requisitos — EARS

Requisitos do Rastro (REQ-01 a REQ-65) escritos nos cinco moldes EARS (Mavin et al., 2009). Cada um tem um id estável (`REQ-xx`), que é citado nas fichas de tela, nos contratos e nos cenários de qualidade.

- **Molde**: U = ubíquo · E = evento · S = estado · I = indesejado · O = opcional.
- **Origem**: de onde vem o requisito. FI-01 = Formulário de Ideação. AC-n = critério de aceitação da primeira fatia (FI-01 §11.2). ADR = decisão registrada em `adr/`.
- **Verificação**: o teste que comprova o requisito (arquivo previsto · caso). `e2e/` são testes de interface do painel (Playwright + axe).

Convenções usadas no texto:

- "lote ativo" é o lote indicado por `PublicacaoAtiva` para a fonte.
- Valores monetários são inteiros em centavos (`*_centavos`).
- Erros da API seguem `application/problem+json` (RFC 9457) com o campo `codigo`.

## A · Importação e publicação

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-01 | E | QUANDO o operador executar `rastro importar --fonte cgu --arquivo <zip>`, O SISTEMA DEVE ler os CSVs em Latin-1 com separador `;` em fluxo e registrar um `LoteImportacao` no estado `validado`, com `hash_sha256` do arquivo e contagens de `linhas_lidas`, `linhas_aceitas` e `linhas_rejeitadas`. | FI-01 §11.3 | `tests/test_cgu.py::test_importa_zip_exemplo` |
| REQ-02 | I | SE uma linha tiver `Código da Emenda` fora do padrão de 12 dígitos, ENTÃO O SISTEMA DEVE rejeitá-la com o motivo `codigo_invalido` e somá-la em `RejeicaoLote` do lote. | FI-01 §11.3 | `tests/test_cgu.py::test_rejeita_codigo_invalido` |
| REQ-03 | I | SE um valor monetário não puder ser convertido para centavos inteiros (formato `1.234,56`), ENTÃO O SISTEMA DEVE rejeitar a linha com o motivo `valor_malformado`. | FI-01 §11.3 | `tests/test_cgu.py::test_rejeita_valor_malformado` |
| REQ-04 | I | SE o pacote da fonte não tiver todas as colunas esperadas pelo contrato de importação, ENTÃO O SISTEMA DEVE marcar o lote como `falhou`, registrar `motivo_falha = formato_alterado` e manter o lote ativo anterior. | FI-01 §10.3 | `tests/test_cgu.py::test_formato_alterado` |
| REQ-05 | E | QUANDO o operador importar um arquivo cujo `hash_sha256` já pertence a um lote `validado`, `publicado` ou `substituido` da mesma fonte, O SISTEMA DEVE encerrar com código 0 e a mensagem "lote já importado (Lote #n)", sem criar lote nem alterar registros. | AC-2 | `tests/test_store.py::test_reimportacao_nao_duplica` |
| REQ-06 | I | SE as linhas rejeitadas por `codigo_invalido`, `valor_malformado`, `linha_malformada` ou `emenda_sem_cadastro` passarem de 5% das linhas do recorte (linhas lidas menos `ano_fora_do_recorte`), ENTÃO O SISTEMA DEVE recusar o lote (estado `recusado`, `motivo_falha = rejeicoes_acima_do_limite`) e manter o lote ativo anterior. | ADR-0001 | `tests/test_store.py::test_recusa_lote_com_muitas_rejeicoes` |
| REQ-07 | E | QUANDO o operador executar `rastro publicar --lote <id>` sobre um lote `validado`, O SISTEMA DEVE trocar `PublicacaoAtiva.lote_id` da fonte e marcar o lote anterior como `substituido`, numa única transação. | AC-3, ADR-0001 | `tests/test_store.py::test_publicacao_atomica` |
| REQ-08 | E | QUANDO um lote for publicado e já existir lote ativo da mesma fonte, O SISTEMA DEVE calcular as `MudancaLote` entre o lote ativo e o novo, na mesma transação da troca. No primeiro lote publicado de uma fonte, nenhuma `MudancaLote` é gerada. | ADR-0004 | `tests/test_mudancas.py::test_mudancas_calculadas_na_publicacao` · `::test_primeiro_lote_sem_mudancas` |
| REQ-09 | S | ENQUANTO uma importação ou publicação estiver em andamento, O SISTEMA DEVE responder cada consulta com dados de um único lote por fonte: o que estava ativo no início da transação de leitura. | AC-3, ADR-0002 | `tests/test_store.py::test_leitura_durante_publicacao` |
| REQ-10 | I | SE o processo de importação for interrompido antes de terminar, ENTÃO O SISTEMA DEVE, na execução seguinte da CLI, marcar o lote como `falhou` com `motivo_falha = interrompido`. Nenhum registro desse lote pode aparecer nas consultas. | ADR-0001 | `tests/test_store.py::test_lote_interrompido` |
| REQ-11 | E | QUANDO o agendador disparar `rastro sincronizar`, O SISTEMA DEVE baixar as fontes habilitadas concorrentemente e publicar os lotes válidos um de cada vez (um único escritor no banco). | Brief (gancho de concorrência) | `tests/test_sincronizar.py::test_downloads_concorrentes_publicacao_serial` |
| REQ-12 | I | SE o download de uma fonte falhar, ENTÃO O SISTEMA DEVE registrar um lote `falhou` com `motivo_falha = fonte_indisponivel`, manter o lote ativo anterior e continuar mostrando a `data_referencia` dele. | FI-01 §10.4 | `tests/test_sincronizar.py::test_fonte_indisponivel` |
| REQ-13 | O | ONDE a fonte Siga Brasil estiver habilitada (`Fonte.habilitada = true`), O SISTEMA DEVE importar os valores de execução orçamentária dela como lotes da fonte `siga` e exibi-los separados dos valores da CGU, sem somar valores das duas fontes. | FI-01 §4.2, §12 | `tests/test_siga.py::test_valores_por_fonte_nao_somados` (fase 6) |

## B · Consulta pública (API e painel)

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-14 | U | O SISTEMA DEVE acompanhar todo valor exibido no painel ou devolvido pela API com a sua proveniência: `Fonte.nome`, `LoteImportacao.id`, `LoteImportacao.data_referencia`, `LoteImportacao.hash_sha256` e `Fonte.url_download`. | FI-01 §10.1 | `tests/test_api.py::test_toda_resposta_tem_proveniencia` · `e2e/proveniencia.spec.ts` |
| REQ-15 | U | O SISTEMA DEVE apresentar valor empenhado, liquidado, pago, restos a pagar e valor recebido por favorecido como grandezas distintas, cada uma com rótulo e definição próprios. Nenhuma tela nem resposta pode somar etapas diferentes num total único. | FI-01 §4.1 | `e2e/etapas-distintas.spec.ts` |
| REQ-16 | E | QUANDO um cliente pedir `GET /api/emendas/{codigo}` com um código existente no lote ativo, O SISTEMA DEVE devolver 200 com a emenda, os valores por etapa e a proveniência de cada valor. | AC-1 | `tests/test_api.py::test_consulta_emenda_conhecida` |
| REQ-17 | I | SE o `codigo` pedido não tiver 12 dígitos, ENTÃO O SISTEMA DEVE responder 422 com `codigo = codigo_malformado`. | AC-4 | `tests/test_api.py::test_codigo_malformado_422` |
| REQ-18 | I | SE o `codigo` pedido for bem formado mas não existir no lote ativo, ENTÃO O SISTEMA DEVE responder 404 com `codigo = emenda_nao_encontrada`. | AC-4 | `tests/test_api.py::test_codigo_inexistente_404` |
| REQ-19 | S | ENQUANTO não houver lote publicado para a fonte `cgu`, O SISTEMA DEVE responder 503 com `codigo = sem_lote_publicado` a toda operação de dados, exceto `obter_status`, `listar_lotes`, `obter_lote` e `obter_contrato`. | AC-4 | `tests/test_api.py::test_sem_lote_503` |
| REQ-20 | E | QUANDO o cliente listar emendas com qualquer combinação de `ano`, `autor_codigo`, `uf_gasto`, `funcao_codigo`, `tipo` e `q`, O SISTEMA DEVE devolver no máximo `por_pagina` (≤ 100) emendas que atendam a todos os filtros, ordenadas por `ordenar` (`codigo`, `-empenhado`, `-liquidado` ou `-pago`), com `total` igual ao número de emendas que atendem aos filtros. | FI-01 §4.2 (2) | `tests/test_api.py::test_lista_filtrada_paginada` |
| REQ-21 | U | O SISTEMA DEVE derivar `Emenda.uf_gasto` da coluna "Localidade do gasto" e nunca da UF do favorecido. Localidades nacionais ou de várias UFs são gravadas com `uf_gasto` nulo e representadas na API e nos filtros pela sigla reservada `NM` ("Nacional ou múltiplas UFs"). | FI-01 §3.2 | `tests/test_cgu.py::test_uf_do_gasto` |
| REQ-22 | E | QUANDO o cliente pedir agregações por `autor`, `uf` ou `funcao`, O SISTEMA DEVE devolver, por grupo, a soma de cada etapa separadamente e a quantidade de emendas do lote ativo. Na dimensão `autor`, grupos de autores com `Autor.tipo ≠ parlamentar` vêm com `coletivo = true` e `rotulo` igual a `Autor.nome`. | FI-01 §4.2 (2), Brief | `tests/test_api.py::test_agregacoes_por_dimensao` |
| REQ-23 | E | QUANDO o cliente pedir a linha do tempo de uma emenda, O SISTEMA DEVE devolver, para cada etapa, a sequência de valores em todos os lotes publicados da fonte, cada ponto com o lote e a `data_referencia` em que o valor apareceu. | FI-01 §4.2 (4) | `tests/test_api.py::test_linha_do_tempo_aponta_lote` |
| REQ-24 | E | QUANDO o cliente pedir as mudanças sem `lote_novo_id`, O SISTEMA DEVE devolver as `MudancaLote` do lote ativo da fonte (comparado ao lote que ele substituiu). | FI-01 §4.2 (5) | `tests/test_api.py::test_o_que_mudou` |
| REQ-25 | U | O SISTEMA DEVE exibir favorecido pessoa física com `Favorecido.nome_publicavel` e `Favorecido.codigo_origem` (CPF mascarado) exatamente como publicados pela CGU. | ADR-0007 | `tests/test_api.py::test_pf_como_publicado` · `e2e/favorecidos.spec.ts` |
| REQ-26 | U | O SISTEMA DEVE exibir, junto a toda lista de favorecidos, o aviso: "Recebimento registrado não comprova a aplicação final do recurso nem indica irregularidade." | FI-01 §5 | `e2e/favorecidos.spec.ts` |
| REQ-27 | E | QUANDO o cliente listar os lotes, O SISTEMA DEVE devolver os lotes de cada fonte com `estado`, `data_referencia`, `hash_sha256`, `linhas_aceitas`, `linhas_rejeitadas` e as rejeições por motivo. | FI-01 §10.1 | `tests/test_api.py::test_lista_lotes` |
| REQ-28 | I | SE um mesmo IP, exceto o loopback usado pelo painel e pelo script de carga, passar de 60 requisições por minuto na API pública, ENTÃO O SISTEMA DEVE responder 429 com o cabeçalho `Retry-After`. | FI-01 §3.1 (limites a definir) | `tests/test_api.py::test_limite_de_taxa` |
| REQ-29 | E | QUANDO o cliente pedir um autor pelo `codigo`, O SISTEMA DEVE devolver nome, tipo, soma por etapa e a lista paginada das emendas do autor no lote ativo. | FI-01 §4.2 (2) | `tests/test_api.py::test_autor` |
| REQ-30 | U | O SISTEMA DEVE servir em `/openapi.json` o contrato OpenAPI 3.1 da API, semanticamente igual a `contratos/openapi.yaml`. | ADR-0003 | `tests/test_contrato.py::test_openapi_igual_ao_versionado` |

## C · Assinaturas e alertas

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-31 | E | QUANDO um visitante sem chave criar a primeira assinatura, O SISTEMA DEVE gerar uma chave de assinante aleatória de 128 bits, devolvê-la uma única vez na resposta e guardar apenas `Assinante.chave_hash` (SHA-256). | ADR-0005 | `tests/test_assinaturas.py::test_chave_devolvida_uma_vez` |
| REQ-32 | I | SE uma requisição a `/api/assinaturas` ou `/api/alertas` vier com o cabeçalho `X-Chave-Assinante` ausente ou desconhecido, ENTÃO O SISTEMA DEVE responder 401 com `codigo = chave_invalida`, sem revelar se existem assinaturas. Exceção: `POST /api/assinaturas` sem o cabeçalho, que cria a chave (REQ-31). | ADR-0005 | `tests/test_assinaturas.py::test_chave_invalida_401` |
| REQ-33 | E | QUANDO o assinante criar uma assinatura válida, O SISTEMA DEVE gravá-la com `estado = ativa` e `lote_base_id` igual ao lote ativo da fonte `cgu`, e responder 201. | FI-01 §4.2 (6) | `tests/test_assinaturas.py::test_cria_assinatura` |
| REQ-34 | I | SE a assinatura não tiver nenhum critério de filtro, ENTÃO O SISTEMA DEVE responder 422 com `codigo = assinatura_invalida`. | FI-01 §4.2 (6) | `tests/test_assinaturas.py::test_assinatura_sem_filtro_422` |
| REQ-35 | E | QUANDO um lote for publicado, O SISTEMA DEVE avaliar todas as assinaturas ativas contra as `MudancaLote` desse lote e criar um `Alerta` para cada par (assinatura, mudança) em que a mudança atenda ao filtro e à condição da assinatura (REQ-63, REQ-64). | FI-01 §4.2 (7), ADR-0004 | `tests/test_alertas.py::test_avalia_assinaturas_ativas` |
| REQ-36 | U | O SISTEMA DEVE manter no máximo um `Alerta` por par (`assinatura_id`, `mudanca_id`), inclusive quando a avaliação for repetida ou executada em paralelo. | FI-01 §10.1, ADR-0004 | `tests/test_alertas.py::test_sem_duplicata_concorrente` |
| REQ-37 | U | O SISTEMA DEVE considerar, para cada assinatura, apenas mudanças de lotes publicados depois de `Assinatura.lote_base_id`. | ADR-0004 | `tests/test_alertas.py::test_ignora_mudancas_anteriores` |
| REQ-38 | S | ENQUANTO uma assinatura estiver com `estado = pausada`, O SISTEMA DEVE ignorá-la na avaliação de alertas. | FI-01 §4.2 (6) | `tests/test_alertas.py::test_pausada_sem_alerta` |
| REQ-39 | E | QUANDO o assinante marcar um alerta como lido, O SISTEMA DEVE gravar `Alerta.lido_em`. Repetir a operação não altera o valor gravado. | FI-01 §4.2 (7) | `tests/test_alertas.py::test_marcar_lido_idempotente` |
| REQ-40 | E | QUANDO o assinante excluir uma assinatura, O SISTEMA DEVE remover a assinatura e os alertas dela, e responder 204. | FI-01 §4.2 (6) | `tests/test_assinaturas.py::test_exclui_assinatura` |
| REQ-41 | U | O SISTEMA DEVE operar assinaturas apenas com a chave de assinante, sem coletar nome, e-mail, telefone ou outro dado pessoal. | FI-01 §10.2, ADR-0005 | revisão do contrato `Assinatura`/`Assinante` · `tests/test_contrato.py::test_sem_dado_pessoal` |
| REQ-42 | I | SE um assinante tentar criar mais de 20 assinaturas, ENTÃO O SISTEMA DEVE responder 422 com `codigo = limite_assinaturas`. | ADR-0005 | `tests/test_assinaturas.py::test_limite_20` |

## D · Interface do painel

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-43 | U | O painel DEVE atender à WCAG 2.2 nível AA em todas as telas P, D e S, com zero violações `serious` ou `critical` no axe-core. | Trabalho 1 §2.1 | `e2e/acessibilidade.spec.ts` |
| REQ-44 | E | QUANDO uma tela esperar resposta da API por mais de 300 ms, O painel DEVE exibir esqueleto de carregamento, nunca valores provisórios. | Diretrizes | `e2e/estados.spec.ts::carregando` |
| REQ-45 | E | QUANDO uma consulta não tiver resultados, O painel DEVE exibir o estado vazio com os filtros aplicados e a ação "Limpar filtros". | Diretrizes | `e2e/estados.spec.ts::vazio` |
| REQ-46 | I | SE a API responder com erro 5xx, ENTÃO O painel DEVE exibir uma mensagem de erro com o identificador da requisição (`X-Request-Id`) e a ação "Tentar de novo". | Diretrizes | `e2e/estados.spec.ts::erro` |
| REQ-47 | S | ENQUANTO o navegador estiver sem conexão, O painel DEVE exibir o aviso "Sem conexão" e ocultar valores carregados antes, sem apresentá-los como atuais. | Diretrizes | `e2e/estados.spec.ts::offline` |
| REQ-48 | U | O painel DEVE mostrar em toda tela com dados a `data_referencia` e o id do lote ativo, com link para P09. | FI-01 §10.4 | `e2e/proveniencia.spec.ts` |

## E · Desempenho e engenharia

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-49 | U | A API DEVE responder `GET /api/emendas/{codigo}` com p95 < 100 ms e `GET /api/agregacoes` com p95 < 300 ms, sob 20 usuários virtuais por 60 s, com a base 2025 completa na máquina de referência. | Brief (gancho de desempenho) | `scripts/carga.py` (relatório p50/p95/p99) |
| REQ-50 | U | O ETL DEVE importar e validar o ZIP completo de emendas da CGU em até 10 min na máquina de referência e gravar a duração de cada etapa (leitura, validação, gravação, publicação) em `LoteImportacao.duracao_etl_ms`. | Brief (gancho de desempenho) | `scripts/medir_etl.py` |
| REQ-51 | U | O pipeline de CI DEVE executar `pytest`, lint e typecheck do painel a cada push, e o merge na `main` só pode acontecer com o pipeline aprovado. | FI-01 §6 | GitHub Actions `ci.yml` |

## F · Requisitos acrescentados na revisão (ids novos, sem renumerar os anteriores)

| ID | Molde | Requisito | Origem | Verificação |
| :-- | :-: | :-- | :-- | :-- |
| REQ-52 | I | SE o arquivo importado tiver o `hash_sha256` de um lote `recusado` da mesma fonte, ENTÃO O SISTEMA DEVE encerrar com código 2 e a mensagem "lote já recusado (Lote #n)", sem criar lote. | AC-2 | `tests/test_store.py::test_reimportar_recusado` |
| REQ-53 | E | QUANDO o operador importar um arquivo cujo `hash_sha256` só pertence a lotes `falhou`, O SISTEMA DEVE criar um novo lote para ele (a unicidade de hash ignora lotes `falhou`). | AC-2, REQ-10 | `tests/test_store.py::test_reimportar_falhou` |
| REQ-54 | U | O SISTEMA DEVE aceitar os registros por favorecido de emendas de 2025 qualquer que seja o `ano_mes` do pagamento, até a `data_referencia` do lote. | FI-01 §4.3 | `tests/test_cgu.py::test_pagamentos_de_outros_anos` |
| REQ-55 | I | SE o cliente pedir um autor (`obter_autor`) ou lote (`obter_lote`, `listar_mudancas?lote_novo_id=`) inexistente, ENTÃO O SISTEMA DEVE responder 404 com `codigo = nao_encontrado`. | Contrato | `tests/test_api.py::test_404_generico` |
| REQ-56 | I | SE outro processo da CLI já estiver escrevendo no banco (trava `data/rastro.lock`), ENTÃO a CLI DEVE encerrar com código 5 sem alterar dados. | ADR-0002 | `tests/test_cli.py::test_trava_escritor_unico` |
| REQ-57 | I | SE o operador executar `rastro publicar` sobre lote que não esteja `validado` (sem `--reprocessar-alertas`), ENTÃO a CLI DEVE encerrar com código 6 e manter o lote ativo. | ADR-0001 | `tests/test_cli.py::test_publicar_lote_nao_validado` |
| REQ-58 | I | SE o navegador bloquear o `localStorage` ou a área de transferência, ENTÃO O painel DEVE avisar o usuário e oferecer a alternativa manual (texto selecionável, arquivo .txt). | ADR-0005 | `e2e/chave.spec.ts::armazenamento_bloqueado` |
| REQ-59 | I | SE o ano da emenda for diferente de 2025, ENTÃO O SISTEMA DEVE descartar a linha com o motivo `ano_fora_do_recorte`, contado em `RejeicaoLote` mas fora da taxa do REQ-06. | FI-01 §4.3, §10.2 | `tests/test_cgu.py::test_ano_fora_do_recorte` |
| REQ-60 | S | ENQUANTO `obter_status` indicar `lote_ativo = null` para a fonte `cgu`, O painel DEVE exibir "Dados ainda não publicados" no lugar de qualquer valor. | AC-4 | `e2e/sem-lote.spec.ts` |
| REQ-61 | E | QUANDO o cliente pedir as mudanças com `lote_novo_id` de um lote publicado ou substituído, O SISTEMA DEVE devolver as `MudancaLote` desse lote. | FI-01 §4.2 (5) | `tests/test_api.py::test_mudancas_de_lote_antigo` |
| REQ-62 | I | SE a assinatura tiver `condicao = limiar_valor` sem `etapa` ou com `limiar_centavos` ≤ 0, ENTÃO O SISTEMA DEVE responder 422 com `codigo = assinatura_invalida` e o campo em `Problema.campos`. | FI-01 §4.2 (6) | `tests/test_assinaturas.py::test_limiar_invalido_422` |
| REQ-63 | U | O SISTEMA DEVE considerar satisfeita a condição `limiar_valor` quando, na `etapa` da assinatura, `valor_antes_centavos < limiar_centavos ≤ valor_depois_centavos`, tratando `valor_antes_centavos` nulo (`nova_emenda`) como 0. | ADR-0004 | `tests/test_alertas.py::test_condicao_limiar` |
| REQ-64 | U | O SISTEMA DEVE considerar satisfeita a condição `mudanca_estado` quando a `MudancaLote` tiver `tipo = estado_alterado` ou `nova_emenda`. | ADR-0006 | `tests/test_alertas.py::test_condicao_estado` |
| REQ-65 | U | O SISTEMA NÃO DEVE oferecer busca, filtro, ordenação ou página própria por favorecido pessoa física, na API e no painel. | ADR-0007 | `tests/test_api.py::test_pf_sem_busca` |

## Ligação com os critérios de aceitação da primeira fatia (FI-01 §11.2)

| AC | Requisitos |
| :-- | :-- |
| AC-1 | REQ-01, REQ-14, REQ-16 |
| AC-2 | REQ-05, REQ-52, REQ-53 |
| AC-3 | REQ-07, REQ-09 |
| AC-4 | REQ-17, REQ-18, REQ-19, REQ-60 |
