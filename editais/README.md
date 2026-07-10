# Editais (PDFs oficiais)

Uma subpasta por concurso, no formato `orgao-uf-ano` (ex.: `pge-al-2026`).

Padrão de nome dos arquivos: `ORGAO_UF_ANO_Edital_N_descricao.pdf`. O arquivo
**consolidado** — aquele com "Versão atualizada conforme retificação..." no
cabeçalho, sufixo `_Atualizado` — é o que o **parser lê**; os demais ficam
para rastreabilidade e para o radar.

Regras (ver CLAUDE.md):
- **Sempre trabalhar do consolidado.** Quando o radar detectar retificação nova
  não incorporada, baixar o consolidado atualizado da banca e **substituir** o
  arquivo `_Atualizado` — o versionamento fica no Git.
- O parser extrai as `retificacoes_incorporadas` do próprio PDF (cabeçalho +
  marcadores no corpo); não é preciso registrar nada à mão.

## Concursos

### `pge-al-2026/` — PGE/AL, Procurador do Estado (Cebraspe, Edital 01/2026). Piloto.

| Arquivo | O que é |
|---|---|
| `PGE_AL_2026_Edital_1_Abertura_Atualizado.pdf` | **Consolidado até o Edital nº 3 (6/5/2026)** — entrada do parser |
| `PGE_AL_2026_Edital_1_Abertura.pdf` | Edital de abertura original (31/3/2026) |
| `PGE_AL_2026_Edital_2_Relacao_provisoria_isencao.pdf` | Nº 2 (30/4) — isenção provisória |
| `PGE_AL_2026_Edital_3_Alteracoes_Edital_1.pdf` | Nº 3 (6/5) — retifica 9.2, 10.12.x (incorporado ao consolidado) |
| `PGE_AL_2026_Edital_4_Relacao_final_isencao.pdf` | Nº 4 (15/5) — isenção final |
| `PGE_AL_2026_Edital_5_Retificacao_subitens.pdf` | Nº 5 (8/6) — retifica 5.1.x, 6.4.8 (**não incorporado** → caso do radar) |
| `PGE_AL_2026_Edital_6_Reabertura_inscricao_isencao.pdf` | Nº 6 (25/6) — reabre inscrições/isenção |
| `PGE_AL_2026_Edital_7_Relacao_provisoria_isencao.pdf` | Nº 7 (30/6) — isenção provisória (reabertura) |
| `PGE_AL_2026_Comunicado_Retificacao_Lei_Estadual.pdf` | Comunicado (15/5) — anuncia retificação pela Lei Est. 9.716/2025 |
| `PGE_AL_2026_Respostas_impugnacoes_Edital_1.pdf` | Respostas às impugnações |
