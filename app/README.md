# App mobile (Flutter)

Placeholder — o Flutter SDK ainda não está instalado nesta máquina.

## Quando o SDK estiver instalado

1. Instalar: https://docs.flutter.dev/get-started/install/windows
2. Gerar o projeto **dentro desta pasta** (o `.` no final importa):

   ```powershell
   cd app
   flutter create --org com.eduardoaragao --project-name editais_app .
   ```

## O que o app implementa (ver `referencia/proto_app_pge_al.html`)

- **Edital (hub):** cartões de navegação + selo do radar + card do corte.
- **Dados da prova:** dia/horário do edital + local preenchido pelo candidato
  (CEP + sala) com deep links de Uber, 99 e Google Maps.
- **Conteúdo:** árvore com checkbox à esquerda e expandir à direita;
  progresso por candidato + edital.
- **Datas:** calendário + tabela de status + exportação `.ics`.
- **Provas anteriores:** abas Objetivas / Subjetivas / Orais (2020+).
  Nunca hospedar gravação de prova oral.

Design: verde bottle `#17553F` · dourado `#B8862F` · papel `#FBFAF6`.
Tipografia: Fraunces (títulos) + Inter (corpo). Labels em português (BR).
