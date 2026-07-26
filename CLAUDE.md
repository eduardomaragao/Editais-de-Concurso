# Projeto — App de acompanhamento de editais de concurso

## O que é
Produto para candidatos de concursos públicos jurídicos (base de alunos de **eduardoaragao.com**). O app pega um edital, destrincha tudo (datas, local, corte de lei/jurisprudência, conteúdo programático) e deixa o candidato acompanhar estudo e prazos. Piloto: **PGE/AL — Procurador do Estado (Cebraspe, Edital 01/2026)**.

Este projeto foi especificado passo a passo com o Eduardo. Antes de codar, **leia `referencia/`** — lá estão o contrato de dados, um edital real já processado e o protótipo navegável das telas.

## Arquitetura (proposta; refine se fizer sentido)
- **Backend Python** — parser de editais (PDF → JSON) + API. Sugestão: FastAPI; extração com `pymupdf`/`pdfplumber`. Postgres para persistência.
- **App mobile** — **Flutter** (um código só para iOS e Android). Consome a API.
- **Painel admin (web)** — onde o Eduardo revisa e aprova o que o parser extraiu antes de publicar.
- **Radar** — serviço que monitora o site da banca: descobre novos editais e detecta retificações de editais já cadastrados.

## Modelo de entrada (decisão do Eduardo)
O Eduardo **sobe o PDF oficial consolidado** ("atualizado conforme retificações"). O parser extrai → o Eduardo revisa → publica. A busca automática é só um **radar** que avisa quando há retificação nova; não é a fonte da verdade.

## Contrato de dados
Toda saída do parser **valida** contra `referencia/edital.schema.json` (JSON Schema draft 2020-12). `referencia/pge_al.instance.json` é um exemplo real **válido** — use como caso de teste dourado. `referencia/ficha_campos_edital.md` é o dicionário de campos com a origem de cada um.

Origem dos campos: **AUTO** (parser) · **REVISÃO** (Eduardo confirma) · **CURADORIA** (Eduardo insere) · **USUÁRIO** (candidato preenche no app).

## Regras invioláveis (human-in-the-loop)
1. **Árvore de conteúdo** (matéria → tópico → subtópico) e os **títulos** saem do parser como rascunho, mas a **estrutura e o texto são REVISÃO**. Nada publica sem `edital.conteudo_revisado == true`. O texto do nó deve ser **literal do edital** (item 17).
2. **Corte de lei/jurisprudência** = REVISÃO. Costuma vir como **referência relativa** ("data de publicação deste edital"); guardar o texto literal + a data resolvida. Ancora na **1ª publicação** — retificação **não move** o corte.
3. **Data/hora de prova** = REVISÃO.
4. **Sempre trabalhar do consolidado atualizado.** O radar compara `retificacoes_incorporadas` (no arquivo) com `ultima_retificacao_publicada` (site) e marca `radar_desatualizado`. Quando desatualizado, trava a publicação e pede reupload. (No piloto, o PDF consolidava só até o nº 3, mas o nº 5 já havia remarcado as provas para 05–06/09/2026 — o radar tem que pegar isso.)

## Telas do app (ver `referencia/proto_app_pge_al.html`)
- **Edital (hub):** cartões de navegação + selo do radar + card do corte.
- **Dados da prova:** dia/horário (do edital) + **local preenchido pelo candidato** (CEP + sala) que gera deep links de **Uber, 99** e **Google Maps** (rota de carro / transporte público). Suporta mais de um local.
- **Conteúdo:** árvore com **checkbox à esquerda** (marca o tópico inteiro) e **expandir à direita** (mostra subtópicos literais, marcáveis um a um). Progresso é dado do USUÁRIO, por candidato+edital.
- **Datas:** calendário + tabela de status + botão **"Adicionar à agenda"** (exporta `.ics` para Google/Apple/Outlook).
- **Provas anteriores:** de 2020+; abas **Objetivas / Subjetivas / Orais**; cada concurso com **Prova + Gabarito** (objetiva) / **Padrão de resposta** (subjetiva) / **Espelho** (oral). **Nunca hospedar a gravação da oral** (proibido pela banca) — só pontos/critérios.

## Design
Verde bottle `#17553F` (justiça) · dourado `#B8862F` (conquista/concluído) · papel `#FBFAF6`. Tipografia: **Fraunces** (títulos) + **Inter** (corpo). O protótipo já reflete isso.

