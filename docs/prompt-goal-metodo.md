# /goal — Método "Contrato Dourado"

> Prompt reutilizável, extraído do projeto App de Editais (2026).
> Preencha os [COLCHETES] e cole como primeira mensagem num projeto novo.

---

**Objetivo:** construir [DESCREVA O PRODUTO EM 2-3 FRASES: o que é, para
quem, e qual o caso piloto com dados reais].

Trabalhe pelo método abaixo, nesta ordem, sem pular a fase 0.

## Fase 0 — Referência antes de código (nada de codar ainda)

Crie uma pasta `referencia/` com quatro artefatos e me devolva para
aprovação:

1. **Contrato de dados** (`*.schema.json`, JSON Schema draft 2020-12):
   a estrutura que o sistema produz/consome, com a origem de cada campo
   anotada (AUTOMÁTICO / REVISÃO-HUMANA / CURADORIA / USUÁRIO-FINAL).
2. **Exemplo dourado**: uma instância REAL do domínio, válida contra o
   schema — será o caso de teste permanente.
3. **Spec dos módulos críticos**: para o problema mais difícil do
   projeto ([QUAL É?]), desenhe o algoritmo e os casos de aceite ANTES
   de implementar.
4. **CLAUDE.md** com: o que é o produto; **regras invioláveis** (o que
   jamais pode acontecer sem confirmação humana: [LISTE]); roadmap; e a
   seção **"Estado atual"** — que você DEVE atualizar a cada entrega,
   incluindo lições aprendidas, para qualquer sessão futura continuar
   sem re-descobrir nada.

Só depois da minha aprovação: scaffold + Git, com um **teste de
contrato** (o exemplo dourado valida contra o schema) verde no primeiro
commit.

## Regras do método (valem a sessão inteira)

1. **Contrato é a fonte da verdade.** Toda saída valida contra o schema;
   inválido = erro fatal, nunca emita rascunho quebrado. Se houver banco,
   o documento vive em coluna JSON — o schema manda, o banco carrega.
2. **Golden test de ponta a ponta** contra o artefato real do domínio
   ([QUAL ARQUIVO/DADO REAL EXISTE?]). Comparação tolerante a
   normalização (acentos, espaços), por contenção quando o golden for
   amostra.
3. **Comece pelo módulo mais arriscado, com testes primeiro.** Fixtures
   reconstruídas de dados reais, incluindo as armadilhas reais — não
   invente exemplos fáceis.
4. **Human-in-the-loop com travas**: os campos críticos saem como
   rascunho; publicar exige todas as travas abertas; **editar depois de
   confirmar fecha a trava de novo**; reprocessar fecha todas.
5. **Mutação segura**: toda alteração edita uma cópia, valida contra o
   contrato e só então grava.
6. **Verificação viva, sempre**: depois dos testes, dirija o
   navegador/dispositivo de verdade (cliques, formulários, medições) e
   me mostre a prova. Races, encoding e layout só aparecem aí.
7. **Dados do usuário ficam no dispositivo**; o servidor recebe apenas
   resumos que o usuário escolheu compartilhar.
8. **Estado derivado é função pura** dos dados primários (placares,
   medalhas, métricas): recalcule sempre, nunca acumule. Escadas de
   conquista como listas de dados.
9. **Commits incrementais** com mensagem explicando o porquê (no
   Windows: mensagem via arquivo, `git commit -F`). CLAUDE.md atualizado
   no mesmo commit.
10. **Incidentes reais do domínio viram casos de teste** permanentes.

## Sequência de execução

1. Fase 0 → aprovação → scaffold + teste de contrato
2. Núcleo de risco com testes → 3. demais módulos guiados por inspeção
   do artefato real → 4. pipeline completo + golden e2e → 5. camada de
   revisão humana com travas → 6. interface do usuário final → 7.
   iterações de produto — cada uma fechando o ciclo: implementar →
   analyze/testes → verificação viva → CLAUDE.md → commit.

Contexto do ambiente: [SO / ferramentas já instaladas / restrições].
Convenções: [idioma do código vs. conteúdo, estilo].
