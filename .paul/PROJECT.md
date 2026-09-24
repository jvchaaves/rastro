# Rastro — contexto do projeto

**Modo de trabalho:** adaptação manual do ciclo Plan–Apply–Unify no Codex. Este arquivo foi preparado a partir do [FI-01](../FI-01.md) e do [brief fornecido](../docs/references/brief.md); não foi produzido pelo comando `/paul:init`.

## Propósito

Permitir que cidadãos, jornalistas e organizações de controle social acompanhem registros públicos de emendas parlamentares federais, da autoria e classificação aos valores de execução e aos favorecidos, com proveniência visível.

## Problema

O acompanhamento de uma emenda exige interpretar etapas e registros distintos. Uma apresentação que confunda destinação prevista, empenho, liquidação, pagamento e aplicação final pode atribuir incorretamente valores e responsabilidades.

## Público

- Cidadãos que consultam emendas e localidades.
- Jornalistas e pesquisadores que filtram, comparam e conferem fontes.
- Organizações de controle social que acompanham mudanças e alertas.
- Operador de dados responsável pela importação e publicação de lotes.

## MVP proposto no brief

1. Ingerir e normalizar dados de emendas da CGU e avaliar uma segunda fonte do Siga Brasil.
2. Expor API e painel com agregações por parlamentar, UF e função.
3. Permitir assinaturas com alerta por limiar cruzado ou mudança de execução.
4. Sincronizar fontes sem mostrar versões parciais e distribuir alertas sem duplicação.
5. Medir latência de consultas, duração de ETL e indexação.

O objetivo de caber em 60 horas vem do brief. A viabilidade da segunda fonte e o canal de alerta ainda precisam de decisão explícita; esses itens não podem ser removidos do MVP sem revisão do escopo pelo solicitante.

## Regras de interpretação dos dados

- Cada valor exibido deve ter fonte, lote e data de referência.
- Pagamento ao favorecido não demonstra a aplicação final do recurso.
- Localidade de aplicação do recurso e localidade do favorecido são campos diferentes.
- Autoria e apoio parlamentar são relações diferentes; não atribuir o total de uma emenda a um apoiador sem evidência específica.
- Códigos ausentes ou `Sem informação` não formam chaves de junção.
- Falta de registro de favorecido no lote não deve ser apresentada como prova de falta de pagamento.
- O sistema não classifica fraudes ou irregularidades.

## Fontes e evidência inicial

- [CGU — download de emendas](https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares): ZIP oficial inspecionado em 24/09/2026; detalhes e contagens em [pesquisa de fontes](../docs/research/fontes-2026-09-24.md).
- [Siga Brasil — Senado](https://www12.senado.leg.br/orcamento/sigabrasil): painéis e relatórios públicos confirmados; extração automatizada e chave de vínculo com a CGU ainda não confirmadas.

## Propostas técnicas ainda não confirmadas pelo estudante

- Recorte inicial: emendas de 2025 com código válido, incluindo os pagamentos relacionados disponíveis até o lote publicado.
- Stack: Python, FastAPI, SQLite, HTML renderizado no servidor e pytest. Domínio do estudante nessas tecnologias não foi informado.
- Canal inicial de alerta: dentro do painel, sem envio de mensagens externas.

## Fora de escopo

- Conclusões sobre fraude, legalidade ou impacto final de políticas públicas.
- Emendas estaduais ou municipais no primeiro MVP.
- Cobertura de todos os exercícios históricos desde a primeira versão.
- Múltiplos canais de entrega de alerta sem necessidade demonstrada.

## Decisões pendentes antes do plano de implementação

1. Confirmação da stack proposta e domínio real do estudante em cada tecnologia.
2. Confirmação do recorte proposto por ano da emenda 2025.
3. Forma reproduzível de extrair dados do Siga Brasil e regra de vinculação com a CGU.
4. Confirmação de alerta dentro do painel e mecanismo mínimo de identidade da assinatura.
5. Política de exposição de favorecidos que sejam pessoas físicas.
6. Definição operacional de “mudança de status de execução” baseada em campos oficiais ou comparação entre lotes.

Essas lacunas permanecem explícitas no FI-01 e não autorizam o modelo a inventar decisões em tarefas futuras.
