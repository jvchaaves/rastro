# ADR-0003 · Derivar a fase dos valores, incluindo restos a pagar, e traduzi-la por tabela com fonte obrigatória

- **Status:** aceita (revista em 27/10/2026, após a T1; tabela em versão 1 com fontes oficiais, aguardando o teste de compreensão)
- **Contexto:** A aposta central (FI §4.4) é que traduzir as fases faz o morador entender o que aconteceu com o dinheiro. Uma tradução errada atribui a parlamentares e prefeituras algo que não aconteceu (FI §3.2). A T1 mostrou que na fonte:
  - `Valor Pago` registra só o pago **no ano do empenho**; o que é pago depois aparece em `Valor Restos A Pagar Pagos`;
  - cancelamentos aparecem em `Valor Restos A Pagar Cancelados`;
  - `Valor Restos A Pagar Inscritos` não fecha com os outros campos em 61% das linhas;
  - nenhuma linha tem empenhado = 0 sem cancelamento (a fase "sem empenho" não existe nos dados).
- **Opções consideradas:**
  1. Texto livre nos templates.
  2. Explicação gerada por LLM a cada emenda.
  3. Regra só com `valor_empenhado`, `valor_liquidado` e `valor_pago` (versão inicial).
  4. Regra com `valor_final = empenhado − rp_cancelado` e `valor_pago_total = pago + rp_pago` (REQ-13), mais tabela `termo_traduzido` com fonte obrigatória (REQ-16) e lista de expressões proibidas (REQ-15).
- **Decisão:** Opção 4. `fase_simples` ∈ {`empenhada`, `liquidada`, `paga_parcial`, `paga`, `cancelada`}, calculada na view `emenda_ativa`. `rp_inscrito` é guardado, mas não entra em regra.
- **Evidência (T1, 2 780 linhas da PB):**
  - A opção 3 classificava errado 1 745 linhas (63%), em geral mostrando "reservado" para emenda já paga.
  - Na opção 4, em 93% das emendas com código, `valor_pago_total` é igual à soma recebida pelos favorecidos, uma fonte independente.
- **Consequências:**
  - \+ A fase exibida bate com quem recebeu o dinheiro.
  - \+ 100% dos termos exibidos têm fonte, garantido pelo banco.
  - \+ Regra pura, testável com casos reais extraídos da T1 (Q5).
  - − "Liquidada" é rara (2 linhas): a liquidação de restos a pagar não é publicada em separado. Aceito: o texto não promete mais do que os dados dizem.
  - − Os 7% restantes (favorecidos ≠ pago total) seguem a regra pelos valores; a diferença aparece na lista "Para quem foi pago".
  - Opções 1 e 2 descartadas: textos divergentes e sem fonte. Opção 3 descartada pela evidência acima.
