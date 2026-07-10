"""Testes do versioning.py — PARSER_SPEC §11.5: cabecalho "nº 3" +
marcadores no corpo → ["no 2", "no 3"]."""

from editais.parser import versioning

CONSOLIDADO = """EDITAL Nº 1 – PGE/AL, DE 31 DE MARÇO DE 2026

Versão atualizada conforme retificação constante do Edital nº 3 – PGE/AL, de 6 de maio de 2026.

9.2 As provas serão avaliadas conforme os critérios.
(Retificado por meio do Edital nº 3 – PGE/AL, de 6 de maio de 2026, disponível no endereço eletrônico
http://www.cebraspe.org.br/concursos/pge_al_26)
9.3 Os textos definitivos.
"""


def test_cabecalho_e_marcadores():
    resultado = versioning.extrair_versao(CONSOLIDADO)
    # nº 1 e o proprio edital de abertura; consolidado ate o nº 3 incorpora 2..3
    assert resultado.retificacoes_incorporadas == ["no 2", "no 3"]
    assert resultado.versao_arquivo == "consolidado ate Edital no 3 (2026-05-06)"
    assert resultado.pendencias == []


def test_sem_cabecalho_de_versao_gera_pendencia():
    texto = "EDITAL Nº 1\n(Retificado por meio do Edital nº 2 – X, de 1 de abril de 2026)\ncorpo."
    resultado = versioning.extrair_versao(texto)
    assert resultado.versao_arquivo is None
    assert resultado.retificacoes_incorporadas == ["no 2"]
    assert any("consolidado" in p for p in resultado.pendencias)


def test_edital_sem_retificacao_alguma():
    resultado = versioning.extrair_versao("EDITAL Nº 1 sem nada.")
    assert resultado.retificacoes_incorporadas == []
    assert resultado.versao_arquivo is None
