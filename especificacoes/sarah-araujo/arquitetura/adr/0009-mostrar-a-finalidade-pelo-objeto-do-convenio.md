# ADR-0009 · Mostrar a finalidade da emenda pelo objeto do convênio, como texto da fonte

- **Status:** aceita (27/10/2026, T1-b)
- **Contexto:** A pergunta "para que era esse dinheiro?" (que obra, que hospital) não é respondida por área e ação do orçamento, que são genéricas. O arquivo do Portal traz `EmendasParlamentares_Convenios.csv`, com objeto, convenente, número, data e valor de cada convênio. Na T1-b, porém, só 31% das emendas da PB com código têm convênio (36% em João Pessoa), nenhuma transferência especial tem, e muitos objetos são genéricos ("Aquisição de equipamento e material permanente…").
- **Opções consideradas:**
  1. Não mostrar finalidade além de área e ação.
  2. Mostrar o objeto do convênio como está na fonte e dizer explicitamente quando ele não existe.
  3. Gerar um resumo da finalidade (por regra ou por modelo de linguagem) a partir de área, ação e objeto.
  4. Integrar Transferegov e Sagres (TCE-PB) para seguir o dinheiro dentro da prefeitura.
- **Decisão:** Opção 2 (REQ-71 a REQ-73, REQ-82).
- **Consequências:**
  - \+ Responde "para quê" com o texto oficial em um terço das emendas, inclusive casos muito concretos (ex.: obras viárias com ciclovias, R$ 15,7 mi).
  - \+ Nada é inventado: o texto vem da fonte e é rotulado "Descrição informada no convênio".
  - − Em dois terços das emendas não há descrição; a tela diz isso, em vez de esconder.
  - − Objetos genéricos continuam genéricos.
  - Opção 3 descartada: um resumo gerado poderia afirmar uma finalidade que o documento não afirma. Opção 4 fica fora do MVP: outras fontes e outro formato, ainda não verificados.
