"""Identificacao do edital (PARSER_SPEC §8).

Extrai do preambulo (cabecalho + intro antes do item 1) e de itens
especificos: orgao/numero/publicacao (linha "EDITAL Nº 1 – PGE/AL, DE 31
DE MARÇO DE 2026"), cargo (linha do titulo), banca (lista de bancas
conhecidas), base legal (intro), vagas (quadro do item 4), remuneracao
(item 2), taxa (item 6.1), local das fases (item 1.3) e validade (16.29).
"""

import re
import unicodedata
from dataclasses import dataclass, field

from editais.parser.sectioner import Secoes

RE_EDITAL = re.compile(
    r"EDITAL\s+N[ºo°]\s*(\d+)\s*[–—-]\s*([A-ZÀ-Ü]+(?:/[A-Z]{2})?)\s*,\s*"
    r"DE\s+(\d{1,2})\s+DE\s+([A-ZÀ-Üa-zà-ü]+)\s+DE\s+(\d{4})"
)
RE_CARGO = re.compile(r"NO CARGO DE\s+(.+?)\s+EDITAL\s+N", re.DOTALL)
RE_BASE_LEGAL = re.compile(
    r"((?:Lei|Resolu[çc][ãa]o|Decreto)(?:\s+(?:Estadual|Federal|Complementar))?)"
    r"\s+n[ºo°]\s*([\d.]+)(?:,\s*de\s+[^,]*?(\d{4}))?"
)
RE_REMUNERACAO = re.compile(r"REMUNERA[ÇC][ÃA]O:\s*R\$\s*([\d.]+,\d{2})")
RE_TAXA = re.compile(r"TAXA:\s*R\$\s*([\d.]+,\d{2})")
RE_LOCAL = re.compile(r"realizad[ao]s?\s+em\s+([^.\n]*?/[A-Z]{2})")
RE_VALIDADE = re.compile(
    r"prazo de validade do concurso esgotar-se-[áa] ap[óo]s\s+(\w+)\s+anos?"
)
RE_NUMERO_SOLTO = re.compile(r"^\d{1,4}$")

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11,
    "dezembro": 12,
}
NUMEROS_POR_EXTENSO = {"um": 1, "dois": 2, "tres": 3, "quatro": 4, "cinco": 5}
BANCAS_CONHECIDAS = ["Cebraspe", "FCC", "FGV", "Vunesp", "IBFC", "Cesgranrio", "IADES"]


@dataclass
class IdentificacaoExtraida:
    edital: dict
    pendencias: list[str] = field(default_factory=list)


def extrair_identificacao(secoes: Secoes) -> IdentificacaoExtraida:
    pendencias: list[str] = []
    edital: dict = {}
    preambulo = " ".join(secoes.preambulo.split())

    m = RE_EDITAL.search(preambulo)
    if m:
        numero, orgao, dia, mes_nome, ano = m.groups()
        edital["orgao"] = orgao
        edital["numero"] = f"{int(numero)}/{ano}"
        mes = MESES.get(_norm(mes_nome))
        if mes:
            edital["publicacao"] = f"{int(ano):04d}-{mes:02d}-{int(dia):02d}"
        else:
            edital["publicacao"] = None
            pendencias.append(f"Mes nao reconhecido na data do edital: {mes_nome!r}")
    else:
        pendencias.append("Linha 'EDITAL Nº ...' nao encontrada — preencher orgao/numero/publicacao.")

    m = RE_CARGO.search(preambulo)
    if m:
        edital["cargo"] = m.group(1).strip()
    else:
        pendencias.append("Cargo nao encontrado no cabecalho.")

    texto_banca = preambulo + " " + " ".join(secoes.itens.get(1, "").split())
    edital["banca"] = next((b for b in BANCAS_CONHECIDAS if b in texto_banca), None)
    if edital["banca"] is None:
        pendencias.append("Banca nao reconhecida — preencher manualmente.")

    base_legal = [
        f"{tipo} {numero}/{ano}" if ano else f"{tipo} {numero}"
        for tipo, numero, ano in RE_BASE_LEGAL.findall(preambulo)
    ]
    if base_legal:
        edital["base_legal"] = base_legal

    vagas = _vagas(secoes.itens.get(4, ""), pendencias)
    if vagas:
        edital["vagas"] = vagas

    edital["remuneracao"] = _moeda(RE_REMUNERACAO, secoes.itens.get(2, ""))
    edital["taxa"] = _moeda(RE_TAXA, secoes.itens.get(6, ""))
    if edital["remuneracao"] is None:
        pendencias.append("Remuneracao nao encontrada (item 2).")
    if edital["taxa"] is None:
        pendencias.append("Taxa nao encontrada (item 6.1).")

    m = RE_LOCAL.search(" ".join(secoes.itens.get(1, "").split()))
    edital["local_fases"] = m.group(1).strip() if m else None

    edital["validade_anos"] = _validade(secoes.itens.get(16, ""))
    if edital["validade_anos"] is None:
        pendencias.append("Prazo de validade nao encontrado (item 16).")

    return IdentificacaoExtraida(edital=edital, pendencias=pendencias)


def _vagas(texto_item4: str, pendencias: list[str]) -> dict | None:
    """Quadro do item 4: os numeros saem do PDF como linhas soltas, na ordem
    AC, PCD, PPIQ, Total (imediatas), AC, PCD, PPIQ, Total (CR), Total geral.
    """
    numeros = [
        int(linha.strip())
        for linha in texto_item4.splitlines()
        if RE_NUMERO_SOLTO.match(linha.strip())
    ]
    if len(numeros) < 8:
        pendencias.append("Quadro de vagas (item 4) nao reconhecido — preencher manualmente.")
        return None
    imediatas, cadastro_reserva = numeros[3], numeros[7]
    if sum(numeros[:3]) != imediatas:
        pendencias.append(
            f"Quadro de vagas inconsistente: AC+PCD+PPIQ={sum(numeros[:3])} "
            f"mas total imediatas={imediatas} — revisar."
        )
    return {"imediatas": imediatas, "cadastro_reserva": cadastro_reserva}


def _moeda(padrao: re.Pattern, texto: str) -> float | None:
    m = padrao.search(" ".join(texto.split()))
    if m is None:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


def _validade(texto_item16: str) -> int | None:
    m = RE_VALIDADE.search(" ".join(texto_item16.split()))
    if m is None:
        return None
    palavra = _norm(m.group(1))
    if palavra.isdigit():
        return int(palavra)
    return NUMEROS_POR_EXTENSO.get(palavra)


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
