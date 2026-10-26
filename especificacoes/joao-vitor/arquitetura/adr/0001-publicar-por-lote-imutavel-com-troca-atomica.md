# ADR-0001 · Publicar dados por lote imutável com troca atômica do lote ativo

- **Status:** aceita
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-05, REQ-06, REQ-07, REQ-09, REQ-10, REQ-14

## Contexto

- O pacote da CGU é substituído inteiro a cada atualização e pode mudar sem aviso (FI-01 §10.3).
- A regra de confiança do brief exige que todo valor exibido aponte para a sua origem.
- Uma consulta feita durante uma atualização não pode misturar dados de duas versões (FI-01 §10.1, AC-3).
- A funcionalidade de linha do tempo precisa dos valores antigos, então atualizar linha a linha apagaria a história.

## Opções consideradas

1. **Upsert linha a linha** na tabela de emendas, guardando a "última versão".
   - Prós: simples e com pouco espaço em disco. Contras: um leitor vê o lote pela metade durante a gravação e o histórico se perde. **Descartada** porque quebra a linha do tempo (REQ-23) e a consistência sob atualização.
2. **Duas bases (azul/verde)** com troca de arquivo do SQLite.
   - Prós: troca atômica do arquivo inteiro. Contras: copia a base a cada lote e invalida conexões abertas da API. **Descartada** porque a troca de arquivo não é atômica para leitores já conectados e não guarda o histórico entre lotes.
3. **Lote imutável:** cada importação grava as próprias linhas, marcadas com `lote_id`, e um ponteiro `PublicacaoAtiva` por fonte decide o que é visível.
   - Prós: troca atômica por um único `UPDATE`, histórico completo, reimportação idempotente por hash. Contras: o banco cresce a cada lote.

## Decisão

Opção 3, porque é a única que dá, ao mesmo tempo, publicação atômica para quem está lendo e o histórico de lotes de que a linha do tempo e o "o que mudou" precisam.

- Cada `LoteImportacao` é identificado pelo `hash_sha256` do arquivo e passa pelos estados `importando → validado → publicado → substituido`, ou termina em `recusado`/`falhou`.
- Publicar é **uma** transação que calcula as mudanças, troca `PublicacaoAtiva.lote_id` e marca o lote anterior como `substituido`.
- Um lote cujas rejeições por defeito passem de 5% das linhas do recorte (linhas lidas menos `ano_fora_do_recorte`) é recusado e não pode ser publicado (REQ-06).
- Lotes são publicados em ordem de `data_referencia`: um lote igual ou mais antigo que o ativo é recusado na publicação (REQ-95).

```mermaid
stateDiagram-v2
    [*] --> importando
    importando --> validado: leitura e validação ok
    importando --> recusado: rejeições > 5%
    importando --> falhou: formato alterado / interrompido / fonte indisponível
    validado --> publicado: rastro publicar (troca atômica)
    publicado --> substituido: outro lote publicado
```

## Consequências

- **(+)** A proveniência sai de graça: toda linha carrega `lote_id`, e daí vêm a fonte, o hash e a data.
- **(+)** A linha do tempo e o "o que mudou" são consultas sobre lotes, sem tabela de histórico à parte.
- **(+)** Reimportar o mesmo arquivo é um no-op detectável pelo hash (AC-2).
- **(+)** Um lote ruim nunca fica visível. O anterior continua publicado com a sua data.
- **(−)** O armazenamento cresce a cada lote, cerca de 150 mil linhas por lote CGU no recorte 2025. Mitigação: depois de N lotes, compactar os lotes `substituido` para guardar só `RegistroExecucao` (decisão futura).
- **(−)** Toda consulta precisa filtrar por `lote_id`, o que exige índices compostos começando por `lote_id`.
