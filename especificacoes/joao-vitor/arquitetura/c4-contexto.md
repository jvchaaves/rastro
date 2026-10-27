# C4 · Nível 1 — Contexto do sistema

Pessoas e sistemas externos com que o Rastro se relaciona (seção 3 do arc42). A fronteira do sistema é o que o grupo constrói: a CLI de dados, a API, o painel e o banco. A coluna "Telas" da tabela abaixo é a mesma do quadro "Atores × telas" do inventário, e o `verificar.py` confere a igualdade.

```mermaid
C4Context
    title Rastro — contexto do sistema

    Person(cidadao, "Cidadão (morador)", "Quer saber o que foi destinado à sua cidade e em que pé está; navegador, muitas vezes no celular")
    Person(gestor, "Gestor municipal", "Acompanha o que está empenhado e ainda não foi pago no município")
    Person(jornalista, "Jornalista ou pesquisador", "Filtra, compara e confere a fonte; consome a API")
    Person(controle, "Pessoa de controle social", "Assina filtros e acompanha alertas no painel")
    Person(operador, "Operador de dados", "Importa, valida e publica lotes pela linha de comando")

    System(rastro, "Rastro", "Reúne registros públicos de emendas parlamentares federais e mostra, por município, valores por etapa, o estado em linguagem simples, favorecidos e mudanças entre lotes, sempre com a origem de cada dado")

    System_Ext(cgu, "Portal da Transparência (CGU)", "ZIP com CSVs de emendas e de pagamentos por favorecido")
    System_Ext(siga, "Siga Brasil (Senado)", "Execução orçamentária; integração sujeita à validação (REQ-13)")
    System_Ext(agendador, "Agendador do sistema (launchd/cron)", "Dispara a sincronização periódica")

    Rel(cidadao, rastro, "Consulta o município e as emendas, com proveniência", "HTTPS, navegador")
    Rel(gestor, rastro, "Consulta pendências do município e assina alertas", "HTTPS, navegador")
    Rel(jornalista, rastro, "Consulta painel e API", "HTTPS, JSON")
    Rel(controle, rastro, "Cria assinaturas e lê alertas", "HTTPS, navegador")
    Rel(operador, rastro, "Importa e publica lotes", "CLI")
    Rel(agendador, rastro, "Executa rastro sincronizar", "processo local")
    Rel(rastro, cgu, "Baixa pacotes de dados abertos", "HTTPS")
    Rel(rastro, siga, "Baixa relatórios de execução (fase 6)", "HTTPS")
    Rel(cidadao, cgu, "Confere o dado na origem pelo link de proveniência", "HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## Pessoas e sistemas externos

| Elemento | Tipo | Interage por | O que troca com o Rastro | Telas |
| :-- | :-- | :-- | :-- | :-- |
| Cidadão (morador) | pessoa | painel web (celular e desktop) | Consulta; chave de assinante se quiser alertas (sem dado pessoal, REQ-41) | P01, P02, P03, P04, P05, P07, P09, P10, P11, S01, S02, S03, S04, S05 |
| Jornalista ou pesquisador | pessoa | painel web e API pública | Consulta; limite de 60 req/min por IP de cliente (REQ-28, REQ-84) | P02, P03, P04, P06, P07, P08, P09, P11, D01 |
| Pessoa de controle social | pessoa | painel web | Chave de assinante, filtros e limiares (sem dado pessoal, REQ-41) | P08, S01, S02, S03, S04, S05 |
| Gestor municipal | pessoa | painel web | Consulta; chave de assinante para acompanhar o município | P02, P03, P10, S01, S02, S03, S04, S05 |
| Operador de dados | pessoa | CLI `rastro` na máquina local | Arquivos ZIP baixados, comandos de publicação e versões da tabela de tradução | O01, O02, P09, P11 |
| Portal da Transparência (CGU) | sistema externo | download HTTPS | ZIP Latin-1 `;`: emendas e pagamentos por favorecido | P09 (link de origem) |
| Siga Brasil (Senado) | sistema externo | download HTTPS (a validar) | Valores de execução orçamentária | P03 e P09, quando habilitado |
| Agendador (launchd/cron) | sistema externo | processo local | Disparo de `rastro sincronizar` | — |

## Limites (o que fica fora do sistema)

- O Rastro **não julga** fraude, ilegalidade ou mérito da emenda e não declara a aplicação final do recurso (FI-01 §5; brief).
- O Rastro **não classifica, não pontua e não ranqueia** parlamentares (brief; REQ-71).
- **Não há canal externo de alerta**: sem e-mail, SMS ou push no MVP.
- **Não cobre** emendas estaduais ou municipais (FI-01 §5; brief: fonte e estrutura diferentes), nem anos anteriores a 2025 no MVP (FI-01 §5 e §10.2).
- **Não cruza** com a execução de obra em campo: não há fonte confiável (brief).
- **Não guarda** dados pessoais de usuários (ADR-0005).
- A **aplicação final** do dinheiro (notas, contratos) está fora do contexto: nenhum sistema externo fornece esse dado ao Rastro.
