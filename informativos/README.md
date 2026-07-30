# Informativos de jurisprudência

Base bruta para o **banco de decisões** extraído dos informativos dos tribunais
superiores. Uma subpasta por tribunal (`stf/`, futuramente `stj/`).

Fluxo (mesmo modelo dos editais — human-in-the-loop):

1. **Eduardo baixa** os arquivos oficiais no portal do tribunal e coloca em
   `<tribunal>/brutos/` — usando o script `stf/baixar.py` (ver abaixo), que
   faz o download em lote. O ambiente remoto **não tem acesso** ao site do STF
   (bloqueio de rede + anti-robô), então o download roda sempre na máquina
   local.
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

## Baixar em lote — `stf/baixar.py`

Ninguém precisa abrir edição por edição. O script usa só a biblioteca padrão
do Python (nada para instalar) e baixa tudo de uma vez, pulando o que já
existe — dá para interromper e retomar.

```powershell
cd informativos\stf

# 1) Ver o que ele encontra, sem baixar nada:
python baixar.py --listar

# 2) Baixar de verdade:
python baixar.py
```

Se a listagem oficial mudar de formato e o passo 1 não achar nada, há dois
caminhos alternativos:

```powershell
# A) Modo direto: monta a URL de cada edição pelo número, sem ler a listagem.
#    Números que não existirem são só reportados e ignorados — pode usar uma
#    faixa generosa. Rode --listar antes para descobrir os números de 2023+.
python baixar.py --padrao --min 1080 --max 1250

# B) Plano B manual: abra a página de Edições Anteriores no navegador,
#    salve com Ctrl+S ("Página da web, somente HTML") e aponte o arquivo:
python baixar.py --pagina "Edicoes_Anteriores.html"
```

Detalhes: pausa de 1,5 s entre requisições (educado com o servidor), 4
tentativas com espera crescente em erro de rede, e preferência de formato
`docx > doc > rtf > htm > pdf`. Os arquivos saem como
`brutos/informativo-NNNN.docx`.

Depois de baixar, é só commitar a pasta `brutos/` e me avisar — daí eu sigo
com o inventário, o schema do registro de decisão e o parser.
