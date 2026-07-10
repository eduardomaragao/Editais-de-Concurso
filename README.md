# App de acompanhamento de editais de concurso

Produto para candidatos de concursos públicos jurídicos (base de alunos de
[eduardoaragao.com](https://eduardoaragao.com)). O app pega um edital,
destrincha tudo (datas, corte de lei/jurisprudência, conteúdo programático)
e deixa o candidato acompanhar estudo e prazos.

Piloto: **PGE/AL — Procurador do Estado (Cebraspe, Edital 01/2026)**.

## Estrutura do monorepo

| Pasta | O que é |
|---|---|
| `referencia/` | Contrato de dados (`edital.schema.json`), caso de teste dourado (`pge_al.instance.json`), spec do parser e protótipo das telas. **Fonte da verdade — não editar sem combinar.** |
| `backend/` | Python: parser de editais (PDF → JSON), API (FastAPI), painel admin (Jinja2/HTMX) e radar de retificações. |
| `app/` | App mobile Flutter (iOS + Android). Placeholder até o Flutter SDK ser instalado. |

## Como rodar (backend)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

Documentação completa do projeto: [CLAUDE.md](CLAUDE.md).
Spec do parser: [referencia/PARSER_SPEC.md](referencia/PARSER_SPEC.md).
