# Rotas HTML — páginas e fragmentos

As telas são HTML montado no servidor (Jinja) e atualizadas por fragmentos (HTMX), conforme ADR-0001. Cada rota chama **a mesma função de serviço** da operação OpenAPI indicada; a rota HTML só muda a forma de apresentar. Assim, toda ação de tela aponta para uma operação do contrato (`openapi.yaml`).

Regras comuns:
- Toda rota de página aceita os mesmos parâmetros de consulta que a operação correspondente (REQ-12, REQ-41).
- Requisições com cabeçalho `HX-Request: true` recebem só o fragmento; sem ele, a página inteira (REQ-41).
- Erros: 404 → A12; 500 → A12 com código de referência; sem versão ativa → estado "dados ainda não carregados" (REQ-39).
- Listas paginadas sempre devolvem `versao` e os links de página a repetem (REQ-12). Uma `versao` indisponível gera 303 para a URL sem ela (REQ-63).

| Rota | Tipo | Tela | Operação de serviço |
|---|---|---|---|
| `GET /` | página | A01 | — (estática + `obter_versao_ativa` no rodapé) |
| `GET /fragmentos/sugestoes?q=` | fragmento | A01 | `listar_municipios`; com 12 dígitos, `buscar_emendas_por_codigo` (REQ-69) |
| `GET /buscar?q=` | página (sem JS) | A01 | `listar_municipios` (1 resultado exato → 303 para A03) ou, com 12 dígitos, `buscar_emendas_por_codigo` (1 emenda → 303 para A05) |
| `GET /municipios` | página | A02 | `listar_municipios` (sem `q`) |
| `GET /municipios/{codigo_ibge}?ano=` | página | A03 | `obter_municipio` |
| `GET /municipios/{codigo_ibge}/emendas?funcao=&ano=&fase=&sem_pagamento_antigo=&pagina=&versao=` | página | A04 | `listar_emendas_municipio` |
| `GET /fragmentos/municipios/{codigo_ibge}/emendas?funcao=&ano=&fase=&sem_pagamento_antigo=&pagina=&versao=` | fragmento | A04 | `listar_emendas_municipio` |
| `GET /municipios/{codigo_ibge}/recebidos?ano=&pagina=&versao=` | página | A14 | `listar_recebidos_municipio` |
| `GET /fragmentos/municipios/{codigo_ibge}/recebidos?ano=&pagina=&versao=` | fragmento | A14 | `listar_recebidos_municipio` |
| `GET /emendas/{id_emenda}` | página (com `og:title`/`og:description`, REQ-68) | A05 | `obter_emenda` |
| `GET /termos/{slug}` | página | A06 | `obter_termo` |
| `GET /fragmentos/termos/{slug}` | fragmento (painel) | A06 | `obter_termo` |
| `GET /termos` | página | A07 | `listar_termos` |
| `GET /sem-municipio?funcao=&abrangencia=&ano=&fase=&pagina=&versao=` | página | A08 | `listar_emendas_sem_municipio` |
| `GET /fragmentos/sem-municipio?funcao=&abrangencia=&ano=&fase=&pagina=&versao=` | fragmento | A08 | `listar_emendas_sem_municipio` |
| `GET /autores` | página | A15 | `listar_autores` |
| `GET /autores/{autor_id}` | página | A09 | `obter_autor` |
| `GET /sobre/dados` | página | A10 | `obter_versao_ativa`, `listar_verificacoes` |
| `GET /sobre` | página | A11 | — (estática) |
| (qualquer rota inexistente / erro) | página | A12 | — |
| `GET /emendas/{id_emenda}/citar` | página | A13 | `obter_citacao_emenda` |
| `GET /static/*` | arquivos | — | Pico.css e htmx servidos localmente, com cache longo |
