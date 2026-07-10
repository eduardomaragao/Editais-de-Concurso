"""Extracao de texto limpo do PDF (PARSER_SPEC §2).

Responsabilidades: extrair por pagina em ordem de leitura, remover
cabecalho/rodape repetidos (linhas presentes em >=30% das paginas),
de-hifenizar quebras de linha (so quando a linha seguinte comeca em
minuscula) e preservar o texto literal dos titulos.

A extracao fica atras desta interface para permitir trocar de engine
(pymupdf <-> pdfplumber) sem afetar o resto do pipeline.
"""

from pathlib import Path


def extract_pages(path: str | Path) -> list[str]:
    """Retorna o texto bruto de cada pagina, em ordem de leitura."""
    raise NotImplementedError
