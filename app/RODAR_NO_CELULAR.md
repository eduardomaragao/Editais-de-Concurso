# Rodar o app no celular — passo a passo

> Vale para **Android**. iPhone só compila num Mac — se o seu celular for
> iPhone, pare aqui e me avise.
> O celular e o PC precisam estar no **mesmo Wi-Fi**.

## Parte 0 — Colocar o `flutter` no PATH (uma vez só, 1 min)

Abra o **PowerShell** (menu Iniciar → digite "PowerShell" → Enter) e cole:

```powershell
[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path','User') + ';' + $env:USERPROFILE + '\flutter\bin', 'User')
```

**Feche e abra o PowerShell de novo** (senão não pega). Teste: `flutter --version`
deve mostrar "Flutter 3.44.6".

## Parte 1 — Instalar o Android Studio (uma vez só, ~30 min)

O Flutter precisa do "Android SDK", que vem com o Android Studio.

1. Acesse https://developer.android.com/studio e clique no botão verde
   **Download Android Studio**. Aceite os termos e baixe (~1,2 GB).
2. Rode o instalador baixado: **Next → Next → Install → Finish**
   (não desmarque nada).
3. O Android Studio abre um assistente na primeira vez:
   escolha **Standard** → Next → na tela de licenças, clique em cada item da
   lista à esquerda e marque **Accept** → Finish. Ele vai baixar o SDK
   sozinho (~10 min). Quando terminar, **pode fechar o Android Studio** —
   você nunca mais precisa abri-lo.
4. De volta ao PowerShell, aceite as licenças para o Flutter:
   ```powershell
   flutter doctor --android-licenses
   ```
   Vai aparecer texto de licença várias vezes — digite `y` e Enter em todas.
5. Confira:
   ```powershell
   flutter doctor
   ```
   A linha **Android toolchain** tem que estar com `[√]`. (A linha
   "Visual Studio" com X pode ignorar — é só para app de Windows desktop.)

## Parte 2 — Preparar o celular (uma vez só, 5 min)

1. **Ativar o modo desenvolvedor:** Configurações → **Sobre o telefone** →
   toque **7 vezes seguidas** em **Número da versão** (em Samsung fica em
   Sobre o telefone → Informações do software → **Número de compilação**).
   Vai aparecer "Você agora é um desenvolvedor!".
2. Configurações → **Opções do desenvolvedor** (apareceu agora) → ligue
   **Depuração USB**.
3. Conecte o celular no PC **com cabo USB**. No celular vai pular a pergunta
   **"Permitir depuração USB?"** → marque **Sempre permitir deste
   computador** → **Permitir**. (Se o celular perguntar o tipo de conexão,
   escolha "Transferência de arquivos".)
4. Confira no PowerShell:
   ```powershell
   flutter devices
   ```
   O seu celular tem que aparecer na lista. Se não aparecer: troque o cabo
   (muitos cabos são só de carga, não passam dados).

## Parte 3 — Ligar o backend (toda vez que for testar)

Num PowerShell:

```powershell
cd "C:\Users\eduar\Projects\Aplicativo Editais\backend"
.\.venv\Scripts\python.exe scripts\seed_pge_al.py --publicar
.\.venv\Scripts\python.exe -m uvicorn --factory editais.admin.app:criar_app --host 0.0.0.0 --port 8123
```

- O `--host 0.0.0.0` deixa o celular enxergar o servidor. **Deixe essa
  janela aberta** — o servidor roda nela.
- Na primeira vez o **Firewall do Windows** vai perguntar → clique
  **Permitir acesso** (redes privadas).
- **Teste antes de continuar:** no navegador **do celular**, abra
  `http://192.168.0.59:8123` — tem que aparecer o painel de editais.
  Se não abrir: ou o firewall bloqueou, ou o celular está em outro Wi-Fi,
  ou o IP do PC mudou (veja o box abaixo).

> **Qual é o IP do meu PC?** No PowerShell: `ipconfig` → procure
> "Adaptador de Rede sem Fio Wi-Fi" → **Endereço IPv4**. Hoje é
> `192.168.0.59`, mas pode mudar quando o roteador reinicia — se mudar,
> troque o número nos comandos.

## Parte 4 — Rodar o app no celular

Num **segundo** PowerShell (deixe o do backend rodando):

```powershell
cd "C:\Users\eduar\Projects\Aplicativo Editais\app"
flutter run --dart-define=API_BASE=http://192.168.0.59:8123
```

- A **primeira** compilação demora bastante (5–15 min — ele baixa o Gradle
  e compila tudo). Das próximas vezes leva segundos.
- O app **abre sozinho no celular** quando termina.
- Com o terminal aberto: tecle **r** para recarregar depois de mudar
  código, **q** para encerrar.

## Deu errado?

| Sintoma | Causa provável |
|---|---|
| `flutter` não é reconhecido | Parte 0: PATH — feche e reabra o PowerShell |
| Celular não aparece no `flutter devices` | Cabo só de carga (troque), ou depuração USB desligada, ou não deu "Permitir" no celular |
| App abre mas fica em erro / lista vazia | Backend desligado, IP errado/mudou, ou firewall — refaça o teste do navegador do celular (Parte 3) |
| "Unable to locate Android SDK" | Parte 1 não terminou — abra o Android Studio e complete o assistente |
