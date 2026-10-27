# ADR-0006 · Derivar o estado de execução da etapa mais avançada com valor positivo

- **Status:** proposta (fecha provisoriamente a lacuna "definição de mudança de status" do FI-01 §12; três das quatro verificações já foram feitas com o arquivo real de 26/10/2026; passa a *aceita* quando a quarta, que exige um segundo lote, também passar; ver "Verificação com dados reais")
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-35, REQ-23, REQ-63, REQ-64, REQ-69

## Contexto

O brief pede que o sistema "avise quem assinou quando alguma coisa muda entre um lote e o seguinte", e o FI-01 §4.2 (funcionalidade 6) prevê assinar "mudança de estado". O pacote da CGU não traz um campo de status: traz valores acumulados por etapa. Uma assinatura do tipo `mudanca_estado` precisa de uma definição testável.

## Opções consideradas

1. **Esperar um campo oficial de status** (não existe no pacote inspecionado em 24/09/2026).
   - Prós: nenhuma regra própria. Contras: o campo não existe. **Descartada** porque bloquearia as funcionalidades 6 e 7 do FI-01 (assinar mudança de estado e receber o alerta).
2. **Qualquer variação de valor** conta como mudança de status.
   - Prós: simples. Contras: alerta a cada centavo e confunde valor com estado. **Descartada** pelo excesso de alertas.
3. **Estado derivado:** a etapa mais avançada com valor > 0, na ordem `sem_execucao` < `empenhada` < `liquidada` < `paga`.
   - Prós: testável com dois lotes sintéticos, vocabulário controlado. Contras: cancelamentos podem fazer o estado recuar.

## Decisão

Opção 3, porque é a única definição testável com os campos que a CGU publica hoje.

- `paga` considera `pago + rap_pago > 0`.
- O estado é calculado pela view `v_emenda_estado` em cada lote.
- A mudança de estado é gravada como `MudancaLote.tipo = estado_alterado`, com `estado_antes` e `estado_depois`.
- Toda variação de valor de uma etapa fica como `valor_alterado`, também quando o estado muda junto; nesse caso há as duas linhas. Assim, um limiar cruzado na mesma publicação que muda o estado também gera alerta (REQ-63).

## Verificação com dados reais

Arquivo oficial da CGU baixado em 27/10/2026 (dados de 26/10/2026), 6 310 emendas de 2025:

| Pergunta | Resultado | Situação |
| :-- | :-- | :-- |
| As etapas são coerentes entre si (liquidado ≤ empenhado, pago ≤ liquidado)? | Sim, em 100% das linhas | confirmada |
| Existe liquidado ou pago com empenhado zero? | Nenhum caso; toda emenda de 2025 tem empenho | confirmada |
| Os restos a pagar vêm na mesma linha da emenda? | Sim: 3 548 emendas têm restos a pagar pagos, nas colunas da própria emenda | confirmada |
| Os valores só sobem de um lote para o seguinte? | Não dá para responder com um lote só | **pendente**: baixar de novo depois da próxima atualização e comparar |

Distribuição do estado derivado no lote conferido: `paga` 5 908 (94%), `empenhada` 401, `liquidada` 1, `sem_execucao` 0.

**Critério para passar a *aceita*:** em dois lotes consecutivos, menos de 1% das emendas de 2025 recua de estado. Se recuar mais, uma ADR nova revê a regra.

**Limitação observada:** como qualquer pagamento torna a emenda `paga`, 2 349 emendas (37%) aparecem como `paga` tendo recebido só parte do empenhado. O texto da tradução v1 ("Já houve pagamento registrado") é verdadeiro para elas, e o recorte "empenhado e ainda não pago" (REQ-68) mostra essas 2 750 emendas pendentes, mas o estado sozinho não as distingue. Se o grupo quiser essa distinção no próprio estado, a alternativa é um quinto valor, `paga_em_parte`, numa ADR nova.

## Consequências

- **(+)** A regra é testável com dois lotes sintéticos e independe de campos que a CGU não publica.
- **(+)** A interface usa vocabulário controlado ("empenhada", "liquidada", "paga") e não afirma nada sobre a aplicação final.
- **(−)** Um cancelamento (valor voltando a 0) produz retrocesso de estado, o que é raro mas possível. Ele é mostrado como mudança e merece revisão quando houver dados reais.
- **(−)** Se a CGU passar a publicar um status oficial, esta ADR será substituída.
