"""Arvore de conteudo do item 17 — nucleo do parser (PARSER_SPEC §4).

Monta materia -> topico -> subtopico a partir do outline plano de cada
disciplina. Um candidato a marcador so e aceito se for continuacao plausivel
do estado atual ("proximo numero esperado"); e isso que impede numeros de
lei (14.133/2021) de virarem nos da arvore. Titulos saem literais, sem o
numero e sem ponto final; marcadores de retificacao vao para o versioning.

Ids seguem o formato do golden (adm-7-5, com hifens), nao o sugerido na
spec (adm-7.5).
"""

import re
import unicodedata
from dataclasses import dataclass

# Candidato a marcador de outline: numero (ate 4 niveis) seguido de espaco e
# maiuscula, nao precedido de digito/ponto — evita casar "32.1" dentro de
# "16.32.1". A validacao de verdade e feita por numero_valido().
RE_CANDIDATO = re.compile(r"(?<![\d.])(\d+(?:\.\d+){0,3})\s+(?=[A-ZÀ-Ü])")

# Ex.: "(Retificado por meio do Edital nº 3 – PGE/AL, de 6 de maio de 2026.)"
RE_RETIFICACAO = re.compile(
    r"\s*\(\s*Retificad[oa] por meio do Edital n[ºo°]\s*(\d+)[^)]*\)",
    re.IGNORECASE,
)

# Cabecalho de disciplina: duas ou mais palavras em CAIXA ALTA seguidas de
# ":". Uma palavra so nao basta — senao uma sigla no meio de um titulo
# ("... e OSC: Lei nº 13.019/2014") viraria disciplina.
RE_CABECALHO = re.compile(r"([A-ZÀ-Ü]+(?:\s+[A-ZÀ-Ü]+)+)\s*:")


@dataclass
class DisciplinaParseada:
    materia: dict
    nos: list[dict]  # materia + topicos + subtopicos, na ordem do edital
    marcadores_retificacao: list[str]  # ex.: ["nº 3"] — insumo do versioning


def numero_valido(num: tuple[int, ...], estado: list[int]) -> bool:
    """True se `num` e a continuacao plausivel do caminho atual `estado`.

    Aceita apenas: o primeiro marcador (1,), o primeiro filho (X.1) ou o
    proximo irmao em qualquer nivel ancestral. Qualquer salto — como um
    numero de lei 14.133 depois do topico 12 — e rejeitado.
    """
    profundidade = len(num)
    if not estado:
        return num == (1,)
    if profundidade == len(estado) + 1:
        return list(num[:-1]) == estado and num[-1] == 1
    if profundidade <= len(estado):
        prefixo = list(num[: profundidade - 1])
        return prefixo == estado[: profundidade - 1] and num[-1] == estado[profundidade - 1] + 1
    return False


def parse_disciplina(
    texto: str, materia_id: str, materia_titulo: str, ordem: int | None = None
) -> DisciplinaParseada:
    """Converte o outline plano de uma disciplina em nos do schema."""
    aceitos: list[tuple[tuple[int, ...], int, int]] = []
    estado: list[int] = []
    for m in RE_CANDIDATO.finditer(texto):
        num = tuple(int(x) for x in m.group(1).split("."))
        if numero_valido(num, estado):
            aceitos.append((num, m.start(), m.end()))
            estado = list(num)

    materia: dict = {
        "id": materia_id,
        "parent_id": None,
        "nivel": "materia",
        "titulo": materia_titulo,
    }
    if ordem is not None:
        materia["ordem"] = ordem

    nos = [materia]
    marcadores: list[str] = []
    for i, (num, _inicio, fim_marcador) in enumerate(aceitos):
        fim_titulo = aceitos[i + 1][1] if i + 1 < len(aceitos) else len(texto)
        titulo, marcadores_do_no = _limpar_titulo(texto[fim_marcador:fim_titulo])
        marcadores.extend(marcadores_do_no)
        nos.append(
            {
                "id": _no_id(materia_id, num),
                "parent_id": materia_id if len(num) == 1 else _no_id(materia_id, num[:-1]),
                "nivel": "topico" if len(num) == 1 else "subtopico",
                "titulo": titulo,
                "ordem": num[0] if len(num) == 1 else num[-1],
            }
        )
    return DisciplinaParseada(materia=materia, nos=nos, marcadores_retificacao=marcadores)


def split_disciplinas(texto: str) -> list[tuple[str, str]]:
    """Divide o item 17 em (titulo_da_disciplina, corpo_do_outline)."""
    cabecalhos = list(RE_CABECALHO.finditer(texto))
    partes = []
    for i, m in enumerate(cabecalhos):
        fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
        partes.append((m.group(1).strip(), texto[m.end() : fim]))
    return partes


def parse_item17(texto: str) -> list[DisciplinaParseada]:
    """Parseia o item 17 completo: uma DisciplinaParseada por cabecalho."""
    return [
        parse_disciplina(corpo, _slug(titulo), titulo, ordem=ordem)
        for ordem, (titulo, corpo) in enumerate(split_disciplinas(texto), start=1)
    ]


def _no_id(materia_id: str, num: tuple[int, ...]) -> str:
    return f"{materia_id}-{'-'.join(map(str, num))}"


def _limpar_titulo(bruto: str) -> tuple[str, list[str]]:
    marcadores = [f"nº {n}" for n in RE_RETIFICACAO.findall(bruto)]
    titulo = RE_RETIFICACAO.sub("", bruto)
    titulo = re.sub(r"\s+", " ", titulo).strip()
    if titulo.endswith("."):
        titulo = titulo[:-1].rstrip()
    return titulo, marcadores


def _slug(titulo: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
