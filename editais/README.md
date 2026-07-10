# Editais (PDFs oficiais)

Uma subpasta por concurso, no formato `orgao-uf-ano` (ex.: `pge-al-2026`).

Dentro de cada subpasta:

| Arquivo | O que é |
|---|---|
| `edital-01-2026-consolidado.pdf` | **Consolidado atualizado** ("versão atualizada conforme retificações") — é este que o parser lê. Fonte da verdade. |
| `edital-01-2026-original.pdf` | (opcional) O edital de abertura, como publicado. |
| `retificacao-02.pdf`, `retificacao-03.pdf`… | (opcional) Cada retificação individual, para rastreabilidade. |

Regras (ver CLAUDE.md):
- **Sempre trabalhar do consolidado.** Quando o radar detectar retificação nova
  não incorporada, baixar o consolidado atualizado da banca e **substituir** o
  arquivo — o nome fica o mesmo, o versionamento fica no Git.
- O parser extrai as `retificacoes_incorporadas` do próprio PDF (cabeçalho +
  marcadores no corpo); não é preciso registrar nada à mão.

## Concursos

- `pge-al-2026/` — PGE/AL, Procurador do Estado (Cebraspe, Edital 01/2026). **Piloto.**
