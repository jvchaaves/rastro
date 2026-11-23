# ADR-0007 · Coletar do arquivo único de dados abertos, com requisição condicional pelo ETag

- **Status:** aceita (27/10/2026, T1)
- **Contexto:** O FI-01 deixou em aberto se a coleta seria por CSV ou por API com chave, e com que frequência (§12). Na T1:
  - o Portal publica um **zip único e cumulativo** (2014–2026, 32,5 MB, três CSVs) num bucket S3/CloudFront, sem autenticação;
  - o arquivo tem `ETag` e `Last-Modified`, este último atualizado diariamente;
  - a página do Portal usa um desafio anti-robô (AWS WAF), mas o arquivo em si não.
  - A API exige chave (cadastro gov.br) e é paginada por consulta.
- **Opções consideradas:**
  1. API de dados com chave, paginando por município e ano.
  2. Raspar a página de consulta do Portal.
  3. Baixar o zip único, com `GET` condicional (`If-None-Match`), e processar em streaming.
  4. SIGA Brasil como fonte principal.
- **Decisão:** Opção 3, nos termos de `contratos/fonte-portal.md` e `contratos/carga.md`. A carga roda diariamente, mas só cria versão quando o `ETag` muda (REQ-49). A URL do arquivo fica em configuração (`FONTE_URL`), não no código.
- **Consequências:**
  - \+ Sem chave, sem limite de requisições, um download por dia no máximo.
  - \+ Mesmo arquivo para todos os anos: a escolha de anos vira filtro de tela, não de coleta (todos os anos de 2014 em diante entram).
  - \+ O histórico de verificações dá a frequência real da fonte (A10).
  - − Se o Portal mudar a URL ou o layout, a carga falha. Mitigação: validação rígida (REQ-48), versão anterior no ar (REQ-35) e alerta (REQ-51).
  - − Baixar 32 MB por dia, mesmo para poucas mudanças. Aceito: o `304` evita o download quando nada mudou.
  - A contingência continua sendo o SIGA Brasil, mas exige um adaptador próprio. Não entra no MVP.
  - Ponto a confirmar na implantação: acesso ao arquivo a partir do servidor de hospedagem. A T1 baixou o arquivo pelo navegador; o ambiente de nuvem usado na análise bloqueava o domínio.
