"""Testes do cronograma.py com o Anexo I real da PGE/AL (linha a linha,
como o pymupdf entrega — inclusive cabecalho de tabela repetido na virada
de pagina e titulos quebrados em uma palavra por linha)."""

from pathlib import Path

import pytest

from editais.parser.extractors import cronograma

ANEXO1 = (Path(__file__).parent / "fixtures" / "anexo1_cronograma.txt").read_text(
    encoding="utf-8"
)

# (tipo, inicio, fim) na ordem do Anexo I — 22 eventos.
ESPERADO = [
    ("impugnacao", "2026-04-06", "2026-04-10"),
    ("isencao", "2026-04-13", "2026-04-22"),
    ("inscricoes", "2026-04-13", "2026-05-18"),
    ("impugnacao", "2026-04-28", None),
    ("isencao", "2026-05-04", None),
    ("recurso", "2026-05-05", "2026-05-06"),
    ("isencao", "2026-05-18", None),
    ("inscricoes", "2026-05-19", "2026-05-20"),
    ("pagamento", "2026-05-20", None),
    ("atendimento_especializado", "2026-06-05", None),
    ("atendimento_especializado", "2026-06-05", "2026-06-09"),
    ("recurso", "2026-06-08", "2026-06-09"),
    ("atendimento_especializado", "2026-06-19", None),
    ("atendimento_especializado", "2026-06-19", None),
    ("locais_prova", "2026-06-26", None),
    ("prova_objetiva", "2026-07-11", None),
    ("provas_discursivas", "2026-07-12", None),
    ("resultado_provisorio", "2026-07-14", "2026-07-28"),
    ("resultado_provisorio", "2026-07-14", None),
    ("recurso", "2026-07-15", "2026-07-28"),
    ("resultado_provisorio", "2026-07-29", None),
    ("resultado_final", "2026-08-26", None),
]


@pytest.fixture(scope="module")
def resultado():
    return cronograma.extrair_cronograma(ANEXO1)


def test_todos_os_22_eventos_na_ordem(resultado):
    assert [(e["tipo"], e["inicio"], e["fim"]) for e in resultado.eventos] == ESPERADO


def test_titulos_rejuntados(resultado):
    assert resultado.eventos[1]["titulo"] == (
        "Período de solicitação de isenção de taxa de inscrição"
    )
    # titulo quebrado em uma palavra por linha
    assert resultado.eventos[14]["titulo"] == (
        "Divulgação do edital que informará a disponibilização da consulta "
        "aos locais de provas"
    )


def test_fonte_e_anexo_1(resultado):
    assert all(e["fonte"] == "Anexo I" for e in resultado.eventos)


def test_eventos_validam_contra_o_schema(resultado, def_validator):
    validador = def_validator("eventoCronograma")
    for evento in resultado.eventos:
        erros = list(validador.iter_errors(evento))
        assert erros == [], f"{evento['titulo']}: {[e.message for e in erros]}"


def test_notas_de_rodape_nao_viram_evento(resultado):
    assert not any("passíveis de alteração" in (e["titulo"] or "") for e in resultado.eventos)


@pytest.mark.parametrize(
    ("linha", "esperado"),
    [
        ("6 a 10/4/2026", ("2026-04-06", "2026-04-10")),
        ("5 e 6/5/2026", ("2026-05-05", "2026-05-06")),
        ("13/4 a 18/5/2026", ("2026-04-13", "2026-05-18")),
        ("28/4/2026", ("2026-04-28", None)),
        ("Aplicação da prova objetiva", None),
        ("14 a 28/7/2026", ("2026-07-14", "2026-07-28")),
    ],
)
def test_parse_data(linha, esperado):
    assert cronograma._parse_data(linha) == esperado
