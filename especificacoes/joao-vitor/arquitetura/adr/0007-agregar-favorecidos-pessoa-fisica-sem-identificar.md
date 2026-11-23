# ADR-0007 · Agregar os favorecidos pessoa física por emenda e mês, sem nome nem CPF

- **Status:** aceita (fecha a lacuna "exibição de favorecidos pessoas físicas" do FI-01 §12 e segue o brief do grupo)
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-25, REQ-26, REQ-65, REQ-15

## Contexto

- O arquivo por favorecido da CGU inclui pessoas físicas, com nome e CPF parcialmente mascarado (`***.123.456-**`).
- O FI-01 §3.2 registra que a publicação na origem não equivale a consentimento para uma nova apresentação e que mostrar recebimento pode ser lido como irregularidade.
- O brief do grupo define o dado do Rastro como "público e agregado, sem titular identificado" e diz que o risco a controlar é o de atribuição.
- Por outro lado, a transparência é o objetivo do produto: esconder os recebimentos esconderia parte do caminho do dinheiro.

## Opções consideradas

1. **Nome e identificador como na fonte, com busca por nome.**
   - Prós: máxima transparência. Contras: transforma o Rastro num buscador de pessoas. **Descartada** pela LGPD (minimização) e pelo brief.
2. **Nome e CPF mascarado como na fonte, só no contexto de uma emenda, sem busca.**
   - Prós: cada linha pode ser conferida contra a fonte. Contras: identifica o titular, o que contraria o brief ("sem titular identificado"). **Descartada** por isso.
3. **Agregar as pessoas físicas por emenda e mês** ("Pessoas físicas: N pessoas, R$ X"), mantendo identificados só pessoas jurídicas e entes públicos.
   - Prós: o valor total recebido continua visível e somável à conferência; nenhum titular pessoa física aparece. Contras: o jornalista não confere pessoa a pessoa no Rastro; precisa do download oficial.

## Decisão

Opção 3, porque é a única que mantém o caminho do dinheiro completo (o valor recebido por pessoas físicas aparece, somado) sem identificar titulares, como o brief exige.

- Na importação, as linhas de pessoa física de uma emenda e mês viram uma única linha `RegistroFavorecido` com `favorecido_id` nulo, a soma dos valores e a quantidade de pessoas distintas. O nome e o CPF mascarado são usados só para contar pessoas distintas e são descartados; não entram no banco.
- P05 mostra essa linha como "Pessoas físicas (N)", com o valor do mês.
- `listar_emendas` (`q`) e `listar_opcoes_filtro` não indexam favorecidos (REQ-65).
- Toda lista de favorecidos traz o aviso do REQ-26.

## Consequências

- **(+)** O Rastro não amplia a exposição de pessoas físicas além de um número e de uma soma, e não responde "quanto a pessoa X recebeu".
- **(+)** A soma por emenda continua igual à da fonte: a agregação não perde valor.
- **(−)** Quem precisar conferir pessoa a pessoa usa o download oficial da CGU; a tela D01 indica isso.
- **(−)** A contagem de pessoas distintas depende do par nome + CPF mascarado. Se a CGU mudar o mascaramento, a regra precisa ser revista; um teste de contrato verifica o padrão no lote.
