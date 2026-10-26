# ADR-0004 · Calcular MudancaLote na publicação e gerar alertas idempotentes por (assinatura, mudança)

- **Status:** aceita
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-08, REQ-24, REQ-35, REQ-36, REQ-37

## Contexto

Duas funcionalidades dependem de "o que mudou entre dois lotes": a tela "o que mudou" (P08) e os alertas (S05). A linha do tempo (P04) lê os valores de `RegistroExecucao` lote a lote (ADR-0001) e não depende desta decisão.

Há também duas exigências sobre os alertas:

- O brief pede fan-out de alertas sob concorrência, e o FI-01 exige "no máximo um alerta por mudança e assinatura".
- Uma publicação reexecutada, ou duas avaliações em paralelo, não podem duplicar alertas.

## Opções consideradas

1. **Calcular a diferença sob demanda** em cada consulta e, para alertas, comparar com um "último valor visto" por assinatura.
2. **Gatilhos (triggers) SQLite** que gravam mudanças a cada upsert.
3. **Materializar `MudancaLote` na transação de publicação e derivar os alertas dela**, com UNIQUE(`assinatura_id`, `mudanca_id`).

## Decisão

Opção 3.

- A diferença é calculada com SQL (junção do lote novo com o anterior por `codigo_emenda` e `etapa`) dentro da transação de publicação. Assim, nenhum leitor vê um lote ativo sem as suas mudanças.
- Depois do commit, o despachante faz o seguinte:
  1. Carrega as assinaturas `ativa` com `lote_base_id` < lote novo.
  2. Avalia em paralelo (`ThreadPoolExecutor`).
  3. Grava `Alerta` com `INSERT … ON CONFLICT(assinatura_id, mudanca_id) DO NOTHING`.
- O evento e o resumo estão em `../contratos/eventos.asyncapi.yaml`.

## Consequências

- **(+)** P08 e os alertas usam a mesma tabela. O que o assinante recebe é exatamente o que a tela P08 mostra.
- **(+)** A idempotência é garantida pelo banco, não pela lógica: reprocessar um lote produz `alertas_criados = 0`.
- **(+)** A avaliação paralela é segura porque a única escrita é idempotente.
- **(−)** A publicação fica mais lenta, porque a diferença entra no tempo de publicação. Ela é medida em `duracao_etl_ms.publicacao` (REQ-50).
- **(−)** Se o despachante cair depois do commit, os alertas atrasam até `rastro publicar --reprocessar-alertas` (ou a próxima sincronização). Nada é perdido nem duplicado.
