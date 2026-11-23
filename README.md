# Rastro

Acompanhamento das emendas parlamentares federais destinadas a um município, com o estado de
execução traduzido para linguagem que o morador entende.

> **Status:** repositório recém-criado. Nenhuma linha de aplicação escrita. Este README existe para
> receber os artefatos que alimentam o `/paul:init` de cada módulo.
>
> **Disciplina:** DINF00071 — Desenvolvimento Dirigido por Especificação com Agentes · CI/UFPB · 2026.2

---

## O problema

Emendas parlamentares destinam dinheiro federal a municípios, e o dado é público por obrigação
legal. Ainda assim, o morador não consegue responder a pergunta que importa: *aquela emenda para a
minha cidade virou alguma coisa?* O dado existe em CSV de dezenas de colunas, e o estado da execução
é descrito em vocabulário orçamentário — empenhado, liquidado, pago — que não diz nada a quem não
trabalha com orçamento público.

A consequência é que a transparência existe no papel e não existe na prática: quem fiscalizaria não
consegue ler, e quem consegue ler já é especialista.

## O que o sistema faz

Importa os dados oficiais em lotes, normaliza e guarda a proveniência de cada registro, traduz as
fases de execução para linguagem simples, expõe consulta por município e avisa quem assinou quando
alguma coisa muda entre um lote e o seguinte.

## Quem usa

| Papel | O que precisa |
|---|---|
| Morador | Saber o que foi destinado à cidade dele e em que pé está, sem vocabulário técnico |
| Jornalista local / controle social | Rastrear um valor da indicação ao pagamento, com a fonte de cada afirmação |
| Gestor municipal | Acompanhar o que está empenhado mas não executado |

## Fora de escopo (preliminar — o grupo fecha e justifica)

- Emendas estaduais e municipais: fonte e estrutura diferentes, não cabem no prazo.
- Juízo sobre mérito ou qualidade da emenda: o sistema mostra o caminho do dinheiro, não opina.
- Cruzamento com execução de obra em campo: não há fonte confiável.
- Cadastro de usuário além do necessário para assinatura de alerta.

## Módulos

Um repositório, quatro módulos independentes. Cada módulo tem persistência, API, componente
concorrente, desempenho medido e testes — os cinco, sozinho.

| # | Módulo | Responsável | O que faz |
|---|---|---|---|
| 1 | `ingestao` | *a definir* | Baixa, valida e normaliza os lotes oficiais; guarda proveniência por registro; publica o lote de forma atômica |
| 2 | `nucleo` | *a definir* | Calcula a diferença entre lotes e o estado de execução consolidado de cada emenda |
| 3 | `consulta` | *a definir* | API e busca por município, parlamentar e função; agregações; contrato versionado |
| 4 | `saida` | *a definir* | Assinaturas por filtro e limiar; disparo de alerta com entrega única por assinante |

**Contrato principal:** o lote publicado. A ingestão publica; núcleo, consulta e saída leem — e
nenhum deles sabe como o CSV da origem é lido.

## Dados e privacidade

Dado público e agregado, sem titular identificado. O risco aqui não é privacidade, é **atribuição**:
uma tradução errada de fase pode fazer o sistema afirmar que um parlamentar deixou de executar algo
que ele executou. Por isso:

- Toda informação exibida carrega a fonte, o lote e a data de extração.
- A tradução de fase é tabela versionada e auditável, nunca regra escondida no código.
- O sistema não classifica, não pontua e não ranqueia parlamentares.

**Fontes previstas:** Portal da Transparência / CGU (dados abertos, CSV com dicionário) e Siga Brasil
(Senado), com atribuição obrigatória da fonte.

## Estrutura do repositório

```
rastro/
├── README.md              # este arquivo — brief do projeto
├── CONTRATOS.md           # FI-02: módulos, contratos e duplos
├── modulos/
│   ├── ingestao/   .paul/
│   ├── nucleo/     .paul/
│   ├── consulta/   .paul/
│   └── saida/      .paul/
└── .gitignore             # .claude/ fora do versionamento
```

## Artefatos de entrada do `/paul:init`

O init de cada módulo só roda depois que isto estiver no repositório:

- [ ] **FI-01 de cada integrante**, com as seções 7 e 8 escritas no nível do módulo
- [ ] **CONTRATOS.md** do grupo: os quatro módulos, os contratos entre pares que se tocam e o duplo de cada contrato
- [ ] **Teste de independência** respondido por cada integrante
- [ ] **Telas do sistema** (Trabalho 1): no mínimo dez, como mock, descrição detalhada ou desenho
- [ ] **Artefatos de arquitetura** (Trabalho 1): padrão de especificação escolhido, justificativa e os artefatos produzidos

## Como o trabalho é conduzido

Cada módulo roda o ciclo **Plan → Audit → Apply → Unify**: o plano declara critérios de aceitação
verificáveis, a auditoria revisa antes de qualquer código, a execução segue o plano aprovado e o
fechamento compara planejado com entregue.

A **Fase 1 (Fundação)** é a mesma para todos os projetos da turma: scaffold com CI que falha quando
deve, banco com as restrições de dados no schema, e deploy que só publica com o CI verde. A
diferença entre os projetos começa na Fase 2.

## Licença

MIT.
