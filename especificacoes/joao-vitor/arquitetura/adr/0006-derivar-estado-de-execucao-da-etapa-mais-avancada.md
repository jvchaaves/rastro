# ADR-0006 · Derivar o estado de execução da etapa mais avançada com valor positivo

- **Status:** proposta (fecha provisoriamente a lacuna "definição de mudança de status" do FI-01 §12; três das quatro verificações já foram feitas com o arquivo real de 26/10/2026; passa a *aceita* quando a quarta, que exige um segundo lote, também passar; ver "Verificação com dados reais")
- **Data:** 26/10/2026
- **Revisão:** 27/10/2026, depois da conferência com o arquivo real: o estado `paga` foi dividido em `paga_em_parte` e `paga` (ver "Revisão de 27/10/2026")
- **Requisitos ligados:** REQ-105, REQ-106, REQ-35, REQ-63, REQ-64, REQ-68, REQ-69

## Contexto

O brief pede que o sistema "avise quem assinou quando alguma coisa muda entre um lote e o seguinte", e o FI-01 §4.2 (funcionalidade 6) prevê assinar "mudança de estado". O pacote da CGU não traz um campo de status: traz valores acumulados por etapa. Uma assinatura do tipo `mudanca_estado` precisa de uma definição testável.

## Opções consideradas

1. **Esperar um campo oficial de status** (não existe no pacote inspecionado em 24/09/2026).
   - Prós: nenhuma regra própria. Contras: o campo não existe. **Descartada** porque bloquearia as funcionalidades 6 e 7 do FI-01 (assinar mudança de estado e receber o alerta).
2. **Qualquer variação de valor** conta como mudança de status.
   - Prós: simples. Contras: alerta a cada centavo e confunde valor com estado. **Descartada** pelo excesso de alertas.
3. **Estado derivado:** a etapa mais avançada com valor > 0 e, havendo pagamento, se ele alcança o valor devido, na ordem `sem_execucao` < `empenhada` < `liquidada` < `paga_em_parte` < `paga`.
   - Prós: testável com dois lotes sintéticos, vocabulário controlado. Contras: cancelamentos e empenhos novos podem fazer o estado recuar.

## Decisão

Opção 3, porque é a única definição testável com os campos que a CGU publica hoje.

- A regra completa está no REQ-105. O pagamento considera `pago + rap_pago`, e o valor devido é `empenhado − rap_cancelado`, o mesmo recorte do REQ-68:
  - `paga`: pagamento > 0 e ≥ valor devido;
  - `paga_em_parte`: pagamento > 0 e < valor devido;
  - `liquidada`: sem pagamento e `liquidado` > 0;
  - `empenhada`: só `empenhado` > 0;
  - `sem_execucao`: nenhum valor.
- O estado é calculado pela view `v_emenda_estado` em cada lote.
- A mudança de estado é gravada (REQ-106) como `MudancaLote.tipo = estado_alterado`, com `estado_antes` e `estado_depois`.
- Toda variação de valor de uma etapa fica como `valor_alterado`, também quando o estado muda junto; nesse caso há as duas linhas. Assim, um limiar cruzado na mesma publicação que muda o estado também gera alerta (REQ-63).

## Verificação com dados reais

Arquivo oficial da CGU baixado em 27/10/2026 (dados de 26/10/2026), 6 310 emendas de 2025:

| Pergunta | Resultado | Situação |
| :-- | :-- | :-- |
| As etapas são coerentes entre si (liquidado ≤ empenhado, pago ≤ liquidado)? | Sim, em 100% das linhas | confirmada |
| Existe liquidado ou pago com empenhado zero? | Nenhum caso; toda emenda de 2025 tem empenho | confirmada |
| Os restos a pagar vêm na mesma linha da emenda? | Sim: 3 548 emendas têm restos a pagar pagos, nas colunas da própria emenda | confirmada |
| Os valores só sobem de um lote para o seguinte? | Não dá para responder com um lote só | **pendente**: baixar de novo depois da próxima atualização e comparar |

Distribuição do estado derivado no lote conferido, já com a revisão abaixo: `paga` 3 559 (56%), `paga_em_parte` 2 349 (37%), `empenhada` 401, `liquidada` 1, `sem_execucao` 0.

**Critério para passar a *aceita*:** em dois lotes consecutivos, menos de 1% das emendas de 2025 recua de estado. Se recuar mais, uma ADR nova revê a regra.

## Revisão de 27/10/2026

Na primeira versão desta ADR havia quatro estados, e qualquer pagamento tornava a emenda `paga`. No arquivo real, isso pôs 94% das emendas de 2025 em `paga`, inclusive 2 349 (37%) que receberam só parte do empenhado. O morador leria "Já houve pagamento registrado" sem saber que falta dinheiro.

- **Mudança:** o estado `paga` foi dividido em `paga_em_parte` ("Parte do dinheiro já foi paga") e `paga` ("Todo o valor devido foi pago"; devido = empenhado menos cancelado). A tabela de tradução v1 já nasce com os cinco textos (`../contratos/modelo-de-dados.md`, ADR-0008).
- **Coerência com o recorte do gestor:** toda emenda `paga_em_parte` está em "empenhado e ainda não pago" (REQ-68), e nenhuma `paga` está. No arquivo conferido, o recorte tem 2 750 emendas: 2 349 `paga_em_parte`, 400 `empenhada` e 1 `liquidada`; a única `empenhada` fora dele teve o empenho todo cancelado.
- **Efeito nas assinaturas:** a passagem de `paga_em_parte` para `paga` é uma mudança de estado e gera alerta para a condição `mudanca_estado` (REQ-64). Ela acontece quando um pagamento novo alcança o valor devido ou quando um cancelamento de restos a pagar reduz o valor devido até o já pago (267 emendas de 2025 têm cancelamento). O Rastro mostra a mudança e os valores por etapa, sem dizer qual das duas causas houve (P08).
- **Recuo novo:** um empenho a mais numa emenda `paga` a faz voltar a `paga_em_parte`. Esse recuo é mostrado como mudança, como os demais (P08), e conta no critério de 1% acima.

## Consequências

- **(+)** A regra é testável com dois lotes sintéticos e independe de campos que a CGU não publica.
- **(+)** A interface usa vocabulário controlado ("empenhada", "liquidada", "paga em parte", "paga") e não afirma nada sobre a aplicação final.
- **(−)** Um cancelamento (valor voltando a 0) ou um empenho novo numa emenda já paga produz retrocesso de estado, o que é raro mas possível. Ele é mostrado como mudança e merece revisão quando houver dados reais.
- **(−)** Se a CGU passar a publicar um status oficial, esta ADR será substituída.
