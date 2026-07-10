"""Testes do radar — aceite do piloto (PARSER_SPEC §9): o arquivo consolida
ate o Edital no 3, mas o site expoe o no 5 (retificacao) e os no 6-7 (nao
retificam) → radar_desatualizado=true, publicacao travada."""

import pytest

from conftest import PDF_PATH
from editais.parser import assemble, validate
from editais.radar import cebraspe, core

# A lista real do concurso PGE/AL (datas dos PDFs no repo).
SITE_PGE_AL = [
    core.EditalPublicado(1, "2026-03-31", "Edital nº 1 – PGE/AL, de 31 de março de 2026 - Abertura"),
    core.EditalPublicado(2, "2026-04-30", "Edital nº 2 – PGE/AL, de 30 de abril de 2026 - Relação provisória de isenção"),
    core.EditalPublicado(3, "2026-05-06", "Edital nº 3 – PGE/AL, de 6 de maio de 2026 - Retificação dos subitens 9.2 e 10.12"),
    core.EditalPublicado(4, "2026-05-15", "Edital nº 4 – PGE/AL, de 15 de maio de 2026 - Relação final de isenção"),
    core.EditalPublicado(5, "2026-06-08", "Edital nº 5 – PGE/AL, de 8 de junho de 2026 - Retificação dos subitens 5.1.1.1 e 6.4.8"),
    core.EditalPublicado(6, "2026-06-25", "Edital nº 6 – PGE/AL, de 25 de junho de 2026 - Reabertura das inscrições e da isenção"),
    core.EditalPublicado(7, "2026-06-30", "Edital nº 7 – PGE/AL, de 30 de junho de 2026 - Relação provisória de isenção"),
]


def test_aceite_do_piloto():
    resultado = core.comparar(["no 2", "no 3"], SITE_PGE_AL)
    assert resultado.radar_desatualizado is True
    assert resultado.publicacao_travada is True
    assert resultado.ultima_retificacao_publicada == "no 5 (2026-06-08)"
    assert [e.numero for e in resultado.nao_incorporados] == [5]
    assert any("TRAVADA" in a for a in resultado.alertas)
    # nº 6 e 7 nao travam, mas viram alerta informativo
    assert any("no 6, no 7" in a for a in resultado.alertas)


def test_arquivo_atualizado_nao_trava():
    incorporadas = ["no 2", "no 3", "no 5"]
    resultado = core.comparar(incorporadas, SITE_PGE_AL)
    assert resultado.radar_desatualizado is False
    assert resultado.publicacao_travada is False
    assert resultado.ultima_retificacao_publicada == "no 5 (2026-06-08)"


def test_edital_sem_retificacao_alguma_incorporada():
    # sem cabecalho de consolidacao, a base e o proprio edital de abertura (nº 1)
    resultado = core.comparar([], SITE_PGE_AL[:3])
    assert resultado.radar_desatualizado is True  # nº 3 e retificacao nao incorporada
    assert [e.numero for e in resultado.nao_incorporados] == [3]


def test_site_vazio_gera_alerta_e_nao_trava():
    resultado = core.comparar(["no 3"], [])
    assert resultado.radar_desatualizado is False
    assert resultado.publicacao_travada is False
    assert resultado.alertas


@pytest.mark.parametrize(
    ("titulo", "esperado"),
    [
        ("Edital nº 5 - Retificação dos subitens", True),
        ("Edital nº 3 - Alterações do Edital nº 1", True),
        ("Edital nº 4 - Relação final de isenção", False),
        ("Edital nº 6 - Reabertura das inscrições", False),
    ],
)
def test_classificacao_de_retificacao(titulo, esperado):
    assert core.e_retificacao(titulo) is esperado


HTML_CEBRASPE = """
<div class="lista-editais">
  <a href="/concursos/arquivos/ED_1_PGE_AL_ABERTURA.pdf">Edital nº 1 – PGE/AL, de 31 de março de 2026</a>
  <a href="/concursos/arquivos/ED_3_PGE_AL_RET.pdf"><strong>Edital nº 3</strong> – PGE/AL, de 6 de maio de 2026 - Retificação</a>
  <a href="/concursos/arquivos/ED_5_PGE_AL_RET.pdf">Edital nº 5 – PGE/AL, de 8 de junho de 2026 - Retificação de subitens</a>
  <a href="/outros/manual.pdf">Manual do candidato</a>
  <a href="/concursos/pagina">Página do concurso</a>
</div>
"""


def test_extrair_editais_do_html():
    editais = cebraspe.extrair_editais_do_html(HTML_CEBRASPE)
    assert [(e.numero, e.data) for e in editais] == [
        (1, "2026-03-31"),
        (3, "2026-05-06"),
        (5, "2026-06-08"),
    ]
    assert editais[1].retificacao is True
    assert editais[0].retificacao is False
    assert editais[2].url.endswith("ED_5_PGE_AL_RET.pdf")


def test_cebraspe_fetcher_usa_o_download_injetado():
    fetcher = cebraspe.CebraspeFetcher("http://exemplo", baixar=lambda url: HTML_CEBRASPE)
    assert [e.numero for e in fetcher.fetch_editais()] == [1, 3, 5]


class FetcherFake:
    def __init__(self, editais):
        self._editais = editais

    def fetch_editais(self):
        return self._editais


@pytest.mark.skipif(not PDF_PATH.exists(), reason="PDF consolidado nao esta no repo")
def test_integracao_parse_mais_radar_bate_com_o_golden(golden):
    documento = assemble.parse_edital(PDF_PATH).documento
    resultado = core.verificar(documento, FetcherFake(SITE_PGE_AL))

    assert resultado.publicacao_travada is True
    assert documento["edital"]["radar_desatualizado"] is True
    assert documento["edital"]["ultima_retificacao_publicada"] == (
        golden["edital"]["ultima_retificacao_publicada"]  # "no 5 (2026-06-08)"
    )
    assert validate.erros(documento) == []
