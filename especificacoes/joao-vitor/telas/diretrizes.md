# Diretrizes globais da interface — Rastro

Valem para todas as fichas de tela. As fichas não repetem estas diretrizes; registram só o que é próprio de cada tela.

## Público

| Quem | Situação de uso | O que espera da interface |
| :-- | :-- | :-- |
| Cidadão | Chega por um link compartilhado ou por busca, muitas vezes no celular, querendo saber "quanto foi para minha cidade" ou "o que fez o meu deputado" | Resposta direta, sem jargão sem explicação, sem precisar entender o ciclo orçamentário antes |
| Jornalista ou pesquisador | Apura uma pauta no computador, compara autores e UFs, precisa citar a fonte e reproduzir a consulta | Filtros precisos, números exatos, link para a origem e uma URL que reproduz a consulta |
| Pessoa de controle social | Acompanha um conjunto de emendas por semanas e volta ao painel para ver o que mudou | Assinar sem cadastro, ver alertas novos de forma clara e entender cada mudança |
| Operador de dados | Roda a CLI no terminal do macOS e decide se um lote pode ser publicado | Números de validação claros, decisão explícita e nada publicado por engano |

## Plataforma e orientação

- **Painel web** (telas P, D, S), responsivo:
  - celular em retrato a partir de 360 px de largura, prioridade do cidadão;
  - desktop a partir de 1280 px, prioridade do jornalista.
  - Tabelas largas rolam dentro do próprio contêiner no celular. Filtros viram uma folha inferior ("Filtros (3)").
- **Terminal** (telas O): largura mínima de 80 colunas, texto simples e legível sem cor.
- Toda consulta do painel tem uma URL estável com os filtros na query string (por exemplo, `/emendas?uf_gasto=PB&funcao_codigo=10`), para compartilhar e citar.

## Tom de voz e de interface

- **Factual e sóbrio.** Os verbos são os do registro: "empenhou", "liquidou", "pagou", "registrou recebimento". Nunca "gastou em", "desviou", "suspeito" ou "irregular".
- **Explica antes de exigir.** Cada termo técnico (empenhado, liquidado, restos a pagar) tem uma definição curta ao alcance de um toque, tirada do glossário.
- **Neutro em relação a pessoas.** Parlamentares e favorecidos aparecem pelo que o registro diz, sem adjetivos, cores de alarme ou rankings de "piores".
- **Frases curtas, voz ativa, segunda pessoa** quando fala com o usuário ("Você ainda não tem assinaturas").

## Princípios verificáveis

1. **Todo valor tem origem a um toque.** Cada valor monetário exibido leva, em no máximo uma interação, à fonte, ao lote, à data de referência e ao link do download oficial. *Verificação:* `e2e/proveniencia.spec.ts` percorre todos os valores das telas P (REQ-14, REQ-48).
2. **Etapas nunca se somam.** Empenhado, liquidado, pago, restos a pagar e recebido por favorecido aparecem sempre com o rótulo próprio, nunca num "total" único. *Verificação:* nenhuma tela tem um rótulo "Total" que agregue etapas (REQ-15).
3. **Dizer de quando é o dado.** Toda tela com dados mostra "Dados de dd/mm/aaaa · Lote #n" no cabeçalho, com link para P09 (REQ-48).
4. **Estado honesto.** Sem lote publicado, sem rede ou com erro, a tela diz isso por escrito. Nunca mostra R$ 0,00, tabela vazia ou valor guardado como se fosse atual (REQ-19, REQ-46, REQ-47).
5. **Nenhuma conclusão que o dado não sustenta.** Onde houver favorecidos, aparece o aviso do REQ-26. Nenhuma tela usa "aplicado em", "investido em" ou "resultado" (FI-01 §5).

## Referência visual

