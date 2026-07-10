# Como continuar no Claude Code (com o Fable 5)

Este pacote é o ponto de partida. Siga na ordem.

## 1. Instalar o Claude Code
O instalador nativo é o método recomendado (não precisa de Node.js).

- **macOS / Linux:**
  ```
  curl -fsSL https://claude.ai/install.sh | bash
  ```
- **Windows (PowerShell):**
  ```
  irm https://claude.ai/install.ps1 | iex
  ```
  (No Windows nativo, instale antes o **Git for Windows** — git-scm.com. Se aparecer aviso de PATH, feche e reabra o terminal.)

Confirme:
```
claude --version
```
Se algo falhar, rode `claude doctor`. Docs oficiais: code.claude.com/docs/en/setup

## 2. Entrar / autenticar
```
claude
```
Ele abre o navegador para login. Serve assinatura **Pro/Max/Team/Enterprise** ou conta do **Anthropic Console** (API paga). O plano gratuito não dá acesso ao Claude Code.

## 3. Abrir o projeto
Descompacte este pacote, depois:
```
cd pge-app
claude
```
O Claude Code lê o **CLAUDE.md** automaticamente ao iniciar — ou seja, ele já entra sabendo do projeto.

## 4. Selecionar o Fable 5
Dentro da sessão, rode:
```
/model
```
e escolha **Claude Fable 5**. Se ele não aparecer na lista, depende do seu acesso (plano/Console) — nesse caso use o Console ou defina o modelo pela configuração/variável de ambiente com o identificador `claude-fable-5`. Observação: o Fable 5 tem salvaguardas; em alguns temas a resposta pode vir do modelo Opus 4.8. Para desenvolvimento de app isso não deve atrapalhar.

## 5. Primeiro comando (cole isto na sessão)
> Leia o CLAUDE.md e a pasta `referencia/`. Não gere código ainda: me devolva (a) a stack que você propõe, (b) a estrutura de pastas do monorepo e (c) o plano do parser v1 que emite JSON válido contra `referencia/edital.schema.json`, usando `referencia/pge_al.instance.json` como caso de teste. Depois que eu aprovar, começamos pelo scaffold.

Isso mantém o seu jeito de trabalhar: aprovar antes de gerar. Quando aprovar, é só dizer "pode fazer o scaffold".

## Dica
Depois que existirem os primeiros arquivos de código, rode `/init` para o Claude Code preencher os comandos reais do projeto no CLAUDE.md.

## O que tem em `referencia/`
- `edital.schema.json` — contrato de dados (JSON Schema).
- `pge_al.instance.json` — edital PGE/AL real, já válido contra o schema (caso de teste).
- `ficha_campos_edital.md` — dicionário de campos + origem de cada um.
- `pge_al_edital_processado_v2.md` — edital PGE/AL processado por inteiro (referência de conteúdo).
- `proto_app_pge_al.html` — protótipo navegável das telas (abra no navegador).
