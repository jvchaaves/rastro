# ADR-0008 · Mostrar o dinheiro da cidade por dois caminhos separados: destino declarado e pagamento à prefeitura

- **Status:** aceita (27/10/2026, T1)
- **Contexto:** O FI-01 previa mostrar na cidade só as emendas com município declarado. A T1 mostrou que, na PB:
  - emendas com município declarado somam R$ 0,95 bi empenhados;
  - emendas `MÚLTIPLO` somam R$ 4,82 bi;
  - emendas para o estado somam R$ 1,12 bi.

  Pelo desenho original, a página da cidade mostraria cerca de 14% do dinheiro, o oposto do aviso que o FI pede (§10.2: "sem o aviso, a cidade pareceria ter recebido menos"). A tabela de favorecidos mostra para quem cada emenda pagou, com natureza jurídica e município (só pelo nome). Dos R$ 4,49 bi pagos pelas `MÚLTIPLO` da PB, R$ 2,48 bi foram a prefeituras ou fundos municipais da PB, e R$ 1,83 bi ao Banco do Brasil (DF), intermediário. Há ainda R$ 1,75 bi pagos a entidades da PB por emendas de fora do filtro de UF.
- **Opções consideradas:**
  1. Manter só o destino declarado, com aviso.
  2. Atribuir à cidade todo pagamento a qualquer favorecido com endereço nela.
  3. Dois blocos, nunca somados: **(a)** emendas destinadas à cidade, com fase (REQ-08); **(b)** recebido de outras emendas pela prefeitura e pelos fundos municipais, com valor recebido (REQ-54). Pagamentos a outras entidades da cidade são listados à parte, sem entrar no resumo (REQ-56). Intermediários financeiros nunca são atribuídos a um município (REQ-60).
- **Decisão:** Opção 3 (A03, A14, A08).
- **Consequências:**
  - \+ A cidade deixa de parecer ter recebido muito menos do que recebeu, sem afirmar o que os dados não dizem.
  - \+ "Prefeitura e fundos municipais" é um critério verificável (natureza jurídica), não uma interpretação.
  - \+ Sem dupla contagem: o bloco (b) exclui emendas cujo destino declarado já é a cidade (REQ-54), e os blocos não são somados (REQ-55).
  - − O bloco (b) não tem fase, só valor recebido. A tela diz isso explicitamente.
  - − O município do favorecido é resolvido pelo nome. Há uma tabela de nomes alternativos e a carga falha se mais de 0,5% dos nomes não for resolvido (REQ-62).
  - − O endereço de uma entidade privada não prova onde o dinheiro foi aplicado; por isso ela não entra no resumo.
  - Opção 1 descartada pelos números acima. Opção 2 descartada: atribuiria a João Pessoa o que uma construtora sediada lá recebeu por obra em outro município.
