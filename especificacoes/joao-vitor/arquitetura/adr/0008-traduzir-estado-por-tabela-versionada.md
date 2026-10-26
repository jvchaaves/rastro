# ADR-0008 · Traduzir o estado de execução por uma tabela versionada no banco, nunca por regra no código

- **Status:** aceita (atende ao brief do grupo: "A tradução de fase é tabela versionada e auditável, nunca regra escondida no código")
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-69, REQ-70, REQ-86, REQ-67

## Contexto

- O morador não entende "empenhado", "liquidado" e "pago" (brief, "O problema").
- Uma tradução errada pode fazer o sistema afirmar que um parlamentar deixou de executar algo que executou. O risco do Rastro é de **atribuição**, não de privacidade (brief, "Dados e privacidade").
- Por isso, quem lê um texto simples precisa conseguir conferir qual regra o produziu e desde quando ela vale, mesmo depois de o texto mudar.
- O estado em si já é derivado da etapa mais avançada (ADR-0006). Falta decidir onde fica o **texto** que o traduz.

## Opções consideradas

1. **Textos no código do painel** (um dicionário em TypeScript): simples, mas a mudança some no histórico do Git, a API não devolve o texto e um cliente da API pode traduzir de outro jeito.
2. **Textos num arquivo de configuração da API**, recarregado na inicialização: a API devolve o texto, mas não há registro de qual versão estava valendo quando um alerta ou uma resposta foi produzida.
3. **Tabela `TabelaTraducao` no banco, só com inserção**, uma linha por (versão, estado), publicada por um comando da CLI, e devolvida pela API com o número da versão.

## Decisão

Opção 3.

- A versão 1 é carregada na migração inicial (textos em `../contratos/modelo-de-dados.md`).
- Uma versão nova só entra por `rastro traducao publicar` (`../contratos/cli.md`), que exige os quatro estados (REQ-86) e grava `versao = máxima + 1`.
- Gatilhos `BEFORE UPDATE` e `BEFORE DELETE` impedem alterar ou apagar uma versão publicada (REQ-70).
- Toda resposta com `estado_execucao` traz `estado_texto` e `traducao_versao` (REQ-69). `GET /api/traducoes` (`listar_traducoes`) devolve todas as versões, e a tela P09 as mostra.
- O dono é o módulo `nucleo`, o mesmo que deriva o estado consolidado (brief, tabela de módulos).

## Consequências

- **(+)** Auditável: uma captura de tela com "A entrega foi conferida; falta pagar (tradução v1)" pode ser conferida a qualquer momento.
- **(+)** O painel, a API e qualquer cliente de jornalista mostram o mesmo texto.
- **(+)** Corrigir uma tradução não exige deploy; exige um comando registrado, com nota de motivo.
- **(−)** Uma junção a mais em cada resposta com estado. O custo é baixo (4 linhas na versão vigente, mantidas em memória pela API) e está dentro do orçamento do REQ-49.
- **(−)** Respostas antigas guardadas por terceiros podem ter um texto diferente do atual. O campo `traducao_versao` resolve a dúvida.
