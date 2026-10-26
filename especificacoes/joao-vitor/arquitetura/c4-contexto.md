# C4 · Nível 1 — Contexto do sistema

Pessoas e sistemas externos com que o Rastro se relaciona (seção 3 do arc42). A fronteira do sistema é o que o grupo constrói: a CLI de dados, a API, o painel e o banco.

```mermaid
C4Context
    title Rastro — contexto do sistema

    Person(cidadao, "Cidadão", "Consulta emendas, localidades e valores pelo navegador, muitas vezes no celular")
    Person(jornalista, "Jornalista ou pesquisador", "Filtra, compara e confere a fonte; consome a API")
    Person(controle, "Pessoa de controle social", "Assina filtros e acompanha alertas no painel")
    Person(operador, "Operador de dados", "Importa, valida e publica lotes pela linha de comando")

    System(rastro, "Rastro", "Reúne registros públicos de emendas parlamentares federais e mostra valores por etapa, favorecidos e mudanças entre lotes, sempre com a origem de cada dado")

    System_Ext(cgu, "Portal da Transparência (CGU)", "ZIP com CSVs de emendas e de pagamentos por favorecido")
    System_Ext(siga, "Siga Brasil (Senado)", "Execução orçamentária; integração sujeita à validação (REQ-13)")
    System_Ext(agendador, "Agendador do sistema (launchd/cron)", "Dispara a sincronização periódica")

    Rel(cidadao, rastro, "Consulta emendas e proveniência", "HTTPS, navegador")
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
| Cidadão | pessoa | painel web (celular e desktop) | Consulta; não fornece dados | P01–P09 |
| Jornalista ou pesquisador | pessoa | painel web e API pública | Consulta; limite de 60 req/min por IP (REQ-28) | P02, P03, P06, P08, P09, D01 |
| Pessoa de controle social | pessoa | painel web | Chave de assinante, filtros e limiares (sem dado pessoal, REQ-41) | S01–S05 |
| Operador de dados | pessoa | CLI `rastro` na máquina local | Arquivos ZIP baixados, comandos de publicação | O01, O02 |
| Portal da Transparência (CGU) | sistema externo | download HTTPS | ZIP Latin-1 `;`: emendas e pagamentos por favorecido | P09 (link de origem) |
| Siga Brasil (Senado) | sistema externo | download HTTPS (a validar) | Valores de execução orçamentária | P03 e P09, quando habilitado |
| Agendador (launchd/cron) | sistema externo | processo local | Disparo de `rastro sincronizar` | — |

## Limites (o que fica fora do sistema)

- O Rastro **não julga** fraude ou ilegalidade e não declara a aplicação final do recurso (FI-01 §5).
- **Não há canal externo de alerta**: sem e-mail, SMS ou push no MVP.
- **Não cobre** emendas estaduais ou municipais, nem anos anteriores a 2025 no MVP.
- **Não guarda** dados pessoais de usuários (ADR-0005).
- A **aplicação final** do dinheiro (notas, contratos) está fora do contexto: nenhum sistema externo fornece esse dado ao Rastro.
