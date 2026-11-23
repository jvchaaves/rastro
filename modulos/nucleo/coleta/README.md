# Coleta de mudanças entre lotes — Trabalho 2, João Vitor

Etapa 1: coleta e normalização, sem modelo de linguagem. Fonte, licença e recorte estão em [FONTE.md](FONTE.md); as regras, com o item que motivou cada uma e quantos itens afetou, em [REGRAS.md](REGRAS.md).

## Como rodar

```sh
python3 coletor.py            # recalcula corpus.jsonl, descartes.jsonl e REGRAS.md a partir de bruto/ (sem rede)
python3 coletor.py --baixar   # pede à CGU o lote vigente (requisição condicional) e, se for novo, guarda em bruto/
```

Só biblioteca padrão do Python 3.10 ou mais novo. Leva uns 5 segundos.

**Reprodução:** apagar `corpus.jsonl`, `descartes.jsonl` e `REGRAS.md` e rodar `python3 coletor.py` gera arquivos idênticos byte a byte. Rodar duas vezes também: os arquivos são reescritos inteiros, em ordem estável, e a chave de cada item não se repete.

## Arquivos

| Arquivo | O que é |
| :-- | :-- |
| `coletor.py` | O coletor. As cinco funções do esqueleto têm o nome do passo: `obter`, `extrair`, `normalizar`, `deduplicar`, `gravar`; `comparar` pareia dois lotes (passo 3b). `conferir_exemplos` confere, a cada execução, o item do bruto citado em cada regra |
| `bruto/AAAA-MM-DD_EmendasParlamentares.csv.gz` | O CSV de cada lote, byte a byte como veio no ZIP da CGU, comprimido com gzip determinístico. A data é a de referência do lote |
| `bruto/lotes.json` | Manifesto dos lotes: URL, data de referência, data da coleta, cabeçalhos HTTP, SHA-256 do ZIP original e do CSV, lista de arquivos do ZIP |
| `corpus.jsonl` | Uma mudança por linha (esquema abaixo) |
| `descartes.jsonl` | Uma linha por registro que não entrou, com `fonte`, `codigo`, `motivo` e `detalhe` |
| `REGRAS.md` | Gerado pelo coletor: uma regra por linha, com o item do bruto que a motivou e a contagem da última execução |

O ZIP original (32 MB e 47 MB) não vai para o repositório: só o arquivo usado, `EmendasParlamentares.csv`. O SHA-256 do ZIP fica no manifesto, para conferir a origem, e o aluno guarda os dois ZIPs fora do repositório.

`.gitattributes` fixa o fim de linha em LF, para a comparação byte a byte valer também no Windows.

## Vocabulário

Os nomes dos campos vêm do modelo de dados do Trabalho 1 do aluno (`especificacoes/joao-vitor/arquitetura/contratos/modelo-de-dados.md`, na branch `trabalho1/joao-vitor`): `Emenda.*`, as etapas de `RegistroExecucao`, `MudancaLote.tipo` e o estado de execução do REQ-105 (`especificacoes/joao-vitor/arquitetura/requisitos.md`). O `CONTRATOS.md` do grupo ainda não existe; quando existir, o esquema segue os nomes dele.

## Esquema do `corpus.jsonl`

```json
{"id": "rastro-mud-20261119-202612460001",
 "texto": "Emenda 202612460001 (2026), de JULIO CESAR, … Entre o lote de 26/10/2026 e o de 19/11/2026: Valor Liquidado passou de R$ 7.004.128,57 para R$ 11.044.500,00 (+R$ 4.040.371,43); …",
 "campos": {"codigo_emenda": "202612460001", "lote_anterior": "2026-10-26", "lote_novo": "2026-11-19",
            "presenca": "alterada",
            "alteracoes": [{"campo": "liquidado_centavos", "antes": 700412857, "depois": 1104450000, "diferenca_centavos": 404037143}, …],
            "estado_antes": "paga_em_parte", "estado_depois": "paga",
            "mudancas_lote": [{"tipo": "valor_alterado", "etapa": "liquidado"}, {"tipo": "valor_alterado", "etapa": "pago"}, {"tipo": "estado_alterado", "etapa": null}],
            "emenda": {"codigo": "202612460001", "ano": 2026, "tipo": "…", "autor_codigo": "…", "autor_nome": "JULIO CESAR", "possui_apoiador": null, "localidade_gasto": "MÚLTIPLO", "uf_gasto": "PI", "municipio_ibge": null, "…": "…", "empenhado_centavos": 1104450000, "…": "…"},
            "fonte_anterior": "bruto/2026-10-26_EmendasParlamentares.csv.gz:92065"},
 "fonte": "bruto/2026-11-19_EmendasParlamentares.csv.gz:92156",
 "coletado_em": "2026-11-23",
 "chave": "<SHA-256 de codigo|lote_anterior|lote_novo>"}
```

| Campo | Significado |
| :-- | :-- |
| `texto` | A mudança escrita por regra fixa, com os rótulos da CGU. É o que a Etapa 2 vai julgar |
| `campos.presenca` | `alterada` (nos dois lotes, com algum campo diferente), `nova` (só no lote novo) ou `removida` (só no anterior) |
| `campos.alteracoes` | Campos diferentes, com o valor normalizado antes e depois. Em valor, também `diferenca_centavos`; em texto, também `antes_cgu` e `depois_cgu`, o texto original, porque dois valores originais diferentes podem virar o mesmo nulo ("Sem informação" → "Múltiplo", R19). Vazio em `nova` e `removida` |
| `campos.estado_antes` / `estado_depois` | Estado de execução pela regra do REQ-105 do Trabalho 1; nulo do lado em que a emenda não existe |
| `campos.mudancas_lote` | As linhas de `MudancaLote` do modelo do Trabalho 1 que a mudança gera: `nova_emenda`, `valor_alterado` com a `etapa`, `estado_alterado`. Emenda removida e troca de local não têm tipo naquele modelo, e a lista fica sem elas |
| `campos.emenda` | O registro normalizado do lote novo (ou do anterior, se removida), com os nomes do modelo de dados do Trabalho 1 (`Emenda.*` e etapas de `RegistroExecucao` em centavos). Todo registro tem os 29 campos; `possui_apoiador` é nulo no lote que não tem a coluna |
| `fonte` / `campos.fonte_anterior` | Arquivo em `bruto/` e linha do CSV descomprimido (a linha 1 é o cabeçalho), em cada lote: a proveniência por registro do recorte. Para conferir: `gzip -dc bruto/2026-11-19_EmendasParlamentares.csv.gz \| sed -n 92156p` |
| `coletado_em` | Data em que foi baixado o lote citado em `fonte` |
| `chave` | Hash da deduplicação |
