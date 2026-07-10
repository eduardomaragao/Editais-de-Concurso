"""Nucleo do radar (PARSER_SPEC §9): comparar o que o arquivo incorpora com
o que a banca publicou.

Regras:
- `retificacoes_incorporadas` vem do proprio PDF (versioning.py).
- So RETIFICACAO trava a publicacao: um "Edital no 5 - Retificacao..." nao
  incorporado marca `radar_desatualizado=true` e pede reupload do
  consolidado. Editais que nao retificam (relacao de isencao, convocacao)
  viram alerta informativo, sem travar.
- `ultima_retificacao_publicada` sai no formato do golden: "no 5 (2026-06-08)".
"""

import re
from dataclasses import dataclass, field
from typing import Protocol

from editais.parser.util import norm_ascii


@dataclass(frozen=True)
class EditalPublicado:
    numero: int
    data: str | None = None  # ISO
    titulo: str | None = None
    url: str | None = None

    @property
    def retificacao(self) -> bool:
        return e_retificacao(self.titulo or "")


class FetcherBanca(Protocol):
    """Interface plugavel por banca (PARSER_SPEC: fetch_editais)."""

    def fetch_editais(self) -> list[EditalPublicado]: ...


@dataclass
class RadarResultado:
    ultima_retificacao_publicada: str | None
    radar_desatualizado: bool
    publicacao_travada: bool
    nao_incorporados: list[EditalPublicado] = field(default_factory=list)
    alertas: list[str] = field(default_factory=list)


def e_retificacao(titulo: str) -> bool:
    normalizado = norm_ascii(titulo)
    return "retifica" in normalizado or "altera" in normalizado


def comparar(
    retificacoes_incorporadas: list[str], publicados: list[EditalPublicado]
) -> RadarResultado:
    if not publicados:
        return RadarResultado(
            ultima_retificacao_publicada=None,
            radar_desatualizado=False,
            publicacao_travada=False,
            alertas=["Nenhum edital obtido do site da banca — verificar o fetcher."],
        )

    # nº 1 e o edital de abertura: sem retificacao incorporada, a base e 1.
    max_incorporado = max(
        (int(m.group(1)) for r in retificacoes_incorporadas
         if (m := re.search(r"(\d+)", r))),
        default=1,
    )

    retificacoes = [e for e in publicados if e.retificacao]
    nao_incorporados = [e for e in retificacoes if e.numero > max_incorporado]
    outros_novos = [
        e for e in publicados if not e.retificacao and e.numero > max_incorporado
    ]

    ultima = max(retificacoes, key=lambda e: e.numero, default=None)
    ultima_str = None
    if ultima is not None:
        ultima_str = f"no {ultima.numero} ({ultima.data})" if ultima.data else f"no {ultima.numero}"

    alertas = []
    desatualizado = bool(nao_incorporados)
    if desatualizado:
        numeros = ", ".join(f"no {e.numero}" for e in nao_incorporados)
        alertas.append(
            f"Existe retificacao nao incorporada ({numeros}); o arquivo consolida "
            f"ate o no {max_incorporado}. Publicacao TRAVADA — reenvie o "
            "consolidado atualizado."
        )
    if outros_novos:
        numeros = ", ".join(f"no {e.numero}" for e in outros_novos)
        alertas.append(
            f"Editais publicados apos a consolidacao (nao retificam o texto): "
            f"{numeros} — conferir se afetam o cronograma."
        )

    return RadarResultado(
        ultima_retificacao_publicada=ultima_str,
        radar_desatualizado=desatualizado,
        publicacao_travada=desatualizado,
        nao_incorporados=nao_incorporados,
        alertas=alertas,
    )


def aplicar_no_documento(documento: dict, resultado: RadarResultado) -> dict:
    """Grava os campos do radar no documento (in place) e o devolve."""
    documento["edital"]["ultima_retificacao_publicada"] = (
        resultado.ultima_retificacao_publicada
    )
    documento["edital"]["radar_desatualizado"] = resultado.radar_desatualizado
    return documento


def verificar(documento: dict, fetcher: FetcherBanca) -> RadarResultado:
    """Conveniencia: busca na banca, compara e aplica no documento."""
    resultado = comparar(
        documento["edital"].get("retificacoes_incorporadas", []),
        fetcher.fetch_editais(),
    )
    aplicar_no_documento(documento, resultado)
    return resultado
