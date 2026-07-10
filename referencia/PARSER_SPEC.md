# PARSER_SPEC — extração de edital (PDF → JSON)

**Objetivo:** transformar o PDF do edital consolidado em um objeto que **valida contra `edital.schema.json`**, deixando todos os campos de REVISÃO como rascunho (não publicado). Caso de teste dourado: o PDF da PGE/AL deve produzir algo equivalente a `pge_al.instance.json`.

**Como usar:** coloque este arquivo em `referencia/PARSER_SPEC.md` e peça ao Claude Code: *"implemente o parser conforme referencia/PARSER_SPEC.md, começando pelo outline.py e pelo corte.py, com testes."*

**Princípio geral:** o parser **nunca** decide sozinho nada crítico. Ele emite um rascunho com `conteudo_revisado=false` e `corte_conteudo.revisado`/datas marcados para conferência. Extrair muito e afirmar pouco.

---

## 1. Módulos (backend/parser/)

```
pdf_text.py       # extracao de texto + de-hifenizacao + remocao de cabecalho/rodape
sectioner.py      # divide em itens (1..17) e Anexos (I, II)
outline.py        # <<< nucleo: monta a arvore numerada do item 17
extractors/
  identificacao.py
  cronograma.py   # Anexo I
  corte.py        # <<< item 16.32 / referencia relativa -> data
  conteudo.py     # usa outline.py, aplica fases
  fases.py        # quadro 7.1 -> mapa disciplina->[P1,P2,...]
  isencoes.py
  dados_prova.py
versioning.py     # retificacoes incorporadas (cabecalho + marcadores)
radar.py          # monitora a banca e compara versoes
assemble.py       # compoe o dict final
validate.py       # jsonschema (draft 2020-12) contra edital.schema.json
tests/
```

Libs sugeridas: `pymupdf` (fitz) ou `pdfplumber` para texto; `jsonschema` para validação; `python-dateutil` para datas. Deixe a extração de PDF atrás de uma interface (`extract_pages(path) -> list[str]`) para poder trocar de engine.

---

## 2. pdf_text.py — texto limpo

1. Extrair por página, preservando ordem de leitura. Editais Cebraspe são de coluna única; ainda assim ordene blocos por (y, x).
2. **Remover cabeçalho/rodapé repetidos**: linhas que se repetem em ≥30% das páginas (ex.: "ESTADO DE ALAGOAS...", número de página) viram ruído — descarte.
3. **De-hifenização**: junte quebras do tipo `Procuradoria-\nGeral` → `Procuradoria-Geral` e palavra partida no fim da linha (`respon-\nsabilidade` → `responsabilidade`). Cuidado para **não** colar dois itens distintos: só junte quando a linha seguinte começa em minúscula.
4. Normalize espaços, mas **preserve o texto literal** dos títulos de conteúdo (é o que vai pro app).
5. Saída: um texto único por documento + índice de offsets por página (útil para `fonte`).

---

## 3. sectioner.py — achar as seções

Localize as âncoras dos itens numerados de 1º nível: `^\s*(\d{1,2})\s+[A-ZÀ-Ú]` no início de linha, mas confirme pela **sequência** (1,2,3…) para não confundir com subitens. Guarde os intervalos:

- `item[7]` (fases), `item[16]` (disposições finais — contém o corte), `item[17]` (conteúdo).
- `ANEXO I` (cronograma), `ANEXO II` (modelo de laudo — ignorar).

Cada extrator recebe só o seu trecho.

---

## 4. outline.py — a árvore do item 17 (núcleo)

### Formato de entrada
Dentro do item 17, cada disciplina começa com um cabeçalho em CAIXA ALTA terminado em `:` — ex.: `DIREITO ADMINISTRATIVO:` — seguido de um outline plano:

```
1 Estado. 1.1 Funções. 1.2 Poderes. ... 7 Atos administrativos. 7.1 Elementos. ...
12 Licitações e contratos administrativos: Lei nº 14.133/2021. ... 21 Responsabilidade civil do Estado.
```

Alguns títulos têm marcador de retificação depois: `(Retificado por meio do Edital nº 3 ...)` — extraia para `versioning`, remova do título.

### O problema difícil
Números de **lei** dentro dos títulos (`Lei nº 14.133/2021`, `6.830/1980`, `art. 5º`) parecem marcadores de outline (`14.133`). Não dá para dividir só por regex de `\d+\.\d+`.

### Solução: validar pelo "próximo número esperado"
Os marcadores do outline são **sequenciais e hierárquicos**; números de lei não. Então aceite um candidato como marcador **apenas se ele for uma continuação plausível** do estado atual.

