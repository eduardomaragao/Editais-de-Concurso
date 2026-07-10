# App mobile (Flutter)

App do candidato — consome a API do backend (só editais **publicados**).

## Rodar em dev

O backend precisa estar de pé com um edital publicado:

```powershell
cd ..\backend
.\.venv\Scripts\python.exe scripts\seed_pge_al.py --publicar
.\.venv\Scripts\python.exe -m uvicorn --factory editais.admin.app:criar_app --port 8123
```

Depois o app (SDK em `%USERPROFILE%\flutter`):

```powershell
cd app
%USERPROFILE%\flutter\bin\flutter run -d web-server --web-port 8124
# ou num emulador/dispositivo: flutter run
```

Backend em outro endereço: `flutter run --dart-define=API_BASE=https://...`

## Verificação

```powershell
flutter analyze
flutter test
```

## Estrutura

| Arquivo | O que é |
|---|---|
| `lib/modelos.dart` | Acesso tipado ao documento do contrato + árvore aninhada |
| `lib/api.dart` | Cliente da API (`/api/editais`) |
| `lib/armazenamento.dart` | Dados do USUÁRIO no aparelho: progresso + locais de prova |
| `lib/ics.dart` | Exportação do cronograma (.ics) e status de eventos |
| `lib/tema.dart` | Identidade visual (verde `#17553F` · dourado `#B8862F` · papel `#FBFAF6`, Fraunces + Inter) |
| `lib/telas/` | Home · Hub do edital · Conteúdo · Datas · Dados da prova · Provas anteriores |

Regras de produto no app:
- **Conteúdo:** checkbox à esquerda marca o tópico inteiro; expandir à direita
  mostra subtópicos marcáveis um a um. Progresso por candidato + edital.
- **Dados da prova:** local é do candidato (CEP via ViaCEP + sala), com deep
  links de Uber, 99 e Google Maps (carro/transporte público). Vários locais.
- **Provas anteriores:** abas Objetivas/Subjetivas/Orais; na oral, nunca a
  gravação — só pontos e espelho.
- **Radar:** selo no hub avisa quando há retificação não incorporada.
