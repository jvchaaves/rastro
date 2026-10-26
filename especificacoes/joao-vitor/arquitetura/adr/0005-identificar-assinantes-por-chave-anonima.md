# ADR-0005 · Identificar assinantes por chave anônima, sem login e sem dados pessoais

- **Status:** aceita (fecha a lacuna "identidade do assinante" do FI-01 §12)
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-31, REQ-32, REQ-41, REQ-42

## Contexto

- O alerta é exibido no painel, sem envio externo (FI-01 §10.2).
- A decisão de alerta no painel foi tomada para "validar a aposta sem integrações nem dados pessoais extras".
- Mesmo assim, o assinante precisa reencontrar as suas assinaturas em outro acesso ou dispositivo.

## Opções consideradas

1. **Login com e-mail e senha**, ou link mágico por e-mail: exige guardar e-mail e enviar mensagens.
2. **OAuth (Google/GitHub)**: guarda identidade de terceiros e depende de um provedor externo.
3. **Chave anônima de assinante**: segredo aleatório de 128 bits, gerado na primeira assinatura e mostrado uma vez. O servidor guarda só o hash.

## Decisão

Opção 3.

- A chave vai no cabeçalho `X-Chave-Assinante`, nunca na URL (evita logs e histórico).
- O painel guarda a chave em `localStorage` e oferece "Entrar com chave" (S03) em outro dispositivo.
- Cada chave pode ter até 20 assinaturas.

## Consequências

- **(+)** Não há dado pessoal (REQ-41), nem senha, nem e-mail transacional.
- **(+)** É compatível com a futura adição de canais: um e-mail pode ser associado à chave mais tarde, com consentimento explícito.
- **(−)** Quem perde a chave perde as assinaturas, porque não há recuperação. A tela S02 deixa isso explícito e oferece copiar e baixar a chave.
- **(−)** Quem tem a chave tem acesso total às assinaturas dela. É aceitável porque as assinaturas só contêm filtros sobre dados públicos.