```
def parse_disciplina(texto, materia_id):
    # candidatos: r'(?<![\d.])(\d+(?:\.\d+){0,3})\s+(?=[A-ZÀ-Ú])'
    estado = []          # caminho atual, ex.: [7, 1]
    aceitos = []         # (num_tuple, pos_inicio)
    for m in candidatos(texto):
        num = tuple(int(x) for x in m.group(1).split('.'))
        if numero_valido(num, estado):
            aceitos.append((num, m.start()))
            estado = list(num)         # avanca o estado
    # o titulo de cada aceito vai do fim do seu marcador ate o inicio do proximo aceito
    # limpar: strip de '.' final, remover marcador de retificacao
    return montar_nos(aceitos, texto, materia_id)

def numero_valido(num, estado):
    d = len(num)
    if not estado:
        return num == (1,)                       # comeca em 1
    if d == len(estado) + 1:                      # primeiro filho: X.1
        return list(num[:-1]) == estado and num[-1] == 1
    if d <= len(estado):                          # irmao ou irmao-de-ancestral
        prefixo = list(num[:d-1])
        return prefixo == estado[:d-1] and num[-1] == estado[d-1] + 1
    return False                                  # pulo grande -> nao e outline (ex.: lei)
```

Assim `14.133` depois de, digamos, o item `12` **não** é "o próximo esperado" (esperado seria `13` ou `12.1`), então fica no título. 

### Mapeamento para o schema
- disciplina → nó `materia` (`parent_id=null`).
- profundidade 1 (ex.: `7`) → `topico`, `parent_id = materia`.
- profundidade ≥2 (ex.: `7.1`, `4.1.1`) → `subtopico`, `parent_id = nó imediatamente acima na hierarquia`.
- `ordem` = o próprio número (para `topico`, `num[0]`; para subtópico, o último componente).
- `titulo` = **texto literal** (sem o número, sem `.` final).
- `id` sugerido: `f"{materia_id}-{'.'.join(map(str,num))}"`.

### Casos de teste (Direito Administrativo)
- Existe `topico` "Atos administrativos" com `ordem=7` e um `subtopico` "Vinculação e discricionariedade".
- Existe `topico` "Responsabilidade civil do Estado" com `ordem=21` e **sem filhos**.
- "Licitações e contratos administrativos: Lei nº 14.133/2021" é **um** tópico (o `14.133` **não** virou nó).

---

## 5. corte.py — corte de lei/jurisprudência

Procure no item 16 (e varra o doc inteiro como fallback) dois padrões:

- **Legislação:** `legisla[çc][ãa]o.*?vigente\s+na\s+data\s+da\s+(primeira\s+)?publica[çc][ãa]o\s+deste\s+edital`
- **Jurisprudência:** `jurisprud[êe]ncia.*?publicad[ao]s?\s+at[ée]\s+a\s+data\s+de\s+publica[çc][ãa]o\s+deste\s+edital`
- **Explícito (outros editais):** `at[ée]\s+(\d{2}/\d{2}/\d{4})`

Regras:
- Se casar o padrão relativo → `forma="relativa"`, `referencia="data da (primeira) publicação do edital"`, e **resolva** `legislacao_ate` e `jurisprudencia_ate` = `edital.publicacao`.
- Se disser "primeira publicação" → `afetado_por_retificacao=false` (o corte trava na 1ª publicação; retificações não movem).
- Se for data explícita → `forma="explicita"`, use a data literal.
- Se nada casar → `informado=false`.
- Sempre preencha `fonte` (ex.: "16.32 / 16.32.1") e `trecho` (a frase literal).
- **Ambiguidade real** (data do edital vs. publicação no DOE): não escolha sozinho. Resolva para a data do edital, mas **marque para revisão** — deixe as duas candidatas num campo interno para a tela de conferência.

Aceite: no PGE/AL → `legislacao_ate = jurisprudencia_ate = 2026-03-31`, `forma="relativa"`, `afetado_por_retificacao=false`.

---

## 6. cronograma.py — Anexo I

1. Isole o bloco entre `ANEXO I` e `ANEXO II`.
2. Leia as linhas como pares `Atividade | Datas previstas`.
3. **Datas**: aceite `DD/MM/AAAA`, `DD a DD/MM/AAAA`, `DD/MM a DD/MM/AAAA` → `inicio`/`fim`.
4. **tipo**: mapeie por palavras-chave (case-insensitive), na ordem:
   - "impugna" → `impugnacao`; "isen" → `isencao`; "inscri" → `inscricoes`; "pagamento" → `pagamento`;
   - "prova objetiva" → `prova_objetiva`; "discursiva" → `provas_discursivas`; "oral" → `prova_oral`;
   - "t[íi]tulos" → `titulos`; "recurso" → `recurso`; "local" → `locais_prova`;
   - "resultado final" → `resultado_final`; "resultado" → `resultado_provisorio`; senão → `outro`.
5. Guarde `titulo` = texto original da atividade; `fonte` = "Anexo I".

---

## 7. fases.py — quadro 7.1

