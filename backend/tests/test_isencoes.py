"""Testes do isencoes.py com o formato real do item 6.4.8."""

from editais.parser.extractors import isencoes
from editais.parser.sectioner import Secoes

ITEM6 = """6 DAS INSCRIÇÕES NO CONCURSO PÚBLICO
6.1 TAXA: R$ 450,00.
6.4.8.2.1 1ª POSSIBILIDADE (desempregado, conforme dispõe a Lei Estadual nº 6.873/2007):
documentos exigidos.
6.4.8.2.2 2ª POSSIBILIDADE (inscrito em quaisquer dos projetos inseridos nos Programas de Assistência
Social mantidos pelo Governo): documentos.
6.4.8.2.3 3ª POSSIBILIDADE (doador voluntário de sangue, conforme dispõe a Lei Estadual nº
6.672/2005): documentos.
"""

EVENTOS = [
    {"tipo": "impugnacao", "inicio": "2026-04-06", "fim": "2026-04-10"},
    {"tipo": "isencao", "inicio": "2026-04-13", "fim": "2026-04-22"},
    {"tipo": "isencao", "inicio": "2026-05-04", "fim": None},
]


def test_hipoteses_e_periodo():
    r = isencoes.extrair_isencoes(Secoes(preambulo="", itens={6: ITEM6}), EVENTOS)
    assert r.isencoes["tem_isencao"] is True
    assert len(r.isencoes["hipoteses"]) == 3
    assert r.isencoes["hipoteses"][0].startswith("desempregado")
    # o periodo vem do primeiro evento de isencao COM fim (o pedido),
    # nao das divulgacoes de resultado (data unica)
    assert r.isencoes["inicio"] == "2026-04-13"
    assert r.isencoes["fim"] == "2026-04-22"
    assert r.pendencias == []


def test_sem_clausula_de_isencao():
    r = isencoes.extrair_isencoes(Secoes(preambulo="", itens={6: "6 DAS INSCRIÇÕES"}), [])
    assert r.isencoes["tem_isencao"] is False
    assert r.isencoes["hipoteses"] == []
