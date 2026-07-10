"""Testes de fumaca no PDF real do consolidado PGE/AL (PARSER_SPEC §12.1).

Exercita o pipeline inteiro ate onde ja existe: pdf_text -> sectioner ->
outline / corte / cronograma / fases / identificacao, comparando com os
valores do golden (pge_al.instance.json). Texto literal tem acentos e o
golden e ASCII, entao as comparacoes de texto normalizam.
"""

import unicodedata

import pytest

from conftest import PDF_PATH
from editais.parser import outline, pdf_text, sectioner
from editais.parser.extractors import corte, cronograma, fases, identificacao

pytestmark = pytest.mark.skipif(
    not PDF_PATH.exists(), reason="PDF consolidado nao esta no repo"
)


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


@pytest.fixture(scope="module")
def texto():
    return pdf_text.texto_limpo(PDF_PATH)


@pytest.fixture(scope="module")
def secoes(texto):
    return sectioner.dividir(texto.texto)


@pytest.fixture(scope="module")
def disciplinas(secoes):
    return outline.parse_item17(secoes.itens[17])


def test_texto_limpo_51_paginas(texto):
    assert len(texto.offsets_paginas) == 51
    assert "16.32 A legislação de referência" in texto.texto


def test_sectioner_encontra_itens_1_a_17_e_anexos(secoes):
    assert sorted(secoes.itens) == list(range(1, 18))
    assert sorted(secoes.anexos) == ["I", "II"]
    assert "EDITAL Nº 1" in secoes.preambulo
    assert secoes.itens[16].startswith("16 DAS DISPOSIÇÕES FINAIS")
    assert "DIREITO ADMINISTRATIVO:" in secoes.itens[17]


def test_corte_real_bate_com_o_golden(secoes, golden):
    resultado = corte.extrair_corte(secoes.itens[16], publicacao="2026-03-31")
    esperado = golden["edital"]["corte_conteudo"]
    assert resultado.corte["informado"] is True
    assert resultado.corte["fonte"] == esperado["fonte"]  # "16.32 / 16.32.1"
    assert resultado.corte["forma"] == "relativa"
    assert resultado.corte["referencia"] == esperado["referencia"]
    assert resultado.corte["legislacao_ate"] == esperado["legislacao_ate"]
    assert resultado.corte["jurisprudencia_ate"] == esperado["jurisprudencia_ate"]
    assert resultado.corte["afetado_por_retificacao"] is False
    assert _ascii(" ".join(resultado.corte["trecho"].split())) == esperado["trecho"]


def test_outline_real_11_disciplinas(disciplinas):
    titulos = [d.materia["titulo"] for d in disciplinas]
    assert len(titulos) == 11
    assert titulos[0] == "DIREITO ADMINISTRATIVO"
    assert "DIREITO PROCESSUAL DO TRABALHO" in titulos


def test_outline_real_direito_administrativo(disciplinas):
    adm = disciplinas[0]
    por_id = {n["id"]: n for n in adm.nos}
    topicos = [n for n in adm.nos if n["nivel"] == "topico"]
    assert [t["ordem"] for t in topicos] == list(range(1, 26))

    assert por_id["direito-administrativo-7"]["titulo"] == "Atos administrativos"
    assert por_id["direito-administrativo-7-5"]["titulo"] == (
        "Vinculação e discricionariedade"
    )
    assert por_id["direito-administrativo-21"]["titulo"] == (
        "Responsabilidade civil do Estado"
    )
    assert not any(
        n["parent_id"] == "direito-administrativo-21" for n in adm.nos
    )
    licitacoes = por_id["direito-administrativo-12"]
    assert "Lei nº 14.133/2021" in licitacoes["titulo"]
    assert not any(n["id"].startswith("direito-administrativo-12-") for n in adm.nos)


def test_cronograma_real(secoes, def_validator):
    resultado = cronograma.extrair_cronograma(secoes.anexos["I"])
    assert len(resultado.eventos) == 22
    por_tipo = {(e["tipo"], e["inicio"]) for e in resultado.eventos}
    assert ("prova_objetiva", "2026-07-11") in por_tipo  # data do ARQUIVO (pre-nº 5)
    assert ("provas_discursivas", "2026-07-12") in por_tipo
    assert ("inscricoes", "2026-04-13") in por_tipo
    validador = def_validator("eventoCronograma")
    for evento in resultado.eventos:
        assert list(validador.iter_errors(evento)) == []


def test_fases_reais(secoes, disciplinas):
    areas = fases.extrair_areas_por_fase(secoes.itens[7])
    materias = [d.materia["titulo"] for d in disciplinas]
    casamento = fases.casar_fases(areas, materias)
    m = casamento.fases_por_materia
    assert m["DIREITO ADMINISTRATIVO"] == ["P1", "P2", "P4"]
    assert m["DIREITO AMBIENTAL"] == ["P1"]
    assert m["DIREITO PROCESSUAL DO TRABALHO"] == ["P1"]
    assert m["DIREITO EMPRESARIAL"] == ["P1"]
    assert len([p for p in casamento.pendencias if "agrupada" in p]) == 2


def test_identificacao_real(secoes, golden):
    resultado = identificacao.extrair_identificacao(secoes)
    e = resultado.edital
    assert e["orgao"] == "PGE/AL"
    assert e["numero"] == golden["edital"]["numero"]  # "1/2026"
    assert e["publicacao"] == golden["edital"]["publicacao"]  # "2026-03-31"
    assert e["banca"] == "Cebraspe"
    assert "PROCURADOR DO ESTADO DE ALAGOAS" in e["cargo"]
    assert e["vagas"] == golden["edital"]["vagas"]
    assert e["remuneracao"] == golden["edital"]["remuneracao"]
    assert e["taxa"] == golden["edital"]["taxa"]
    assert _ascii(e["local_fases"]) == golden["edital"]["local_fases"]  # Maceio/AL
    assert e["validade_anos"] == 2
