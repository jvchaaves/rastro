# Diretrizes globais da interface — Rastro

Valem para todas as fichas de tela. As fichas não repetem estas diretrizes; registram só o que é próprio de cada tela.

## Público

| Quem | Situação de uso | O que espera da interface |
| :-- | :-- | :-- |
| Cidadão (morador) | Chega por um link compartilhado ou por busca, muitas vezes no celular, querendo saber "o que foi destinado à minha cidade e em que pé está" | Resposta direta em linguagem simples ("O dinheiro foi reservado"), com o termo técnico ao lado, sem precisar entender o ciclo orçamentário antes |
| Jornalista ou pesquisador | Apura uma pauta no computador, compara autores e UFs, precisa citar a fonte e reproduzir a consulta | Filtros precisos, números exatos, link para a origem e uma URL que reproduz a consulta |
| Pessoa de controle social | Acompanha um conjunto de emendas por semanas e volta ao painel para ver o que mudou | Assinar sem cadastro, ver alertas novos de forma clara e entender cada mudança |
| Gestor municipal | Acompanha, no computador da prefeitura, o que foi empenhado para o município e ainda não foi pago | Um recorte "empenhado e ainda não pago" pronto, com a lista exportável e alerta quando algo andar |
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

1. **Todo valor tem origem a um toque e data à vista.** Cada valor monetário leva, em no máximo uma interação, à fonte, ao lote, à data de referência, à data de extração e ao link do download oficial; toda tela com dados mostra a faixa de proveniência do cabeçalho ("Dados de dd/mm/aaaa, extraídos em dd/mm, lote n do Portal da Transparência"), com link para P09. *Verificação:* `e2e/proveniencia.spec.ts` percorre todos os valores das telas P (REQ-14, REQ-48).
2. **Etapas nunca se somam.** Empenhado, liquidado, pago, restos a pagar e recebido por favorecido aparecem sempre com o rótulo próprio, nunca num "total" único. *Verificação:* nenhuma tela tem um rótulo "Total" que agregue etapas (REQ-15, REQ-77).
3. **Linguagem simples com o termo técnico ao lado.** Todo estado de execução aparece primeiro como o texto da tabela de tradução vigente ("A entrega foi conferida; falta pagar") e logo depois como o termo técnico ("liquidada"), com a versão da tradução a um toque (P11). O termo técnico é o valor de `estado_execucao` com espaço no lugar de `_` ("sem execução", "paga em parte"); só a P11 e a D01, que documentam o contrato, mostram o valor do enum como está (`paga_em_parte`). Nomes de município chegam da API como a CGU publica ("JOÃO PESSOA") e o painel os exibe em caixa de título ("João Pessoa"), sem alterar o identificador. O texto nunca é escrito no código do painel. *Verificação:* `e2e/traducao.spec.ts` confere que todo estado exibido é igual ao `estado_texto` da API (REQ-69, ADR-0008).
4. **Estado honesto.** Sem lote publicado, sem rede ou com erro, a tela diz isso por escrito. Nunca mostra R$ 0,00, tabela vazia ou valor guardado como se fosse atual (REQ-19, REQ-46, REQ-47).
5. **Nenhuma conclusão que o dado não sustenta.** Onde houver favorecidos, aparece o aviso do REQ-26. Nenhuma tela usa "aplicado em", "investido em" ou "resultado", porque o Rastro não declara o gasto final (FI-01 §5), nem "atrasada" ou "parada", porque o sistema não opina sobre a execução (brief, fora de escopo), e nenhuma tela ranqueia pessoas: autores aparecem em ordem alfabética, sem posição nem "maiores" (REQ-71). *Verificação:* `e2e/linguagem.spec.ts` procura os termos proibidos e confere a ordem alfabética em P06.

## Referência visual