- **Ideia central: a trilha.** O mesmo elemento visual aparece em todas as telas com valores: uma barra única em que o empenhado é a trilha inteira e o liquidado e o pago a preenchem por dentro. Ela mostra quanto do dinheiro reservado já avançou, sem somar etapas. A cor segue uma escala sequencial de um só tom (claro → escuro = empenhado → liquidado → pago), e cada etapa sempre tem também o rótulo escrito.
- **Tipografia:** Geist (interface, títulos e números, com algarismos tabulares) e Geist Mono só para identificadores (código da emenda, hash, CLI). Títulos com tracking levemente negativo; corpo de 16 px; escala 13/15/16/20/24/40/56.
- **Paleta:** fundo cinza-esverdeado frio `#F2F4F3`, superfícies brancas, tinta `#0F1C22`, texto secundário `#4B5A60` (contraste ≥ 7:1), verde-pinho `#0E5E52` para ações e links, escala da trilha `#A7CFC4` / `#4A9E8B` / `#0E5E52`, âmbar `#FFF6E6`/`#8A4B00` só para avisos e diferenças entre lotes.
- **Inspira:** a clareza de produtos de dados com interface sóbria (painéis densos e legíveis, tabelas com números alinhados à direita) e o padrão de formulários do GOV.UK Design System (rótulo visível, erro junto ao campo).
- **Evitar:**
  - visual de "dashboard de BI" (velocímetros, pizza, gradientes);
  - vermelho de alarme associado a pessoas;
  - rankings de "piores";
  - mapas de calor que sugiram culpa;
  - emoji;
  - etiquetas em caixa-alta em cima de cada bloco.
- **Gráficos:** sempre têm uma tabela equivalente acessível.
- **Layout fino:** é do design system (shadcn/ui). As fichas especificam intenção, não pixel. Os mockups em `anexos/` são referência, não especificação.

## Idioma e formatos

- **pt-BR** em toda a interface (`<html lang="pt-BR">`).
- Moeda: `R$ 1.234.567,89`. Em cartões e gráficos, a forma abreviada `R$ 1,2 mi`, com o valor exato no rótulo acessível e no detalhe.
- Datas: `dd/mm/aaaa`. Mês de favorecido: `mm/aaaa`. Data e hora: `dd/mm/aaaa, hh:mm`.
- Código da emenda sempre completo e em fonte monoespaçada, com botão "copiar".
- Nomes de autores e favorecidos exatamente como publicados pela fonte.

## Acessibilidade (piso: WCAG 2.2 nível AA)

- Contraste de texto ≥ 4,5:1 (≥ 3:1 para texto ≥ 24 px e para componentes de interface e gráficos).
- Navegação completa por teclado, com ordem de foco igual à ordem visual e foco sempre visível (2.4.7, 2.4.11). Há um link "Pular para o conteúdo".
- Alvos de toque ≥ 24×24 px (2.5.8), e 44 px no celular por padrão.
- Cor nunca é o único meio de informação: etapas se distinguem por rótulo, posição e padrão, além da cor (1.4.1).
- Todo gráfico tem tabela equivalente e um resumo textual (1.1.1).
- Mensagens de estado (carregando, erro, "copiado", "alerta marcado como lido") são anunciadas por `aria-live="polite"` (4.1.3).
- Formulários têm rótulos visíveis, erros junto ao campo e um resumo de erros no topo com links para os campos (3.3.1, 3.3.3).
- Nenhuma ação depende de arrastar (2.5.7) e nenhuma informação depende de passar o mouse.
- Respeitar `prefers-reduced-motion` e `prefers-color-scheme`.
- Na CLI: nenhum estado só por cor (rótulos `OK`/`AVISO`/`ERRO`), suporte a `NO_COLOR` e `--sem-cor`, e saída `--json` para leitores de tela e automação.

## Elementos comuns a todas as telas do painel

- **Cabeçalho:** marca "Rastro" (→ P01), navegação Emendas (P02) · Comparar (P06) · O que mudou (P08) · Dados (P09) · API (D01), botão "Alertas" com contador de não lidos (S05, ou S03 se não houver chave), e a faixa "Dados de dd/mm/aaaa · Lote #n" (→ P09), vinda de `obter_status`.
- **Rodapé:** "O Rastro reúne registros públicos. Recebimento registrado não comprova aplicação final nem indica irregularidade." Links para P09 e para o repositório.
- **Estados comuns:**
  - carregando (REQ-44);
  - vazio (REQ-45);
  - erro com `X-Request-Id` (REQ-46);
  - offline (REQ-47);
  - sem lote publicado (REQ-19);
  - limite de taxa: "Muitas consultas seguidas. Tente de novo em N s." (REQ-28).

  As fichas citam esses estados e detalham só o que muda em cada tela.
