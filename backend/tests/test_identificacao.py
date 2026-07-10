"""Unidades do identificacao.py com um mini-edital sintetico no formato
literal do cabecalho da Cebraspe (o teste de ponta a ponta no PDF real
esta em test_pdf_smoke.py)."""

import pytest

from editais.parser.extractors import identificacao
from editais.parser.sectioner import Secoes

PREAMBULO = """ESTADO DE ALAGOAS
PROCURADORIA-GERAL DO ESTADO
CONCURSO PÚBLICO PARA O PROVIMENTO DE VAGAS NO CARGO DE PROCURADOR DO ESTADO DE
ALAGOAS – 1ª CLASSE
EDITAL Nº 1 – PGE/AL, DE 31 DE MARÇO DE 2026

A Procuradoria-Geral do Estado de Alagoas, tendo em vista o disposto na Lei
Estadual nº 5.247, de 26 de julho de 1991, na Lei Complementar nº 7, de 18 de
dezembro de 1991, e na Resolução nº 6, de 6 de novembro de 2025, do CSPGE,
torna pública a realização de concurso público.
"""

ITENS = {
    1: (
        "1 DAS DISPOSIÇÕES PRELIMINARES\n"
        "1.1 O concurso será executado pelo Centro Brasileiro de Pesquisa em "
        "Avaliação e Seleção e de Promoção de Eventos (Cebraspe).\n"
        "1.3 A prova objetiva, as provas discursivas e a prova oral serão "
        "realizadas em Maceió/AL.\n"
    ),
    2: "2 DO CARGO\nREMUNERAÇÃO: R$ 35.877,28.\nJORNADA DE TRABALHO: 20 horas semanais.\n",
    4: (
        "4 DAS VAGAS\n4.1 As vagas estão distribuídas conforme o quadro a seguir:\n"
        "Vagas imediatas\nCadastro de reserva\nAC\nPCD\nPPIQ\nTotal\nAC\nPCD\nPPIQ\nTotal\n"
        "7\n1\n2\n10\n7\n1\n2\n10\n20\n"
    ),
    6: "6 DAS INSCRIÇÕES\n6.1 TAXA: R$ 450,00.\n",
    16: (
        "16 DAS DISPOSIÇÕES FINAIS\n"
        "16.29 O prazo de validade do concurso esgotar-se-á após dois anos contados "
        "a partir da data de publicação da homologação do resultado final.\n"
    ),
}


@pytest.fixture(scope="module")
def resultado():
    return identificacao.extrair_identificacao(Secoes(preambulo=PREAMBULO, itens=ITENS))


def test_orgao_numero_publicacao(resultado):
    assert resultado.edital["orgao"] == "PGE/AL"
    assert resultado.edital["numero"] == "1/2026"
    assert resultado.edital["publicacao"] == "2026-03-31"


def test_cargo_literal(resultado):
    assert resultado.edital["cargo"] == "PROCURADOR DO ESTADO DE ALAGOAS – 1ª CLASSE"


def test_banca(resultado):
    assert resultado.edital["banca"] == "Cebraspe"


def test_base_legal(resultado):
    assert resultado.edital["base_legal"] == [
        "Lei Estadual 5.247/1991",
        "Lei Complementar 7/1991",
        "Resolução 6/2025",
    ]


def test_vagas(resultado):
    assert resultado.edital["vagas"] == {"imediatas": 10, "cadastro_reserva": 10}


def test_valores(resultado):
    assert resultado.edital["remuneracao"] == 35877.28
    assert resultado.edital["taxa"] == 450.0


def test_local_e_validade(resultado):
    assert resultado.edital["local_fases"] == "Maceió/AL"
    assert resultado.edital["validade_anos"] == 2


def test_sem_pendencias_no_caso_completo(resultado):
    assert resultado.pendencias == []


def test_vagas_inconsistentes_geram_pendencia():
    itens = dict(ITENS)
    itens[4] = "4 DAS VAGAS\n5\n1\n2\n10\n7\n1\n2\n10\n20\n"
    r = identificacao.extrair_identificacao(Secoes(preambulo=PREAMBULO, itens=itens))
    assert r.edital["vagas"] == {"imediatas": 10, "cadastro_reserva": 10}
    assert any("inconsistente" in p for p in r.pendencias)


def test_campos_ausentes_geram_pendencias():
    r = identificacao.extrair_identificacao(Secoes(preambulo="nada aqui", itens={}))
    assert r.edital.get("banca") is None
    assert len(r.pendencias) >= 4