## Roadmap sugerido (primeiras tarefas)
1. Scaffold do monorepo: `backend/` (Python), `app/` (Flutter), `admin/` (web).
2. **Parser v1**: lê o PDF do edital e emite JSON que **passa** no `edital.schema.json`. Validar contra `pge_al.instance.json`. Focar primeiro em: identificação, cronograma (Anexo I), corte (16.32), árvore de conteúdo (item 17).
3. **Painel de revisão** da árvore (promover/rebaixar/agrupar tópico↔subtópico; travar publicação).
4. **App**: implementar as telas do protótipo consumindo a API.
5. **Radar**: monitorar a página da banca e sinalizar retificações.

## Comandos
Backend (Python 3.12+; venv em `backend/.venv`):
```powershell
cd backend
python -m venv .venv                          # só na primeira vez
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest          # roda os testes
```
Extras de API/admin (fase 3): `pip install -e ".[api,dev]"`; Postgres em produção: `".[api,postgres]"`.
Painel admin (dev):
```powershell
.\.venv\Scripts\python.exe scripts\seed_pge_al.py     # semeia o SQLite local com o piloto
.\.venv\Scripts\python.exe -m uvicorn --factory editais.admin.app:criar_app --port 8123
```
App Flutter (SDK em `%USERPROFILE%\flutter`, fora do PATH — usar caminho completo ou adicionar):
```powershell
cd app
%USERPROFILE%\flutter\bin\flutter analyze
%USERPROFILE%\flutter\bin\flutter test
%USERPROFILE%\flutter\bin\flutter run -d web-server --web-port 8124   # precisa do backend + edital publicado
```

## Publicação (Play Store)
Em andamento — guia completo em `docs/PUBLICAR.md`. Feito: painel admin trancado com Basic auth (`EDITAIS_ADMIN_USUARIO`/`EDITAIS_ADMIN_SENHA`; falha fechada em produção, dev usa admin/dev), normalização da URL do Postgres (`postgres://`→`postgresql+psycopg://`), `render.yaml` (backend + Postgres num blueprint), ícone do app (`flutter_launcher_icons`, verde `#17553F`) + assinatura de release configurada (`android/key.properties`, gitignored — Eduardo gera com `keytool` e guarda para sempre), rascunhos de `docs/politica-privacidade.md` e `docs/ficha-play-store.md`. **Nota: painel admin (código de revisão em si) fica por conta do Eduardo daqui pra frente — não mexer sem pedido explícito.** Falta: push no GitHub (Eduardo — sem `gh` CLI nem OAuth nesta sessão, push precisa ser feito com o Eduardo presente por causa do login interativo do Credential Manager), deploy no Render, apontar app para a URL de produção, gerar a chave `.jks` de verdade, build do `.aab`, capturas de tela, preencher os campos em colchetes dos rascunhos.

