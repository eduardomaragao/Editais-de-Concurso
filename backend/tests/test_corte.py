"""Testes do corte.py — PARSER_SPEC §5/§11.4.

O ITEM16 reconstroi os itens 16.32/16.32.1 do edital PGE/AL (texto literal,
com acentos). Aceite do piloto: legislacao_ate = jurisprudencia_ate =
2026-03-31, forma relativa, corte nao afetado por retificacao.
"""

from datetime import date

import pytest

from editais.parser.extractors import corte

ITEM16 = (
    "16.31 Não serão fornecidas informações por telefone. "
    "16.32 A legislação de referência a ser considerada será a vigente na "
    "data da primeira publicação deste edital. "
    "16.32.1 Será considerada a jurisprudência dos tribunais superiores "
    "publicada até a data de publicação deste edital. "
    "16.33 Os casos omissos serão resolvidos pelo Cebraspe."
)


def test_relativa_resolvida_para_a_publicacao(def_validator):
    resultado = corte.extrair_corte(ITEM16, publicacao="2026-03-31")
    assert resultado.corte == {
        "informado": True,
        "fonte": "16.32 / 16.32.1",
        "forma": "relativa",
        "referencia": "data da primeira publicacao do edital",
        "legislacao_ate": "2026-03-31",
        "jurisprudencia_ate": "2026-03-31",
        "afetado_por_retificacao": False,
        "trecho": (
            "A legislação de referência a ser considerada será a vigente na "
            "data da primeira publicação deste edital."
        ),
    }
    assert resultado.pendencias == []
    assert list(def_validator("corteConteudo").iter_errors(resultado.corte)) == []


def test_aceita_publicacao_como_date():
    resultado = corte.extrair_corte(ITEM16, publicacao=date(2026, 3, 31))
    assert resultado.corte["legislacao_ate"] == "2026-03-31"


def test_explicita(def_validator):
    texto = (
        "16.30 Serão exigidas a legislação e a jurisprudência publicadas "
        "até 15/02/2026, não sendo consideradas alterações posteriores."
    )
    resultado = corte.extrair_corte(texto)
    assert resultado.corte["informado"] is True
    assert resultado.corte["forma"] == "explicita"
    assert resultado.corte["legislacao_ate"] == "2026-02-15"
    assert resultado.corte["jurisprudencia_ate"] == "2026-02-15"
    assert resultado.corte["fonte"] == "16.30"
    assert resultado.pendencias  # data explicita sempre pede conferencia
    assert list(def_validator("corteConteudo").iter_errors(resultado.corte)) == []


def test_nao_informado(def_validator):
    texto = "16.1 A inscrição implica aceitação das normas. 16.2 Os prazos são preclusivos."
    resultado = corte.extrair_corte(texto, publicacao="2026-03-31")
    assert resultado.corte["informado"] is False
    assert resultado.corte["legislacao_ate"] is None
    assert resultado.pendencias
    assert list(def_validator("corteConteudo").iter_errors(resultado.corte)) == []


def test_relativa_sem_publicacao_fica_pendente():
    resultado = corte.extrair_corte(ITEM16)
    assert resultado.corte["informado"] is True
    assert resultado.corte["forma"] == "relativa"
    assert resultado.corte["legislacao_ate"] is None
    assert resultado.corte["jurisprudencia_ate"] is None
    assert any("publicacao" in p for p in resultado.pendencias)


def test_ambiguidade_edital_vs_doe_resolve_para_o_edital():
    resultado = corte.extrair_corte(
        ITEM16, publicacao="2026-03-31", publicacao_doe="2026-04-01"
    )
    # Resolve para a data do edital, mas preserva as duas candidatas e
    # marca para revisao — o parser nao decide sozinho (PARSER_SPEC §5).
    assert resultado.corte["legislacao_ate"] == "2026-03-31"
    assert resultado.candidatas == {
        "publicacao_edital": "2026-03-31",
        "publicacao_doe": "2026-04-01",
    }
    assert any("DOE" in p for p in resultado.pendencias)


def test_juris_sem_primeira_publicacao_nao_afirma_nada_sobre_retificacao():
    texto = (
        "16.10 Será considerada a jurisprudência publicada até a data de "
        "publicação deste edital."
    )
    resultado = corte.extrair_corte(texto, publicacao="2026-03-31")
    assert resultado.corte["forma"] == "relativa"
    assert resultado.corte["referencia"] == "data da publicacao do edital"
    assert resultado.corte["jurisprudencia_ate"] == "2026-03-31"
    assert resultado.corte["legislacao_ate"] is None
    assert resultado.corte["afetado_por_retificacao"] is None
    assert resultado.pendencias  # falta legislacao + duvida sobre retificacao


def test_fallback_sem_marcadores_de_item():
    texto = (
        "A legislação de referência a ser considerada será a vigente na data "
        "da primeira publicação deste edital."
    )
    resultado = corte.extrair_corte(texto, publicacao="2026-03-31")
    assert resultado.corte["informado"] is True
    assert resultado.corte["fonte"] is None
    assert resultado.corte["legislacao_ate"] == "2026-03-31"


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [
        (None, None),
        ("2026-03-31", "2026-03-31"),
        ("31/03/2026", "2026-03-31"),
        ("5/9/2026", "2026-09-05"),
        (date(2026, 3, 31), "2026-03-31"),
    ],
)
def test_iso(entrada, esperado):
    assert corte._iso(entrada) == esperado
