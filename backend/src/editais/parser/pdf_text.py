"""Extracao de texto limpo do PDF (PARSER_SPEC §2).

Pipeline: extrair por pagina -> remover cabecalho/rodape repetidos ->
de-hifenizar -> montar texto unico com indice de offsets por pagina.

Divergencia consciente da spec: usamos a ordem de leitura nativa do
pymupdf em vez de reordenar blocos por (y, x) — no PDF real da Cebraspe
(coluna unica) a ordem nativa e correta, e a reordenacao arriscaria
embaralhar as tabelas (quadro 7.1, Anexo I). Se outra banca vier com
layout quebrado, trocar aqui dentro sem afetar o resto do pipeline.
"""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass
class TextoExtraido:
    texto: str
    offsets_paginas: list[int]  # offset do inicio de cada pagina em `texto`


def extract_pages(path: str | Path) -> list[str]:
    """Retorna o texto bruto de cada pagina, em ordem de leitura."""
    with fitz.open(path) as doc:
        return [page.get_text() for page in doc]


def remover_cabecalho_rodape(paginas: list[str], limiar: float = 0.3) -> list[str]:
    """Remove linhas de topo/rodape que se repetem em >= `limiar` das paginas.

    So considera as 3 primeiras e 3 ultimas linhas de cada pagina — e onde
    cabecalho e rodape vivem; uma frase repetida no meio do texto (URL da
    banca, formula de praxe) nao pode ser descartada.
    """
    if len(paginas) < 4:
        return paginas

    contagem: Counter[str] = Counter()
    for pagina in paginas:
        linhas = [l.strip() for l in pagina.splitlines() if l.strip()]
        contagem.update(set(linhas[:3] + linhas[-3:]))
    ruido = {linha for linha, n in contagem.items() if n / len(paginas) >= limiar}

    limpas = []
    for pagina in paginas:
        linhas = pagina.splitlines()
        nao_vazias = [l.strip() for l in linhas if l.strip()]
        borda = set(nao_vazias[:3] + nao_vazias[-3:]) & ruido
        limpas.append("\n".join(l for l in linhas if l.strip() not in borda))
    return limpas


def de_hifenizar(texto: str) -> str:
    """Junta palavras quebradas por hifen no fim da linha.

    Linha seguinte comecando em minuscula -> palavra partida, remove o hifen
    ("respon-/sabilidade" -> "responsabilidade"). Comecando em maiuscula ->
    palavra composta, mantem o hifen ("Procuradoria-/Geral" ->
    "Procuradoria-Geral"). Digito ou outro caractere -> nao junta (pode ser
    um item novo).
    """
    resultado: list[str] = []
    for linha in texto.splitlines():
        linha = linha.rstrip()
        anterior = resultado[-1] if resultado else ""
        if anterior.endswith("-") and linha[:1].islower():
            resultado[-1] = anterior[:-1] + linha.lstrip()
        elif anterior.endswith("-") and linha[:1].isupper():
            resultado[-1] = anterior + linha.lstrip()
        else:
            resultado.append(linha)
    return "\n".join(resultado)


def montar_texto(paginas: list[str]) -> TextoExtraido:
    offsets = []
    partes = []
    posicao = 0
    for pagina in paginas:
        offsets.append(posicao)
        partes.append(pagina)
        posicao += len(pagina) + 1  # +1 pelo "\n" de junção
    return TextoExtraido(texto="\n".join(partes), offsets_paginas=offsets)


def texto_limpo(path: str | Path) -> TextoExtraido:
    """Pipeline completo: PDF -> texto unico limpo + offsets por pagina."""
    paginas = remover_cabecalho_rodape(extract_pages(path))
    return montar_texto([de_hifenizar(p) for p in paginas])
