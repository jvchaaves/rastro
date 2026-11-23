# ADR-0004 · Entrar pela cidade, ter perfil de cada autor e nunca ranquear autores

- **Status:** aceita. Revista em 27/10/2026: o perfil do autor saiu de "atrás de flag" e entrou no MVP, a pedido da autora do projeto.
- **Contexto:** É ano eleitoral. Qualquer critério de "desempenho" de parlamentar seria do Rastro, não dos dados, e seria lido como posicionamento. A pergunta natural do morador é "o que veio para a minha cidade". Mas o morador também chega pelo anúncio de um parlamentar, e o jornalista precisa ver o conjunto do que cada autor indicou. A T1-b mostrou ainda que a mesma pessoa pode aparecer com dois códigos de autor (ex.: mudou de deputado para senador).
- **Opções consideradas:**
  1. Página inicial com ranking de autores por valor.
  2. Só a entrada pela cidade, com perfil do autor atrás de uma flag, fora do MVP (decisão anterior).
  3. Entrada principal pela cidade **e** perfil de cada autor no MVP: lista de autores em ordem alfabética, sem valores (A15); perfil com agregados por município em ordem alfabética (A09); nenhuma ordenação por valor; um perfil por código de autor, com link entre códigos de mesmo nome (REQ-81).
- **Decisão:** Opção 3. Vocabulário: "autor da emenda" ou "parlamentar", nunca "candidato" (REQ-27). Nenhuma lista ordena ou compara autores por valor (REQ-28). A lista de autores não mostra números (REQ-80), pelo mesmo motivo da lista de municípios.
- **Consequências:**
  - \+ Quem chega pelo anúncio de um parlamentar consegue conferir o que ele indicou e o que foi pago.
  - \+ O eixo da navegação continua sendo a cidade (A01 → A03); o perfil é um destino, não um placar.
  - \+ Não juntar códigos automaticamente evita misturar homônimos.
  - − Um perfil pode ser lido como "boletim" mesmo sem ranking. Mitigação: nota fixa "não é uma avaliação", ordem alfabética, sem cores de alerta.
  - − A mesma pessoa pode ter dois perfis; o link entre eles depende do nome normalizado.
  - Opção 1 descartada pelo contexto. Opção 2 descartada pela autora: o perfil é importante para o uso real.
