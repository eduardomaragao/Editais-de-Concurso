"""Dados por fase de prova (PARSER_SPEC §8).

Fontes no edital: quadro 7.1 (lista de fases, tipo, numero de questoes de
P1/P2), itens 7.2-7.4 (duracao e turno), item 8 (formato da objetiva),
item 9 (P2/P3: questoes, linhas), item 10 (oral: duracao e questoes),
item 12 (titulos: pontuacao maxima). `locais` sai vazio — e USUARIO.
"""

import re
from dataclasses import dataclass, field

from editais.parser.extractors.fases import recortar_quadro
from editais.parser.sectioner import Secoes
from editais.parser.util import extenso_para_int, norm_ascii

RE_ANCORA_FASE = re.compile(
    r"(Prova objetiva|Prova discursiva|Prova oral|Avalia[çc][ãa]o de t[íi]tulos)"
    r"\s*\((P\d)\)"
)
TIPO_POR_ROTULO = {
    "prova objetiva": "objetiva",
    "prova discursiva": "discursiva",
    "prova oral": "oral",
    "avaliacao de titulos": "titulos",
}
RE_QUESTOES_LINHA = re.compile(r"^(\d{1,3})(?:\s+quest[õo]es)?\s*$")

RE_DURACAO_P1 = re.compile(
    r"prova objetiva ter[áa] a dura[çc][ãa]o de (\d+) horas?.{0,200}?"
    r"turno da (manh[ãa]|tarde|noite)",
    re.IGNORECASE,
)


def _re_duracao_discursiva(fase: str) -> re.Pattern:
    return re.compile(
        rf"prova discursiva \({fase}\) ter[áa] a dura[çc][ãa]o de (\d+) horas?"
        rf".{{0,200}}?turno da (manh[ãa]|tarde|noite)",
        re.IGNORECASE,
    )


RE_FORMATO_P1 = re.compile(r"ser[ãa]o do tipo ([^.;]+?)(?=,\s*sendo|[.;])")
RE_P2 = re.compile(
    r"P2:\s*(\w+)\s+quest[õo]es.{0,200}?at[ée]\s+(\d+)\s+linhas", re.IGNORECASE
)
RE_P3 = re.compile(
    r"P3:\s*reda[çc][ãa]o de uma (.+?),?\s*de at[ée]\s+(\d+)\s+linhas", re.IGNORECASE
)
RE_ORAL_DURACAO = re.compile(
    r"prova oral ter[áa] dura[çc][ãa]o de at[ée]\s+(\d+)\s+minutos", re.IGNORECASE
)
RE_ORAL_QUESTOES = re.compile(r"responder as (\w+) quest[õo]es", re.IGNORECASE)
RE_ORAL_MINUTOS_POR_QUESTAO = re.compile(
    r"sendo (\d+) minutos para a resposta", re.IGNORECASE
)
RE_TITULOS_MAX = re.compile(
    r"avalia[çc][ãa]o de t[íi]tulos valer[áa]\s*(\d+(?:,\d{2})?)\s*pontos",
    re.IGNORECASE,
)


@dataclass
class DadosProvaResultado:
    dados_prova: dict
    pendencias: list[str] = field(default_factory=list)


def extrair_dados_prova(secoes: Secoes) -> DadosProvaResultado:
    pendencias: list[str] = []
    fases: dict[str, dict] = {}

    _do_quadro_71(secoes.itens.get(7, ""), fases)
    if not fases:
        pendencias.append("Quadro 7.1 nao reconhecido — dados de prova incompletos.")

    item7 = " ".join(secoes.itens.get(7, "").split())
    _duracao_e_turno(item7, fases)
    _formato_objetiva(" ".join(secoes.itens.get(8, "").split()), fases)
    _discursivas(" ".join(secoes.itens.get(9, "").split()), fases)
    _oral(" ".join(secoes.itens.get(10, "").split()), fases)
    _titulos(" ".join(secoes.itens.get(12, "").split()), fases)

    lista = [fases[f] for f in sorted(fases)]
    return DadosProvaResultado(
        dados_prova={"fases": lista, "locais": []},  # locais e USUARIO
        pendencias=pendencias,
    )


def _no(fases: dict, fase: str) -> dict:
    return fases.setdefault(
        fase,
        {"fase": fase, "tipo": None, "duracao": None, "turno": None,
         "formato": None, "questoes": None},
    )


def _do_quadro_71(texto_item7: str, fases: dict) -> None:
    fase_atual: str | None = None
    for linha in recortar_quadro(texto_item7):
        linha = " ".join(linha.split())
        m = RE_ANCORA_FASE.search(linha)
        if m:
            fase_atual = m.group(2)
            _no(fases, fase_atual)["tipo"] = TIPO_POR_ROTULO[norm_ascii(m.group(1))]
            continue
        if fase_atual is None:
            continue
        m = RE_QUESTOES_LINHA.match(linha)
        if m and fases[fase_atual]["questoes"] is None:
            fases[fase_atual]["questoes"] = int(m.group(1))


def _duracao_e_turno(item7: str, fases: dict) -> None:
    m = RE_DURACAO_P1.search(item7)
    if m and "P1" in fases:
        fases["P1"]["duracao"] = f"{m.group(1)}h"
        fases["P1"]["turno"] = norm_ascii(m.group(2))
    for fase in ("P2", "P3"):
        m = _re_duracao_discursiva(fase).search(item7)
        if m and fase in fases:
            fases[fase]["duracao"] = f"{m.group(1)}h"
            fases[fase]["turno"] = norm_ascii(m.group(2))


def _formato_objetiva(item8: str, fases: dict) -> None:
    m = RE_FORMATO_P1.search(item8)
    if m and "P1" in fases:
        fases["P1"]["formato"] = m.group(1).strip().rstrip(",")


def _discursivas(item9: str, fases: dict) -> None:
    m = RE_P2.search(item9)
    if m and "P2" in fases:
        questoes = extenso_para_int(m.group(1))
        if questoes:
            fases["P2"]["questoes"] = questoes
        fases["P2"]["formato"] = f"{questoes or m.group(1)} questões, até {m.group(2)} linhas cada"
    m = RE_P3.search(item9)
    if m and "P3" in fases:
        fases["P3"]["questoes"] = 1
        fases["P3"]["formato"] = f"{m.group(1)}, até {m.group(2)} linhas"


def _oral(item10: str, fases: dict) -> None:
    if "P4" not in fases:
        return
    m = RE_ORAL_DURACAO.search(item10)
    if m:
        fases["P4"]["duracao"] = f"até {m.group(1)} min"
    questoes = None
    m = RE_ORAL_QUESTOES.search(item10)
    if m:
        questoes = extenso_para_int(m.group(1))
        fases["P4"]["questoes"] = questoes
    m = RE_ORAL_MINUTOS_POR_QUESTAO.search(item10)
    if m and questoes:
        fases["P4"]["formato"] = (
            f"{questoes} questões, {m.group(1)} minutos para a resposta de cada"
        )


def _titulos(item12: str, fases: dict) -> None:
    m = RE_TITULOS_MAX.search(item12)
    if m and "P5" in fases:
        fases["P5"]["formato"] = f"máximo de {m.group(1)} pontos"
