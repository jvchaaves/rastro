# ADR-0010 · Mostrar na página do município o gasto previsto e o recebido na cidade, em blocos separados e sem somar

- **Status:** aceita
- **Data:** 27/10/2026
- **Requisitos ligados:** REQ-67, REQ-107, REQ-108, REQ-109, REQ-110, REQ-111, REQ-112, REQ-21

## Contexto

- O brief põe o município no centro: o morador quer saber "o que foi destinado à cidade dele", e o gestor municipal quer ver o que foi empenhado e ainda não chegou.
- A P10 foi especificada só com o **local do gasto**, a coluna "Código Município IBGE" do arquivo de emendas (REQ-66). O REQ-21 proíbe derivar o local do gasto do endereço do favorecido, porque uma empresa de outra cidade pode executar a obra.
- A conferência com o arquivo real da CGU (dados de 26/10/2026, emendas de 2025) mostrou que essa escolha, sozinha, deixa a página vazia para quase todo o país:
  - só 759 das 6 310 emendas trazem um município como local do gasto; as demais são de várias cidades ("Múltiplo"), da UF inteira ou nacionais;
  - por isso, só **474 municípios** aparecem como local do gasto;
  - favorecidos sediados em **5 545 municípios** receberam dinheiro dessas emendas (arquivo por favorecido, colunas "UF Favorecido" e "Município Favorecido");
  - em João Pessoa, 17 emendas (R$ 14,2 milhões empenhados) têm a cidade como local do gasto, mas 84 emendas pagaram R$ 143,3 milhões a 53 favorecidos sediados nela (sem contar pessoas físicas), dos quais R$ 37,7 milhões, de 26 emendas, a órgãos municipais (prefeitura e fundos municipais).
- Os nomes de município dos dois arquivos coincidem: os 474 municípios do local do gasto aparecem, com a mesma grafia e a mesma sigla de UF, no arquivo por favorecido.

## Opções consideradas

1. **Manter só o local do gasto.**
   - Prós: um único conceito, sem risco de confusão. Contras: 91% dos municípios com dinheiro de emendas teriam página vazia (404), e o morador concluiria que nada chegou à cidade. **Descartada** porque contraria o objetivo central do brief.
2. **Somar o recebido pelos favorecidos da cidade ao gasto previsto.**
   - Prós: um número só. Contras: mistura duas grandezas (valor da emenda por etapa e valor recebido por favorecido, que já são distintas na P03 e na P05), conta duas vezes a mesma emenda e atribui à cidade o pagamento a uma empresa sediada nela por uma obra feita em outro lugar. **Descartada** porque fere o REQ-21 e o REQ-77.
3. **Dois blocos separados e rotulados:** "Emendas com gasto previsto nesta cidade" (local do gasto, como antes) e "Recebido por favorecidos sediados nesta cidade" (arquivo por favorecido), com a parte recebida por órgãos municipais em destaque e sem total entre os dois.
   - Prós: a página existe para os 5 545 municípios; cada número diz de onde vem. Contras: dois números que o morador precisa entender como distintos; mais uma coluna derivada na importação.

## Decisão

Opção 3, porque é a única que mostra o que chegou à cidade sem afirmar onde o dinheiro foi gasto.

- O favorecido ganha `municipio_sede`, derivado de "Município Favorecido" pela mesma regra de `Emenda.municipio_gasto` (REQ-107), e `orgao_municipal`, derivado da "Natureza Jurídica" (REQ-109). Sem UF válida ou com "Sem informação", a sede fica nula (REQ-108).
- O catálogo de municípios (`OpcoesFiltro.municipios`) passa a ser a união do local do gasto e da sede dos favorecidos, com `quantidade_emendas_gasto` em cada item (REQ-112). O 404 de `obter_municipio` fica só para município fora desse catálogo (REQ-55).
- `obter_municipio` devolve `recebido_na_cidade` ao lado dos valores do gasto previsto (REQ-110), e nenhuma tela ou resposta soma os dois (REQ-111).
- O identificador continua `municipio_gasto` na rota e nos filtros, para não mudar a rota: é o mesmo texto para os dois usos (`joao-pessoa`).
- O contrato HTTP sobe de 0.2.0 para 0.3.0: há campos obrigatórios novos (`recebido_na_cidade`, `quantidade_emendas_gasto`) e um valor novo no enum de estado (ADR-0006).
- Assinaturas por município só aceitam municípios com gasto previsto (`quantidade_emendas_gasto` > 0), e a P10 só oferece "Acompanhar este município" nesse caso, porque o filtro olha o local do gasto.
- Pessoas físicas ficam fora do recebido na cidade, porque o agregado delas não guarda a cidade (ADR-0007). No arquivo conferido, elas somam 0,05% do valor recebido.

## Consequências

- **(+)** A P10 deixa de ser vazia para 91% dos municípios, e o gestor vê quanto a prefeitura e os fundos municipais receberam.
- **(+)** O REQ-21 continua valendo: o local do gasto nunca vem do favorecido; o favorecido só alimenta o bloco próprio.
- **(−)** O recebido na cidade inclui pagamentos a empresas sediadas ali por obras feitas em outros municípios. O rótulo e a nota da P10 dizem isso, e o número nunca é chamado de "gasto na cidade".
- **(−)** As assinaturas por município (`filtro_municipio_gasto`) continuam olhando só o local do gasto: um recebimento novo na cidade não gera alerta, e municípios só com recebimentos não podem ser assinados. Estender as assinaturas ao recebido é trabalho de uma fatia futura.
- **(−)** Um favorecido que mude de sede entre lotes fica com a sede do primeiro lote em que apareceu, porque `Favorecido` é uma dimensão só com inserção.
