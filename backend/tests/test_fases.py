"""Testes do fases.py com o quadro 7.1 real (linhas soltas do pymupdf).

Aceite da PARSER_SPEC §7: Administrativo -> [P1,P2,P4]; Ambiental -> [P1];
Processual do Trabalho -> [P1]. Agrupamentos viram pendencia, nunca decisao.
"""

import pytest

from editais.parser.extractors import fases

QUADRO_71 = """7 DAS FASES DO CONCURSO
7.1 As fases do concurso estão descritas nos quadros a seguir:
PROVA/TIPO
ÁREA DE CONHECIMENTO
NÚMERO DE
QUESTÕES
CARÁTER
Prova objetiva (P1)
Direito Administrativo
Direito Ambiental
Direito Civil e Empresarial
Direito Constitucional
Direito do Trabalho
Direito Financeiro
Direito Previdenciário
Direito Processual Civil
Direito Processual do Trabalho
Direito Tributário
100
Eliminatório e
classificatório
Prova discursiva (P2)
Direito Administrativo
Direito Civil
Direito Constitucional
Direito do Trabalho e Previdenciário
na Administração Pública
Direito Financeiro
Direito Processual Civil
Direito Tributário
5 questões
discursivas
Prova discursiva (P3)
Peça judicial ou
parecer jurídico
Prova oral (P4)
Direito Administrativo
Direito Civil
Direito Constitucional
Direito Financeiro
Direito Processual Civil
Direito Tributário

Avaliação de títulos (P5)
–
–
Classificatório
7.2 A prova objetiva terá a duração de 5 horas e será aplicada na data provável estabelecida no
cronograma constante do Anexo I deste edital, no turno da tarde.
"""

MATERIAS = [
    "DIREITO ADMINISTRATIVO",
    "DIREITO AMBIENTAL",
    "DIREITO CIVIL",
    "DIREITO CONSTITUCIONAL",
    "DIREITO DO TRABALHO",
    "DIREITO EMPRESARIAL",
    "DIREITO FINANCEIRO",
    "DIREITO PREVIDENCIÁRIO",
    "DIREITO PROCESSUAL CIVIL",
    "DIREITO PROCESSUAL DO TRABALHO",
    "DIREITO TRIBUTÁRIO",
]


@pytest.fixture(scope="module")
def areas():
    return fases.extrair_areas_por_fase(QUADRO_71)


@pytest.fixture(scope="module")
def casamento(areas):
    return fases.casar_fases(areas, MATERIAS)


def test_areas_por_fase(areas):
    assert len(areas["P1"]) == 10
    assert len(areas["P2"]) == 7
    assert areas["P3"] == []  # peca/parecer nao e area de conhecimento
    assert len(areas["P4"]) == 6
    assert areas["P5"] == []


def test_area_quebrada_em_duas_linhas_e_rejuntada(areas):
    assert "Direito do Trabalho e Previdenciário na Administração Pública" in areas["P2"]


def test_ruido_de_tabela_nao_gruda_na_ultima_area(areas):
    # "Eliminatório e" / "classificatório" vem logo depois de Direito
    # Tributário no quadro do P1 e nao pode virar continuacao da area.
    assert areas["P1"][-1] == "Direito Tributário"


def test_aceite_da_spec(casamento):
    m = casamento.fases_por_materia
    assert m["DIREITO ADMINISTRATIVO"] == ["P1", "P2", "P4"]
    assert m["DIREITO AMBIENTAL"] == ["P1"]
    assert m["DIREITO PROCESSUAL DO TRABALHO"] == ["P1"]


def test_agrupamentos_distribuidos_e_marcados(casamento):
    m = casamento.fases_por_materia
    assert m["DIREITO EMPRESARIAL"] == ["P1"]  # via "Direito Civil e Empresarial"
    assert m["DIREITO CIVIL"] == ["P1", "P2", "P4"]
    assert m["DIREITO PREVIDENCIÁRIO"] == ["P1", "P2"]  # P2 via agrupamento
    assert m["DIREITO DO TRABALHO"] == ["P1", "P2"]
    agrupamentos = [p for p in casamento.pendencias if "agrupada" in p]
    assert len(agrupamentos) == 2  # Civil+Empresarial (P1) e Trabalho+Prev (P2)
