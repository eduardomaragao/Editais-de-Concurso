# Informativos de jurisprudência

Base bruta para o **banco de decisões** extraído dos informativos dos tribunais
superiores. Uma subpasta por tribunal (`stf/`, futuramente `stj/`).

Fluxo (mesmo modelo dos editais — human-in-the-loop):

1. **Eduardo baixa** os arquivos oficiais no portal do tribunal e coloca em
   `<tribunal>/brutos/`. O ambiente remoto **não tem acesso** ao site do STF
   (bloqueio de rede + anti-robô), então o download é sempre manual/local.
2. O **parser** extrai cada julgado (número do informativo, data, classe e
   número do processo, órgão julgador, ramo do direito, tese/resumo) para o
   banco de decisões.
3. **Revisão** antes de publicar, como no restante do projeto.

## `stf/brutos/` — arquivos aceitos

- **`.docx`** — preferido para as edições novas (o portal oferece "versão
  Word"; é XML estruturado, extrai limpo).
- **`.htm`/`.html`** — edições antigas que só existem como página; salvar com
  Ctrl+S → "Página da web, somente HTML".
- **`.pdf`** — último recurso, quando não houver outro formato.

Nome ideal: `informativo-NNNN.docx` (ex.: `informativo-1123.docx`). Se o site
entregar com outro nome, **pode soltar na pasta do jeito que veio** — a
renomeação/organização é automatizável depois, pelo conteúdo do arquivo.

Escopo inicial: edições de **2023 a 2026**.
