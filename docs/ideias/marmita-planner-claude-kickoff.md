# Marmita Planner — CLAUDE.md inicial (kickoff)

> Este arquivo é o rascunho do `CLAUDE.md` que deve ser copiado para a raiz do
> repositório `marmita-planner` quando ele for criado. O PRD completo está em
> `marmita-planner-prd.md` (copiar para `docs/PRD.md` no repo novo).

---

# Projeto — Marmita Planner

## O que é
App de planejamento alimentar para quem faz marmitas (consumo próprio ou venda):
marmitas, receitas, lista de compras, custos, estoque (despensa/geladeira/freezer),
scanner inteligente e planejador semanal por IA. **Especificação completa em
`docs/PRD.md` — ler antes de codar.** Produto do Eduardo (eduardoaragao.com),
separado do app de Editais (que é gratuito) e do futuro app de Teses.

## Decisões herdadas de projetos anteriores do Eduardo
- **Flutter** para o app (um código iOS+Android) — mesmo stack do app de Editais,
  que já foi publicado no Play Console (`com.eduardoaragao.editais_app`).
- **Backend Python (FastAPI)** quando precisar de nuvem; começar **offline-first**
  (dados locais no aparelho), sync depois (V4 do roadmap).
- Conteúdo/labels em **português (BR)**; código e commits podem ser em inglês.
- Human-in-the-loop e validação de dados via schema quando houver contrato.

## Roadmap (do PRD)
- **V1: marmitas + lista de compras + receitas** ← começar aqui
- V2: scanner inteligente + IA + custos
- V3: estoque + planejamento automático da semana
- V4: venda de marmitas + sincronização + smartwatch

## Primeiras tarefas sugeridas (V1)
1. Scaffold Flutter (`app/`) com navegação entre as telas do V1
   (Dashboard, Marmitas, Receitas, Compras, Configurações).
2. Modelo de dados local (receita → ingredientes → itens de compra; marmita =
   porções de receitas) com persistência local e export/import JSON (já previsto
   nas funcionalidades futuras do PRD).
3. Fluxo central: cadastrar receita → montar marmitas da semana → gerar lista de
   compras agregada automaticamente.
4. Tema visual próprio (não reaproveitar a identidade do app de Editais).

## Fora de escopo por enquanto
- Módulo de treino/exercícios: **vai existir**, mas será adicionado depois
  (decisão do Eduardo em 03/08/2026). Não estruturar nada que impeça essa adição.
- Venda de marmitas, sync em nuvem, smartwatch (V4).
