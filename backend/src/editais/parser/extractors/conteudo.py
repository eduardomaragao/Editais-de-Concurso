"""Conteudo programatico (PARSER_SPEC §4/§7): usa outline.py para montar a
arvore do item 17 e aplica as fases do quadro 7.1 a cada no materia.
"""

from dataclasses import dataclass, field

from editais.parser import outline
from editais.parser.extractors import fases
from editais.parser.sectioner import Secoes


@dataclass
class ConteudoResultado:
    nos: list[dict]
    marcadores_retificacao: list[str] = field(default_factory=list)
    pendencias: list[str] = field(default_factory=list)


def extrair_conteudo(secoes: Secoes) -> ConteudoResultado:
    item17 = secoes.itens.get(17, "")
    disciplinas = outline.parse_item17(item17)
    if not disciplinas:
        return ConteudoResultado(
            nos=[],
            pendencias=["Nenhuma disciplina encontrada no item 17 — revisar extracao."],
        )

    casamento = fases.casar_fases(
        fases.extrair_areas_por_fase(secoes.itens.get(7, "")),
        [d.materia["titulo"] for d in disciplinas],
    )

    nos: list[dict] = []
    marcadores: list[str] = []
    for disciplina in disciplinas:
        fases_da_materia = casamento.fases_por_materia.get(disciplina.materia["titulo"])
        if fases_da_materia:
            disciplina.materia["fases"] = fases_da_materia
        nos.extend(disciplina.nos)
        marcadores.extend(disciplina.marcadores_retificacao)

    return ConteudoResultado(
        nos=nos, marcadores_retificacao=marcadores, pendencias=casamento.pendencias
    )