- **Ideia central: a trilha.** O mesmo elemento visual aparece em todas as telas com valores: uma barra única em que o empenhado é a trilha inteira e o liquidado e o pago a preenchem por dentro. Ela mostra quanto do dinheiro reservado já avançou, sem somar etapas. A cor segue uma escala sequencial de um só tom (claro → escuro = empenhado → liquidado → pago), e cada etapa sempre tem também o rótulo escrito.
- **Tipografia:** Geist (interface, títulos e números, com algarismos tabulares) e Geist Mono só para identificadores (código da emenda, hash, CLI). Títulos em peso 800 com tracking negativo; corpo de 16 px; escala 13/15/16/20/26/38/52/76.
- **Superfícies — "livro-razão":** fundo `#F2F4F0` com quadriculado fino, como papel de registro contábil. Cartões, campos e botões têm borda de tinta `#0F1C22` (1,5–2 px), cantos arredondados de 10–12 px e sombra deslocada **verde-pinho**, que afunda ao clicar. O cabeçalho é uma barra flutuante com a mesma borda e sombra.
- **Inspiração declarada:** a energia de sites estudantis com cara de papel e botões "táteis" (bordas grossas e sombra dura). A identidade (quadriculado de livro-razão, barra flutuante, sombra verde, marca quadrada com as três etapas da trilha) é própria do Rastro.
- **Paleta:** papel `#F2F4F0`, tinta `#0F1C22`, texto secundário `#3B4A50` (8,3:1 sobre o papel) e `#4B5A60` (6,5:1), verde-pinho `#0E5E52` para ações e links (6,9:1), escala da trilha `#A7CFC4` / `#4A9E8B` / `#0E5E52` (na contagem por estado da P10 e na P11, `#2C7E6F` marca "paga em parte", entre o liquidado e o pago), âmbar `#F5B83D` só como fundo de destaque com texto em tinta (9,8:1), nunca como cor de texto (moeda, contador de alertas, faixa de mudanças).
- **Contraste da trilha:** os tons claros da trilha não têm 3:1 entre si, então a trilha nunca carrega informação sozinha: ela tem contorno de tinta (15,7:1 sobre o papel) e os valores de cada etapa estão sempre escritos ao lado, com rótulo. Por isso ela é tratada como reforço visual, e a informação está no texto (WCAG 1.4.1 e 1.4.11).
- **Movimento:** uma entrada suave por tela, as moedas correndo na trilha da P01 e a faixa de mudanças. Tudo para com `prefers-reduced-motion`.
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

## Convenção para o campo "Ações" (diretiva 5)

Toda ação de toda ficha termina apontando o contrato que ela aciona, numa destas quatro formas:

| Forma | Quando | Exemplo |
| :-- | :-- | :-- |
| (`operação`) | A ação chama a API na própria tela | "Alterar um filtro → (`listar_emendas`)" |
| → Pxx (`operação`) | A ação navega para outra tela; a operação é a que a tela de destino chama ao abrir | "Linha → P03 (`obter_emenda`)" |
| `cli:comando` ou evento | Superfície do terminal ou evento interno | "Ctrl-C → (`cli:importar`)", "`lote.publicado`" |
| **ação local** · sem chamada à API (REQ-74) | Copiar, ligar ou desligar uma série, gerar CSV/.txt de dados já carregados, sair, voltar, abrir link externo, ir para uma tela que não chama a API ao abrir (S02, S03) | "Copiar código → ação local · sem chamada à API (REQ-74)" |

O `verificar.py` confere que cada ação de cada ficha tem uma dessas quatro marcas e que a operação existe no contrato.

Telas de destino e a operação que cada uma chama ao abrir: P01 `obter_status` · P02 `listar_emendas` · P03 `obter_emenda` · P04 `obter_linha_do_tempo` · P05 `listar_favorecidos` · P06 `obter_agregacoes` · P07 `obter_autor` · P08 `listar_mudancas` · P09 `listar_lotes` (ou `obter_lote` quando abre num lote) · P10 `obter_municipio` · P11 `listar_traducoes` · D01 `obter_contrato` · S01 `listar_opcoes_filtro` · S02 e S03 nenhuma (ação local) · S04 `listar_assinaturas` · S05 `listar_alertas` · O02 `cli:publicar`.

## Elementos comuns a todas as telas do painel

- **Cabeçalho (barra flutuante):** cartão branco destacado do topo, com borda de tinta e sombra verde. Contém a marca (→ P01), o menu Emendas (P02), Comparar (P06), O que mudou (P08), Dados (P09) e API (D01), com a seção atual em realce verde-claro. Tem também a busca global ("Buscar emenda ou cidade", atalho `/`: 12 dígitos → P03 via `obter_emenda`; nome de município de `listar_opcoes_filtro.municipios` → P10 via `obter_municipio`; outro texto → P02 com `?q=`), o sino de alertas com o número de não lidos (S05 via `listar_alertas`, ou S03 sem chave) e o botão "Acompanhar" (S01). Logo abaixo da barra fica a linha "Dados de dd/mm/aaaa, extraídos em dd/mm, lote n do Portal da Transparência. Ver origem" (→ P09), vinda de `obter_status` (`Status.fontes[].proveniencia`: `data_referencia`, `importado_em`, `lote_id`) (REQ-48). No celular ficam só a marca, o sino e o botão de menu.
- **Rodapé:** "O Rastro reúne registros públicos. Recebimento registrado não comprova aplicação final nem indica irregularidade." Links para P09 e para o repositório.
- **Estados comuns:**
  - carregando (REQ-44);
  - vazio (REQ-45);
  - erro com `X-Request-Id` (REQ-46);
  - offline (REQ-47);
  - sem lote publicado (REQ-19);
  - limite de taxa: "Muitas consultas seguidas. Tente de novo em N s." (REQ-28). O painel repassa o IP do navegador à API (REQ-84), então o limite vale por pessoa, também no painel.

  As fichas citam esses estados e detalham só o que muda em cada tela.
