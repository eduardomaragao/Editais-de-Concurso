# Publicar na Play Store — guia passo a passo

Ordem: (1) subir no GitHub → (2) hospedar o backend no Render →
(3) apontar o app para produção e empacotar → (4) ficha da Play Store.
As partes 3 e 4 o Claude faz com você; comece pelas 1 e 2.

> **Conceito:** a Play Store distribui o **app** (roda no celular). O
> **backend** (guarda editais, contas, ranking) mora no Render, na
> internet. São servidores diferentes.

---

## Parte 1 — Subir o projeto no GitHub

Você já tem conta. No site https://github.com/new crie um repositório
**privado** (ex.: `app-editais`), **sem** marcar "Add a README".

Depois, no PowerShell, dentro da pasta do projeto:

```powershell
cd "C:\Users\eduar\Projects\Aplicativo Editais"
git remote add origin https://github.com/SEU_USUARIO/app-editais.git
git push -u origin main
```

(Se pedir login, use seu usuário e um **token** — o GitHub não aceita
mais senha no push. Se aparecer erro de token, me avise que te explico.)

## Parte 2 — Hospedar o backend no Render

1. Entre em https://render.com (pode logar com o GitHub).
2. **New** → **Blueprint** → conecte sua conta GitHub → escolha o
   repositório `app-editais`. O Render lê o arquivo `render.yaml` que já
   está no projeto e propõe criar **dois recursos**: o backend e o banco
   Postgres. Clique **Apply**.
3. Espere o primeiro deploy (alguns minutos). Quando ficar verde:
   - Anote o **endereço** do backend, algo como
     `https://editais-backend.onrender.com`.
   - Pegue a **senha do admin**: no serviço `editais-backend` →
     aba **Environment** → variável `EDITAIS_ADMIN_SENHA` → **Reveal**.
     Guarde essa senha (é o login do painel: usuário `admin`).
4. Teste: abra `https://SEU-BACKEND.onrender.com` no navegador. Vai pedir
   usuário/senha (o do passo 3) e mostrar o painel de revisão, vazio.
5. No painel, **suba o PDF do edital**, revise e publique — igual você já
   fez no seu PC. Agora está no ar.

> **Pegadinha do plano grátis:** o backend "dorme" após ~15 min sem uso e
> demora ~30s para acordar na primeira visita. Para produção de verdade,
> troque `plan: free` por `starter` no `render.yaml` (sempre ligado).
> O Postgres grátis também tem prazo — confira os limites atuais do Render.

## Parte 3 — Apontar o app para produção e empacotar (Claude faz com você)

Quando o backend estiver no ar e você me passar o **endereço**:

- Aponto o app para `https://SEU-BACKEND.onrender.com`.
- Gero o **ícone** do app.
- Configuro a **assinatura**. Você roda um comando que cria a **chave**
  (um arquivo `.jks` + senhas) e **guarda para sempre** — se perder,
  nunca mais atualiza o app na loja. NUNCA suba essa chave no GitHub.
- Gero o pacote **`.aab`** (Android App Bundle) para enviar à loja.

## Parte 4 — Ficha da Play Store (Claude rascunha, você revisa)

- **Política de privacidade** (obrigatória — o app tem contas e coleta
  progresso). Precisa estar hospedada numa URL (dá para servir pelo
  próprio backend).
- Descrição, categoria, e **capturas de tela** (tiro do app rodando).
- Questionário de classificação e de segurança de dados do Google.
- Enviar o `.aab`, escolher "produção", e aguardar a **revisão do
  Google** (de horas a alguns dias na primeira vez).

## Contas e custos (resumo)

| Item | Custo | Quem faz |
|---|---|---|
| Google Play Console | US$ 25 (uma vez) + verificação de identidade | Você |
| Render (backend + Postgres) | Grátis para começar; ~US$ 7+/mês "sempre ligado" | Você cria; Claude configurou |
| Domínio próprio | Opcional (o `.onrender.com` já vem grátis) | Depois, se quiser |
| Chave de assinatura | Grátis | Você gera e guarda |
