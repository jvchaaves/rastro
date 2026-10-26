# ADR-0007 · Exibir favorecido pessoa física como publicado pela CGU, sem busca por pessoa

- **Status:** aceita (fecha a lacuna "exibição de favorecidos pessoas físicas" do FI-01 §12)
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-25, REQ-26, REQ-15

## Contexto

O arquivo por favorecido da CGU inclui pessoas físicas, com nome e CPF já mascarado (`***.123.456-**`). O FI-01 §3.2 registra que:

- a publicação na origem não equivale a consentimento para uma nova apresentação;
- mostrar recebimento pode ser lido como irregularidade.

Por outro lado, a transparência é o objetivo do produto, e esconder favorecidos esconderia parte do caminho do dinheiro.

## Opções consideradas

1. **Nome completo e identificador como na fonte, com busca por nome:** máxima transparência e máxima exposição. Transforma o Rastro num buscador de pessoas.
2. **Agregar pessoas físicas sem nome** ("Pessoas físicas: N favorecidos, R$ X"): menor exposição, mas perde a verificabilidade contra a fonte.
3. **Exibir como a CGU publica, só no contexto de uma emenda**, sem busca, filtro, ordenação ou página por pessoa física, e com aviso fixo.

## Decisão

Opção 3.

- O favorecido PF aparece apenas na lista de favorecidos de uma emenda (P05), com `nome_publicavel` e `codigo_origem` exatamente como na fonte.
- O Rastro não reconstrói, não completa e não cruza o CPF.
- `listar_emendas` (`q`) e `listar_opcoes_filtro` não indexam favorecidos.
- Toda lista de favorecidos traz o aviso do REQ-26.

## Consequências

- **(+)** Tudo que é mostrado pode ser conferido no download oficial, e o Rastro não amplia a exposição além da fonte.
- **(+)** Não se pode responder "quanto a pessoa X recebeu de emendas" pelo Rastro. Isso é intencional.
- **(−)** Pesquisadores que precisem desse corte devem usar o download oficial da CGU, e a tela D01 indica isso.
- **(−)** Se a CGU mudar o mascaramento, a regra precisa ser revista. Um teste de contrato verifica o padrão mascarado no lote.
