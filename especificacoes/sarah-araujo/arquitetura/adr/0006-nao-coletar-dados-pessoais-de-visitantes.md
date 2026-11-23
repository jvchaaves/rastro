# ADR-0006 · Não coletar dados pessoais de visitantes

- **Status:** aceita (FI-01 §5; LGPD — Lei 13.709/2018)
- **Contexto:** Nenhuma feature precisa saber quem é o usuário. Os dados exibidos (autor, valores) são públicos por obrigação legal e se referem a agentes públicos no exercício da função. O único dado pessoal possível de visitante é o IP nos logs. Na fonte, o único dado pessoal fora de agentes públicos é o favorecido pessoa física.
- **Opções consideradas:**
  1. Analytics de terceiros para medir uso.
  2. Contas opcionais para favoritos.
  3. Nenhuma coleta: sem cookies, sem analytics, IP truncado nos logs, retenção de 30 dias.
- **Decisão:** Opção 3 (REQ-01, REQ-02). Além disso, a tabela de favorecidos da fonte (T1) traz pagamentos a pessoas físicas, com CPF mascarado e nome. A carga não grava nome nem código de pessoa física e exibe só "Pessoa física" (REQ-53). O uso é medido só por contagens agregadas de requisições por rota, a partir dos logs anonimizados.
- **Consequências:**
  - \+ Sem base legal a justificar, sem banner de consentimento, sem incidente de vazamento de dado de visitante.
  - \+ Consulta sem medo de ser identificado (relevante em cidade pequena e em ano eleitoral).
  - − Sem dados de comportamento para melhorar a interface; a validação de compreensão é feita com o teste de 5 pessoas (FI §10.1).
