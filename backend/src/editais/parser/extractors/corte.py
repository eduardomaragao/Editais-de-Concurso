"""Corte de lei/jurisprudencia — item 16.32 (PARSER_SPEC §5).

Forma relativa ("vigente na data da primeira publicacao deste edital") e
resolvida para a data de publicacao do edital; "primeira publicacao" implica
afetado_por_retificacao=false (retificacao NAO move o corte). Sempre guarda
fonte e trecho literais. Tudo aqui e REVISAO: o resultado carrega uma lista
de pendencias para a tela de conferencia, e a ambiguidade edital vs. DOE e
resolvida para a data do edital com as duas candidatas preservadas.
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime

RE_LEGISLACAO = re.compile(
    r"legisla[çc][ãa]o.*?vigente\s+na\s+data\s+da\s+(primeira\s+)?"
    r"publica[çc][ãa]o\s+deste\s+edital",
    re.IGNORECASE | re.DOTALL,
)
RE_JURISPRUDENCIA = re.compile(
    r"jurisprud[êe]ncia.*?publicad[ao]s?\s+at[ée]\s+a\s+data\s+de\s+"
    r"publica[çc][ãa]o\s+deste\s+edital",
    re.IGNORECASE | re.DOTALL,
)
RE_DATA_EXPLICITA = re.compile(r"at[ée]\s+(\d{1,2}/\d{1,2}/\d{4})", re.IGNORECASE)
RE_TEMA = re.compile(r"legisla|jurisprud", re.IGNORECASE)

# Marcador de item do edital (16.32, 16.32.1) para segmentar o texto e
# preencher `fonte`. Mesma protecao do outline contra casar "32.1" dentro
# de "16.32.1".
RE_ITEM = re.compile(r"(?<![\d.])(\d{1,2}(?:\.\d{1,3}){1,3})\s+(?=[A-ZÀ-Ü])")


@dataclass
class CorteResultado:
    corte: dict  # no formato do $defs/corteConteudo do schema
    pendencias: list[str] = field(default_factory=list)
    # Campo interno para a tela de conferencia (nao entra no JSON final):
    # candidatas de data quando ha ambiguidade edital vs. DOE.
    candidatas: dict = field(default_factory=dict)


def extrair_corte(
    texto: str,
    publicacao: str | date | None = None,
    publicacao_doe: str | date | None = None,
) -> CorteResultado:
    """Extrai o corte do trecho do item 16 (ou do documento, como fallback)."""
    pub = _iso(publicacao)
    pub_doe = _iso(publicacao_doe)
    segmentos = _segmentos(texto)

    m_leg = m_jur = None
    fonte_leg = fonte_jur = None
    trecho_leg = trecho_jur = None
    for marcador, corpo in segmentos:
        if m_leg is None:
            m = RE_LEGISLACAO.search(corpo)
            if m:
                m_leg, fonte_leg, trecho_leg = m, marcador, corpo
        if m_jur is None:
            m = RE_JURISPRUDENCIA.search(corpo)
            if m:
                m_jur, fonte_jur, trecho_jur = m, marcador, corpo

    candidatas = {}
    if pub_doe is not None:
        candidatas = {"publicacao_edital": pub, "publicacao_doe": pub_doe}

    if m_leg or m_jur:
        return _relativo(
            m_leg, m_jur, fonte_leg, fonte_jur, trecho_leg, trecho_jur,
            pub, pub_doe, candidatas,
        )

    explicito = _explicito(segmentos, candidatas)
    if explicito:
        return explicito

    return CorteResultado(
        corte={
            "informado": False,
            "fonte": None,
            "forma": None,
            "referencia": None,
            "legislacao_ate": None,
            "jurisprudencia_ate": None,
            "afetado_por_retificacao": None,
            "trecho": None,
        },
        pendencias=["Edital nao traz clausula de corte identificavel — confirmar manualmente."],
        candidatas=candidatas,
    )


def _relativo(m_leg, m_jur, fonte_leg, fonte_jur, trecho_leg, trecho_jur,
              pub, pub_doe, candidatas) -> CorteResultado:
    pendencias = []
    primeira = bool(m_leg and m_leg.group(1))

    if pub is None:
        pendencias.append(
            "Corte relativo, mas a data de publicacao do edital nao esta "
            "disponivel — resolver a data e confirmar."
        )
    if pub_doe is not None and pub_doe != pub:
        pendencias.append(
            f"Publicacao ambigua: data do edital ({pub}) vs. DOE ({pub_doe}). "
            "Corte resolvido para a data do edital — confirmar qual conta."
        )
    if not primeira:
        pendencias.append(
            "Clausula nao menciona 'primeira publicacao' — confirmar se "
            "retificacao move o corte."
        )
    if m_leg and not m_jur:
        pendencias.append("Clausula de jurisprudencia nao encontrada — confirmar.")
    if m_jur and not m_leg:
        pendencias.append("Clausula de legislacao nao encontrada — confirmar.")

    fontes = [f for f in (fonte_leg, fonte_jur) if f]
    fontes_unicas = list(dict.fromkeys(fontes))
    return CorteResultado(
        corte={
            "informado": True,
            "fonte": " / ".join(fontes_unicas) if fontes_unicas else None,
            "forma": "relativa",
            "referencia": (
                "data da primeira publicacao do edital"
                if primeira
                else "data da publicacao do edital"
            ),
            "legislacao_ate": pub if m_leg else None,
            "jurisprudencia_ate": pub if m_jur else None,
            "afetado_por_retificacao": False if primeira else None,
            "trecho": trecho_leg or trecho_jur,
        },
        pendencias=pendencias,
        candidatas=candidatas,
    )


def _explicito(segmentos, candidatas) -> CorteResultado | None:
    for marcador, corpo in segmentos:
        if not RE_TEMA.search(corpo):
            continue
        m = RE_DATA_EXPLICITA.search(corpo)
        if m is None:
            continue
        data = _iso(m.group(1))
        return CorteResultado(
            corte={
                "informado": True,
                "fonte": marcador,
                "forma": "explicita",
                "referencia": None,
                "legislacao_ate": data,
                "jurisprudencia_ate": data,
                "afetado_por_retificacao": None,
                "trecho": corpo,
            },
            pendencias=[
                "Corte com data explicita — confirmar se vale para legislacao "
                "e jurisprudencia e se retificacao o move."
            ],
            candidatas=candidatas,
        )
    return None


def _segmentos(texto: str) -> list[tuple[str | None, str]]:
    """Divide o texto pelos marcadores de item (16.32, 16.32.1...).

    Sem marcadores, o texto inteiro vira um segmento unico com fonte None —
    e o fallback de varrer o documento inteiro.
    """
    marcas = list(RE_ITEM.finditer(texto))
    if not marcas:
        return [(None, texto.strip())]
    segmentos = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        segmentos.append((m.group(1), texto[m.end() : fim].strip()))
    return segmentos


def _iso(valor: str | date | None) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, date):
        return valor.isoformat()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor):
        return valor
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", valor):
        return datetime.strptime(valor, "%d/%m/%Y").date().isoformat()
    raise ValueError(f"Data em formato nao reconhecido: {valor!r}")
