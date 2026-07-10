"""Isencoes de taxa (PARSER_SPEC §8).

Hipoteses vem do item 6.4.8 ("Nª POSSIBILIDADE (descricao...)"); o periodo
do pedido vem do cronograma (primeiro evento de isencao com data de fim —
os demais eventos de isencao sao divulgacoes de resultado, com data unica).
"""

import re
from dataclasses import dataclass, field

from editais.parser.sectioner import Secoes

RE_POSSIBILIDADE = re.compile(r"\d+ª\s*POSSIBILIDADE\s*\(([^)]+)\)")


@dataclass
class IsencoesResultado:
    isencoes: dict
    pendencias: list[str] = field(default_factory=list)


def extrair_isencoes(
    secoes: Secoes, eventos_cronograma: list[dict] | None = None
) -> IsencoesResultado:
    pendencias: list[str] = []
    item6 = " ".join(secoes.itens.get(6, "").split())
    hipoteses = [" ".join(h.split()) for h in RE_POSSIBILIDADE.findall(item6)]

    inicio = fim = None
    for evento in eventos_cronograma or []:
        if evento["tipo"] == "isencao" and evento.get("fim"):
            inicio, fim = evento["inicio"], evento["fim"]
            break

    tem_isencao = bool(hipoteses)
    if not tem_isencao and "isen" in item6.lower():
        tem_isencao = True
        pendencias.append(
            "Edital menciona isencao, mas as hipoteses (6.4.8) nao foram "
            "reconhecidas — revisar."
        )
    if tem_isencao and inicio is None:
        pendencias.append("Periodo de isencao nao encontrado no cronograma — revisar.")

    return IsencoesResultado(
        isencoes={
            "tem_isencao": tem_isencao,
            "inicio": inicio,
            "fim": fim,
            "hipoteses": hipoteses,
            "link": None,
        },
        pendencias=pendencias,
    )
