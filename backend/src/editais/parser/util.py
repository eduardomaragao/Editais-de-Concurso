"""Utilidades compartilhadas pelos extratores."""

import unicodedata

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11,
    "dezembro": 12,
}

NUMEROS_POR_EXTENSO = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
}


def norm_ascii(s: str) -> str:
    """minusculas, sem acentos, espacos colapsados — para comparacoes."""
    ascii_ = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(ascii_.lower().split())


def extenso_para_int(palavra: str) -> int | None:
    palavra = norm_ascii(palavra)
    if palavra.isdigit():
        return int(palavra)
    return NUMEROS_POR_EXTENSO.get(palavra)