## Estado atual
- Scaffold do monorepo pronto: `backend/` (pacote `editais` com stubs documentados de parser/radar/api/admin/db) + `app/` (placeholder até instalar o Flutter SDK). Admin será Jinja2+HTMX dentro do backend; radar é módulo do backend.
- `backend/tests/test_contract.py` valida o golden `pge_al.instance.json` contra o schema — se quebrar, o contrato mudou; resolver antes de mexer no parser.
- **Parser v1 completo**: `assemble.parse_edital(pdf)` roda o pipeline inteiro (pdf_text → sectioner → todos os extratores), emite documento **válido contra o schema** + relatório de revisão + candidatas de corte. Golden test de ponta a ponta em `tests/test_golden.py` passa contra o PDF real (826 nós de conteúdo, 22 eventos, corte 2026-03-31, retificações ["no 2","no 3"]). Campos do radar (`ultima_retificacao_publicada`/`radar_desatualizado`) ficam de fora do assemble — quem preenche é o radar.
- **Painel de revisão pronto** (`admin/app.py` + `admin/servico.py` + `db/`): upload de PDF → rascunho travado; árvore com editar título/promover/rebaixar (edição fecha a trava de novo); confirmações de corte e datas; radar; publicar só com as 4 travas abertas. SQLite em `backend/data/` (gitignored), Postgres via `EDITAIS_DATABASE_URL`. API JSON (`/api/editais`) só expõe publicados. Toda mutação valida contra o schema antes de gravar. **Cuidado aprendido:** commit da sessão precisa acontecer ANTES do redirect (ver `_mutar` em `app.py`) — o commit no teardown da dependency corre contra o GET do redirect.
- **Relógio de estudo + calendário + grade de matérias** (`app/lib/tempo.dart`, telas `cronometro`/`datas`/`conteudo`): cronômetro com matéria selecionada (sessões agregadas por dia+matéria em prefs), modo foco (intent Android `ZEN_MODE_SETTINGS` → Não Perturbe; aviso no web), métricas dia/semana(2ª-feira)/mês/ano compartilháveis nos Stories; sessão no relógio também mantém a constância viva. Datas com `table_calendar` pt-BR + datas do candidato (FAB, deletáveis, entram no .ics). Conteúdo virou grade 2 colunas de quadros por matéria (nomes curtos, recolhidas) → toque abre a árvore. Insígnias: **46 em 6 categorias** (tela agrupada) — Progresso (6), Matérias (1/3/5/todas), Constância em escada cheia (3,7,14,21,30,45,75,90,120,150,180,210,240,270,300,330,365 — sem buraco 180→365), **Hábito 20/40/60** ("criação do hábito começa aos 20, consolida aos 40, fecha aos 60"), Horas (5→1000) e Pontos (500→15000). Grade de matérias com ícones minimalistas por palavra-chave (`iconeMateria` em `conteudo.dart`) e conteúdo centralizado.
- **Gamificação + rede de amigos + Stories** (`app/lib/gamificacao.dart`, `social_api.dart`, `compartilhar.dart`, telas `conquistas`/`amigos` + `backend/src/editais/api/social.py`): pontos/insígnias são **função pura do progresso** (recalculados, nunca acumulados); diário de estudo por dia alimenta a sequência (constância). API social com conta leve (apelido → código de amigo + token de aparelho, sem senha), amizade mútua, só o **resumo** do progresso sobe (pontos/percentual — a árvore marcada fica no aparelho), incentivos entre amigos (marcados lidos na leitura). Stories: card 9:16 renderizado como PNG (RepaintBoundary) + share sheet — variantes "hoje" (diário), edital completo e por matéria. Verificado ao vivo: registro, amizade por código, ranking com progresso, incentivo entregue, tela de conquistas.
- **App Flutter v1 pronto** (`app/lib/`): as 5 telas do protótipo consumindo `/api` — home, hub (selo do radar + card do corte), conteúdo (checkbox marca subárvore, expandir mostra subtópicos; progresso persistido por edital), datas (status + .ics via clipboard), dados da prova (ViaCEP + deep links Uber/99/Maps), provas anteriores (abas). Verificado no navegador contra o backend real. Polimentos pendentes: .ics como download/share nativo, deep link real do 99, coordenadas para os links.
- **Radar pronto** (`radar/core.py` + `radar/cebraspe.py`): `verificar(documento, fetcher)` compara retificações incorporadas × publicadas e grava os campos no documento. Só **retificação** trava a publicação; editais que não retificam (relação de isenção etc.) viram alerta informativo. Fetcher plugável por banca; o da Cebraspe separa parse de HTML do download (testes sem rede). Aceite do piloto passa: arquivo até nº 3 + site com nº 5 → travado, `ultima="no 5 (2026-06-08)"`. Falta o **serviço agendado** que chama o fetcher (cache, robots.txt, intervalo) — entra junto com a API/admin (fase 3 do roadmap).
- PDFs ficam em `editais/<orgao-uf-ano>/` (consolidado = fonte da verdade do parser) e provas anteriores em `provas/<orgao-uf-ano>/` — convenções nos READMEs de cada pasta. Os 10 PDFs do piloto já estão no repo; o consolidado (entrada do parser) é `editais/pge-al-2026/PGE_AL_2026_Edital_1_Abertura_Atualizado.pdf` (consolida até o nº 3; os nº 5–7 vieram depois → caso de teste do radar).
- Verificado no PDF real: 16.32/16.32.1 e o formato do item 17 batem com as premissas de `outline.py`/`corte.py`. Atenção para os próximos extractors: o item 17 tem preâmbulo (17.1 HABILIDADES) antes das disciplinas, e o Anexo I intercala linhas de horário ("Das 10 horas...") entre as datas.

## Convenções
- Código e commits podem ser em inglês; **conteúdo/labels do app em português (BR)**.
