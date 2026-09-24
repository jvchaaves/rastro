# Rastro

Para onde vão as emendas parlamentares.

Transcrição do material visual fornecido para a ideação do projeto.

## Problema

Opacidade no uso de emendas: o cidadão não consegue acompanhar o caminho do dinheiro, da indicação ao pagamento.

Usuários: cidadão, jornalista e controle social.

## MVP descrito

- Ingerir e normalizar dados de emendas.
- Oferecer API e painel com agregação por parlamentar, UF e função.
- Permitir assinatura com alerta quando um limiar é cruzado ou o status de execução muda.

## Concorrência

Sincronização periódica concorrente de múltiplas fontes e distribuição de alertas para assinantes.

## Desempenho

Agregações sobre base grande, com milhares de registros. Medir latência de consulta, tempo de ETL e indexação.

## Dados

Portal da Transparência / CGU: arquivos CSV com dicionário de dados. Siga Brasil / Senado: dados de execução orçamentária.

## Viabilidade e riscos registrados

MVP proposto para 60 horas. Riscos: volume e limpeza dos CSVs; consulta web limitada; atribuição incorreta de recursos. Mostrar a proveniência dos dados.
