"""Retificacoes incorporadas ao PDF (PARSER_SPEC §9).

Le o cabecalho ("Versao atualizada conforme retificacao constante do
Edital no N, de D de MES de AAAA") e os marcadores no corpo ("(Retificado
por meio do Edital no N ...)").

Convencao (segue o golden): o Edital no 1 e o proprio edital de abertura,
entao um consolidado "ate o no 3" incorpora os editais 2..3 — mesmo que
algum deles nao seja uma retificacao textual. Os campos sintetizados saem
em ASCII ("no 3", "consolidado ate...") para casar com o golden.
"""

import re
from dataclasses import dataclass, field

from editais.parser.util import MESES, norm_ascii

RE_CABECALHO_VERSAO = re.compile(
    r"Vers[ãa]o atualizada conforme retifica[çc][ãa]o constante do Edital "
    r"n[ºo°]\s*(\d+)[^,]*,\s*de\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)
RE_MARCADOR = re.compile(
    r"\(\s*Retificad[oa] por meio do Edital n[ºo°]\s*(\d+)", re.IGNORECASE
)


@dataclass
class VersaoExtraida:
    versao_arquivo: str | None
    retificacoes_incorporadas: list[str]
    pendencias: list[str] = field(default_factory=list)


def extrair_versao(texto: str) -> VersaoExtraida:
    pendencias: list[str] = []
    numeros: set[int] = {int(n) for n in RE_MARCADOR.findall(texto)}

    versao_arquivo = None
    m = RE_CABECALHO_VERSAO.search(" ".join(texto[:3000].split()))
    if m:
        base, dia, mes_nome, ano = m.groups()
        numeros.update(range(2, int(base) + 1))
        mes = MESES.get(norm_ascii(mes_nome))
        if mes:
            versao_arquivo = (
                f"consolidado ate Edital no {int(base)} "
                f"({int(ano):04d}-{mes:02d}-{int(dia):02d})"
            )
        else:
            versao_arquivo = f"consolidado ate Edital no {int(base)}"
            pendencias.append(f"Mes nao reconhecido no cabecalho de versao: {mes_nome!r}")
    else:
        pendencias.append(
            "Cabecalho 'Versao atualizada conforme retificacao...' nao encontrado — "
            "confirmar se o PDF e mesmo o consolidado."
        )

    return VersaoExtraida(
        versao_arquivo=versao_arquivo,
        retificacoes_incorporadas=[f"no {n}" for n in sorted(numeros)],
        pendencias=pendencias,
    )
