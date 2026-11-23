# ADR-0005 · Separar a rotina de carga em contêiner próprio, com lock consultivo

- **Status:** aceita
- **Contexto:** A aplicação web roda com vários workers Uvicorn. Um agendador dentro da aplicação dispararia uma carga por worker. Duas cargas simultâneas criariam duas versões concorrentes (REQ-36). A coleta baixa e processa um zip de 32 MB (230 MB descompactados) uma vez por dia (ADR-0007).
- **Opções consideradas:**
  1. Agendador (APScheduler) dentro do processo web.
  2. `cron` do sistema operacional do host chamando o comando.
  3. Serviço `carga` separado no Docker Compose, mesmo pacote Python, com APScheduler + `pg_try_advisory_lock`.
- **Decisão:** Opção 3. A coleta fica isolada em `fonte_portal.py` (adaptador), o que permite trocar a fonte (SIGA) ou carregar um `--arquivo` local. A leitura é em streaming, para não carregar os 183 MB do CSV de favorecidos na memória.
- **Consequências:**
  - \+ Uma única carga por vez, garantida pelo banco, mesmo se alguém disparar manualmente (Q3).
  - \+ Falha ou consumo de memória da carga não derruba o web.
  - \+ Portável: não depende do cron do host (hospedagem indefinida).
  - − Mais um contêiner para operar.
  - Opção 1 descartada: N workers = N cargas. Opção 2 descartada: amarra a hospedagem e fica fora do compose.
