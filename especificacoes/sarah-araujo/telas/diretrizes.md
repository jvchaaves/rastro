# Diretrizes globais — Rastro

Valem para todas as telas. As fichas não repetem o que está aqui.

## Público
- **Morador de município da Paraíba** (persona principal): sem formação em orçamento público. Chega com uma pergunta concreta ("o que veio para a minha cidade?"), em geral a partir de uma notícia ou de um anúncio de parlamentar em rede social. Usa o celular, muitas vezes com 3G/4G fraco ou dados móveis limitados. Uso eventual: não vai aprender a interface.
- **Jornalista local** (persona secundária): usa as mesmas telas e fluxos, no celular ou no computador, de forma recorrente. Precisa citar com precisão e conferir na fonte original (A13, links para o Portal, API).
- Ator não humano, **rotina de carga**: não tem tela; seu trabalho aparece em A10 · Origem dos dados e no rodapé de todas as telas.

## Plataforma e orientação
- Web responsiva, **celular primeiro**, orientação retrato; largura de referência 360 px, mínimo 320 px sem rolagem horizontal.
- Desktop: a mesma tela, numa coluna central de até ~720 px. Nenhuma funcionalidade é exclusiva do desktop.
- Funciona sem JavaScript; com JS, o HTMX troca só partes da tela (REQ-41).
- Navegadores-alvo: Chrome Android e Safari iOS das duas últimas versões principais; Firefox e Chrome desktop.

## Tom de voz e de interface
- **Linguagem simples**, frases curtas, voz ativa, segunda pessoa ("sua cidade"). Termo técnico só ao lado de sua tradução, nunca sozinho.
- **Neutro e descritivo**: diz o que os dados registram, sem adjetivos de julgamento ("só", "apenas", "atrasada", "parada", "abandonada", "desvio"); a lista verificável está em REQ-77. Para reserva antiga sem pagamento, o texto é sempre "ainda sem pagamento".
- Diz **o que o dinheiro fez**, nunca o que a obra fez.
- Vocabulário fixo: "emenda", "autor da emenda", "parlamentar", "prefeitura", "fundo municipal", "dinheiro reservado/pago", "para quem foi pago". Nunca "candidato" (REQ-27).
- Mensagens de erro dizem o que aconteceu e o que fazer, sem culpar o usuário e sem jargão técnico.

## Princípios verificáveis
1. **Responder antes de explicar.** Toda tela de dados abre com uma frase em linguagem simples que responde à pergunta principal dela (manchete da cidade em A03, frase-resposta da emenda em A05); números, termos e listas vêm depois, como o porquê. *Verificação:* o primeiro parágrafo após o `h1` de A03 e A05 é a frase de REQ-65/REQ-64.
2. **Nenhum termo técnico sozinho.** Toda ocorrência de "empenhado", "liquidado", "pago", "restos a pagar" ou sigla na tela tem a tradução visível ao lado e o acesso a "O que isso quer dizer?" (A06), e toda tradução leva à sua fonte oficial em no máximo um toque (REQ-16). *Verificação:* teste de template que procura esses termos sem o componente de tradução + restrição de REQ-16.
3. **Dinheiro, nunca obra.** Nenhum texto afirma ou sugere execução física de obra ou serviço; a tela de detalhe traz o aviso de REQ-18. *Verificação:* lista de expressões proibidas (REQ-15) no CI.
4. **Sem julgamento sobre pessoas.** Nenhuma nota, ranking, medalha, cor de alerta ou ordenação por valor ligada a autor (REQ-28). *Verificação:* revisão de telas + teste de API de A09.
5. **Nunca esconder o que falta.** Toda tela de dados mostra a data da fonte (REQ-03) e, quando couber, o aviso de emendas sem município único (REQ-09), de verificação atrasada (REQ-38), de banco intermediário (REQ-60) e de transferência especial (REQ-61). Valores de registros diferentes nunca são somados num total único (REQ-55). *Verificação:* teste de template por tela.

## Referência visual
- **Inspira:** GOV.UK Design System (clareza, uma coisa por tela, linguagem simples); padrões de linguagem simples do gov.br; o visual padrão do Pico.css (tipografia legível, pouco ornamento); extratos bancários simples de app (valor grande, rótulo curto).
- **Evitar:** dashboards densos com muitos gráficos; tabelas largas que exigem rolagem horizontal no celular; **cores associadas a partidos** (vermelho, azul, laranja ou verde saturados como cor de destaque) e qualquer estética de material de campanha (foto de parlamentar, selos, "destaques"); semáforo vermelho/amarelo/verde para fases (sugere juízo de valor); ícones como único portador de significado.
- Paleta neutra (cinzas + uma cor de ação única, sem conotação partidária). As fases se diferenciam por **texto** e por um marcador de progresso neutro (1 a 4 passos), não por cor.

## Idioma e acessibilidade
- **Idioma:** pt-BR (`<html lang="pt-BR">`). Datas `27/10/2026`; horas `04:06`; dinheiro `R$ 1.234.567,89` (REQ-44).
- **Piso: WCAG 2.2 nível AA** (REQ-45). Pontos obrigatórios em todas as telas:
  - Contraste ≥ 4.5:1 para texto e ≥ 3:1 para componentes e foco.
  - Alvos de toque ≥ 48 × 48 px (acima do mínimo de 24 px do critério 2.5.8).
  - Reflow em 320 px e zoom de 200% sem perda de conteúdo (1.4.10, 1.4.4).
  - Cor nunca é o único meio de informação (1.4.1).
  - Foco visível e não encoberto (2.4.7, 2.4.11); ordem de foco igual à ordem visual.
  - Hierarquia de títulos: um `h1` por tela, que é o nome da tela ou do município.
  - Atualizações por HTMX anunciadas em região `aria-live="polite"`; o foco vai para o conteúdo novo só quando ele substitui a tela.
  - Valores abreviados têm a forma completa para leitor de tela (REQ-44).
  - Link "Pular para o conteúdo" no topo.
  - Tabelas de dados, quando houver, com `<th scope>` e `<caption>`; no celular, viram listas de cartões.

## Elementos comuns a todas as telas
- **Cabeçalho:** marca "Rastro" (link para A01) e link "Sobre" (A11).
- **Rodapé** (REQ-03, REQ-38): "Dados do Portal da Transparência publicados em [`fonte_last_modified`]; verificado em [última verificação]" → A10; links para Glossário (A07) e Sobre (A11).
- **Estados globais** (aplicam-se a toda tela de dados, as fichas só citam):
  - *Sem dados ainda* (REQ-39): "Os dados ainda não foram carregados. Volte mais tarde."
  - *Verificação atrasada* (REQ-38): faixa discreta no topo, "Não conseguimos verificar a fonte desde [data]".
  - *Sem conexão em fragmento* (REQ-42): mensagem no lugar do fragmento + "Tentar de novo"; conteúdo anterior preservado.
  - *Sem permissão:* **não se aplica a nenhuma tela**. O acesso é público e sem login (REQ-01).
