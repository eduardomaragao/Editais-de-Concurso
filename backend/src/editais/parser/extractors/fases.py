"""Quadro 7.1 -> mapa materia -> [P1, P2, ...] (PARSER_SPEC §7).

O quadro sai do PDF como linhas soltas: ancora "Prova X (Pn)" seguida das
areas de conhecimento ("Direito ..."), intercaladas com ruido de tabela
(numero de questoes, carater). Areas quebradas em duas linhas sao rejuntadas
quando a continuacao comeca em minuscula e vem imediatamente apos uma area.

Agrupamentos ("Direito Civil e Empresarial", "Direito do Trabalho e
Previdenciario na Administracao Publica") sao distribuidos entre as materias
do item 17 e SEMPRE marcados como pendencia de revisao — o parser nao decide
agrupamento sozinho.
"""

import re
import unicodedata
from dataclasses import dataclass, field

RE_FASE = re.compile(r"\((P\d)\)")


@dataclass
class FasesResultado:
    fases_por_materia: dict[str, list[str]]  # chave = titulo da materia (item 17)
    pendencias: list[str] = field(default_factory=list)


def extrair_areas_por_fase(texto_item7: str) -> dict[str, list[str]]:
    """Le o quadro do 7.1 e devolve {fase: [area literal, ...]}."""
    linhas = _recortar_quadro(texto_item7)
    areas: dict[str, list[str]] = {}
    fase_atual: str | None = None
    anterior_foi_area = False

    for linha in linhas:
        linha = " ".join(linha.split())
        m = RE_FASE.search(linha)
        if m:
            fase_atual = m.group(1)
            areas.setdefault(fase_atual, [])
            anterior_foi_area = False
            continue
        if fase_atual is None or not linha:
            anterior_foi_area = False
            continue
        if linha.startswith("Direito"):
            areas[fase_atual].append(linha)
            anterior_foi_area = True
        elif anterior_foi_area and linha[:1].islower():
            areas[fase_atual][-1] += " " + linha  # continuacao de area quebrada
        else:
            anterior_foi_area = False
    return areas


def casar_fases(
    areas_por_fase: dict[str, list[str]], materias: list[str]
) -> FasesResultado:
    """Casa as areas do quadro 7.1 com os titulos de materia do item 17."""
    por_norma = {_norm(m): m for m in materias}
    resultado: dict[str, list[str]] = {m: [] for m in materias}
    pendencias: list[str] = []

    for fase in sorted(areas_por_fase):
        for area in areas_por_fase[fase]:
            norma = _norm(area)
            if norma in por_norma:
                resultado[por_norma[norma]].append(fase)
                continue
            casadas = _casar_agrupamento(norma, por_norma)
            if casadas:
                for materia in casadas:
                    resultado[materia].append(fase)
                pendencias.append(
                    f"Area agrupada '{area}' ({fase}) distribuida entre "
                    f"{casadas} — revisar."
                )
            else:
                pendencias.append(
                    f"Area '{area}' ({fase}) sem materia correspondente no "
                    "item 17 — revisar."
                )
    return FasesResultado(fases_por_materia=resultado, pendencias=pendencias)


def _casar_agrupamento(norma: str, por_norma: dict[str, str]) -> list[str]:
    """Distribui "direito civil e empresarial" entre as materias que compoe."""
    partes = [p.strip() for p in norma.split(" e ")]
    if len(partes) < 2:
        return []
    casadas = []
    for i, parte in enumerate(partes):
        if i > 0 and not parte.startswith("direito"):
            parte = "direito " + parte  # "empresarial" -> "direito empresarial"
        for materia_norma, materia in por_norma.items():
            if parte == materia_norma or parte.startswith(materia_norma + " "):
                casadas.append(materia)
                break
    return casadas


def _recortar_quadro(texto_item7: str) -> list[str]:
    linhas = texto_item7.splitlines()
    inicio = fim = None
    for i, linha in enumerate(linhas):
        stripped = linha.strip()
        if inicio is None and stripped.startswith("7.1 "):
            inicio = i
        elif inicio is not None and stripped.startswith("7.2 "):
            fim = i
            break
    return linhas[inicio:fim] if inicio is not None else linhas


def _norm(s: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return " ".join(ascii_.lower().split())