1. No item 7.1, cada prova (P1..P4) lista as áreas de conhecimento.
2. Normalize nomes (`lower`, sem acento) para casar com os cabeçalhos do item 17. Atenção aos **agrupamentos**: 7.1 diz "Direito Civil e Empresarial" e "Direito do Trabalho e Previdenciário na Administração Pública", enquanto o item 17 traz "DIREITO CIVIL", "DIREITO EMPRESARIAL", etc.
3. Produza `mapa: disciplina_normalizada -> set(fases)`. Onde o casamento for agrupado/ambíguo, **marque para revisão** (não descarte).
4. `conteudo.py` aplica `no["fases"]` a cada nó `materia` (e propaga aos filhos se quiser).

Aceite: Administrativo → [P1,P2,P4]; Ambiental → [P1]; Processual do Trabalho → [P1].

---

## 8. identificacao.py / dados_prova.py / isencoes.py

- **identificacao**: órgão, cargo (linha do título), banca (Cebraspe), número/data (cabeçalho), `publicacao` (data do edital — guarde também a do DOE se aparecer), vagas (quadro item 4: AC/PCD/PPIQ), remuneração, taxa (item 6.1), `local_fases` (item 1.3), `validade_anos` (item 16.29 → 2).
- **dados_prova.fases**: itens 7.2–7.4 e 9.1/10.3 → duração/turno/formato/questões por fase. `locais` fica vazio (é USUÁRIO).
- **isencoes**: item 6.4.8 → `hipoteses` (as "Nª POSSIBILIDADE"); período vem do Anexo I.

---

## 9. versioning.py + radar.py

**versioning (do próprio PDF):**
- Cabeçalho: `Versão atualizada conforme retificação constante do Edital nº (\d+)` → base das `retificacoes_incorporadas`.
- Varra o corpo por `\(Retificado por meio do Edital nº (\d+)` → some ao conjunto. Resultado: lista ordenada (ex.: ["nº 2","nº 3"]).

**radar (serviço separado, agendado):**
- `fetch_editais(banca_url) -> list[{numero, data, url}]`. A página da Cebraspe é dinâmica; prefira o índice de arquivos/edital de abertura "atualizado conforme retificações" ou um endpoint estável. Deixe o fetcher plugável por banca.
- `ultima_retificacao_publicada` = maior número visto no site.
- `radar_desatualizado = (ultima_publicada > max(retificacoes_incorporadas))`.
- Quando `true`: **trava a publicação** do edital e emite alerta ("existe Ed. nº X não incorporado; reenvie o consolidado").
- Também descobre **novos editais** de interesse (lista de órgãos/cargos que o Eduardo acompanha) e notifica.
- Seja educado com a banca: cache, `robots.txt`, intervalo entre requisições; nunca burlar proteção.

Aceite (piloto): arquivo consolida até nº 3; se o site expõe nº 5 → `radar_desatualizado=true`.

---

## 10. assemble.py + validate.py

1. `assemble()` compõe o dict: `edital` (com `conteudo_revisado=false`, `corte_conteudo`, campos de versão/radar), `cronograma`, `dados_prova`, `conteudo`, `provas_anteriores=[]` (CURADORIA), `isencoes`, `links`.
2. `validate()` roda `Draft202012Validator` contra `edital.schema.json`. **Falha = erro fatal do parser** (não emitir rascunho inválido).
3. Emitir também um relatório de revisão: lista dos nós/campos marcados para conferência (árvore, corte, datas de prova, agrupamentos de fase).

---

## 11. Critérios de aceite (testes)

1. `parse(pdf_pge_al)` → JSON **válido** contra o schema.
2. Golden test: comparar campos-chave com `pge_al.instance.json` (identificação, corte resolvido em 2026-03-31, matérias e fases).
3. Unit `outline.py`: os três casos do §4 (Atos administrativos 7 + subtópico; Responsabilidade civil 21 sem filhos; Licitações 14.133 não quebrada). Inclua um caso sintético com `art. 5º` e `Lei 9.784/1999` no meio de um título.
4. Unit `corte.py`: frase relativa → data resolvida + `afetado_por_retificacao=false`; frase com data explícita → `forma="explicita"`.
5. Unit `versioning.py`: cabeçalho "nº 3" + marcadores → `["nº 2","nº 3"]`.
6. Todo campo de REVISÃO sai com flag de não-revisado; nada é publicável sem ação humana.

---

## 12. Ordem de implementação sugerida
1. `pdf_text.py` + `sectioner.py` (com testes de fumaça no PDF real).
2. `outline.py` + testes (é o mais arriscado — faça primeiro).
3. `corte.py` + testes.
4. `cronograma.py`, `fases.py`, `identificacao.py`.
5. `assemble.py` + `validate.py` → primeiro JSON válido de ponta a ponta.
6. `versioning.py`; depois `radar.py`.
