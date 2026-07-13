# Relatório deep-research — Sessão "App de Editais" (jul/2026)

Retrospectiva completa da sessão que construiu o produto do zero ao app
funcionando, com foco no **método** — o que é transferível para qualquer
outro projeto.

---

## 1. O que foi construído

Pipeline completo, com dados reais do piloto (PGE/AL 2026, Cebraspe):

| Camada | Entrega |
|---|---|
| **Parser** (Python) | PDF oficial (51 págs.) → JSON válido contra contrato: 826 nós de conteúdo, 22 eventos de cronograma, corte de lei/jurisprudência, vagas, fases, isenções, retificações incorporadas |
| **Painel de revisão** (FastAPI + Jinja2) | Upload → rascunho travado → revisão da árvore (promover/rebaixar/editar) → confirmações → publicação só com 4 travas abertas |
| **Radar** | Compara retificações incorporadas × publicadas no site da banca; retificação não incorporada **trava a publicação** |
| **API** | Só expõe editais publicados; API social (contas leves, amizades, incentivos) |
| **App Flutter** | 8 telas: hub, conteúdo (grade responsiva de matérias com ícones), relógio de estudo com modo foco, datas com calendário + datas próprias, dados da prova (ViaCEP + deep links), provas anteriores, conquistas (46 insígnias em 6 categorias), amigos (ranking + incentivos), Stories (cards 9:16 PNG) |

Números finais: **158 testes** (133 backend + 25 Flutter), ~15 commits
incrementais, tudo verificado ao vivo no navegador.

## 2. A espinha dorsal do método

### 2.1 Referência antes de código
O projeto nasceu com uma pasta `referencia/` escrita ANTES de qualquer
código: **contrato de dados** (JSON Schema draft 2020-12), **exemplo
dourado** real e válido, **spec do parser** módulo a módulo (com o
algoritmo do problema mais difícil já desenhado e casos de aceite), e
**protótipo navegável** das telas. Todo o resto da sessão foi execução
contra essa referência — quase nenhuma decisão de produto precisou ser
tomada no meio do código.

### 2.2 O contrato é a fonte da verdade
- Toda saída do parser valida contra o schema; **inválido = erro fatal**,
  não emite rascunho.
- O banco guarda o documento inteiro numa coluna JSON — o schema manda,
  o banco só carrega. Travas de revisão (que não pertencem ao contrato)
  são colunas próprias.
- Toda mutação no painel **edita uma cópia, valida e só então grava** —
  um clique errado nunca corrompe o rascunho.

### 2.3 Golden test de ponta a ponta
`parse(pdf_real) == campos-chave do exemplo dourado`. Comparação por
contenção (o golden é amostra), com normalização de acentos (golden é
ASCII, parser emite texto literal acentuado — decisão registrada em
memória na primeira sessão e honrada nas seguintes).

### 2.4 Comece pelo módulo mais arriscado, com testes primeiro
O outline do item 17 (árvore de conteúdo) era o risco nº 1: números de
lei (`Lei nº 14.133/2021`) parecem marcadores de outline (`14.133`).
Solução da spec: aceitar candidato só se for **continuação plausível da
sequência** ("próximo número esperado"). Fixtures reconstruídas do texto
real **com as armadilhas reais** (inclusive `Decreto nº 20.910/1932
Prescrição...`, onde "1932 Prescrição" tem exatamente a cara de marcador).

### 2.5 Human-in-the-loop com travas invioláveis
Nada publica sem: árvore revisada + corte confirmado + datas confirmadas +
radar rodado e em dia. **Editar depois de confirmar fecha a trava de
novo.** Reupload (fluxo pós-retificação) fecha todas.

### 2.6 Verificação viva além dos testes
Dirigir o navegador de verdade (cliques, formulários, medição de DOM)
encontrou bugs que 124 testes verdes não pegaram:
- **Race condition real**: commit da sessão no teardown da dependency
  corre contra o GET do redirect → tela mostrava estado antigo. Fix:
  commit explícito ANTES do redirect.
- **Item 18 fantasma** no sectioner: tópico do outline caindo em início
  de linha virava item do edital → regra "cabeçalho é TODO caixa alta",
  pega pelo smoke test no PDF real.
- Grade desproporcional no desktop → corrigida e **cravada em widget
  tests de layout** que medem os quadros em 380px e 1280px.

### 2.7 Dados do usuário ficam no aparelho
Progresso, diário, sessões de estudo, locais de prova: tudo local. A rede
social só recebe **resumo** (pontos/percentual). Conta leve sem senha
(apelido → código de amigo + token de aparelho).

### 2.8 Estado derivado é função pura
Pontos e insígnias são **recalculados do progresso, nunca acumulados** —
o placar não tem como divergir do estudo real. Escadas de conquista são
listas de dados (ajustar marco = 1 linha).

### 2.9 CLAUDE.md como memória viva
Seção "Estado atual" atualizada a **cada** entrega, com as lições
embutidas ("commit antes do redirect", "item 17 tem preâmbulo"). Sessões
futuras (e o próprio usuário) leem e continuam sem re-descobrir nada.

### 2.10 Incidentes do domínio viram testes
O piloto real tinha a situação perfeita: o PDF consolidava até a
retificação nº 3, mas a banca já tinha publicado a nº 5. Isso virou O
caso de aceite do radar — com os 10 PDFs oficiais no repo.

## 3. Lições operacionais (ambiente)

- **Windows/PowerShell**: mensagens de commit multilinha com aspas
  quebram o here-string → sempre `git commit -F arquivo`.
- Console PowerShell mói acentos — inspecionar texto extraído **em
  arquivo**, nunca no console.
- Flutter web + preview: semântica exige clique no placeholder; ids dos
  nós mudam a cada render (re-consultar antes de clicar); primeira carga
  às vezes precisa de reload.
- pymupdf entrega tabelas como linhas soltas (colunas viram sequência) —
  parsers de tabela são máquinas de estado sobre linhas.
- Instalação de SDK grande: baixar em background e seguir trabalhando
  (o código do app foi todo escrito durante o download do Flutter).

## 4. Sequência que funcionou (ordem de execução)

1. Ler a referência → propor stack/estrutura → **aprovação antes de codar**
2. Scaffold + teste de contrato (golden valida contra schema) — 1º commit já com verde
3. Núcleo de risco (outline/corte) com testes
4. Demais extratores guiados por inspeção do artefato real
5. Pipeline completo + golden e2e
6. Serviço de comparação (radar) com fetcher plugável (rede fora dos testes)
7. Camada humana (painel) com travas
8. Interface final (app), verificada ao vivo
9. Iterações de produto (gamificação, social, relógio...) — cada uma:
   implementar → analyze/testes → verificar no navegador → CLAUDE.md → commit
