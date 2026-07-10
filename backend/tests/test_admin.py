"""Testes do painel de revisao: servico (travas, arvore, publicacao) e rotas.

Usa o golden como documento (ele e valido por contrato) num SQLite em
memoria — nada de PDF nem rede aqui.
"""

import copy

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from editais.admin import servico
from editais.admin.app import criar_app
from editais.db import Base, criar_sessionmaker
from editais.radar.core import EditalPublicado


class FetcherFake:
    def __init__(self, editais):
        self._editais = editais

    def fetch_editais(self):
        return self._editais


SITE_EM_DIA = [
    EditalPublicado(1, "2026-03-31", "Edital nº 1 - Abertura"),
    EditalPublicado(3, "2026-05-06", "Edital nº 3 - Retificação"),
]
SITE_DESATUALIZADO = SITE_EM_DIA + [
    EditalPublicado(5, "2026-06-08", "Edital nº 5 - Retificação de subitens"),
]


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def sessao(engine):
    with criar_sessionmaker(engine)() as s:
        yield s
        s.commit()


@pytest.fixture()
def row(sessao, golden):
    return servico.importar_documento(sessao, copy.deepcopy(golden))


def _confirmar_tudo(row):
    servico.confirmar_arvore(row)
    servico.confirmar_corte(row)
    servico.confirmar_datas(row)
    servico.rodar_radar(row, FetcherFake(SITE_EM_DIA))


# --- importacao ---------------------------------------------------------------


def test_importar_cria_rascunho_travado(row):
    assert row.slug == "pge-al-1-2026"
    assert row.publicado is False
    assert row.conteudo_revisado is False
    assert len(servico.travas(row)) == 4  # arvore, corte, datas, radar desatualizado


def test_reimportar_fecha_as_travas_de_novo(sessao, row, golden):
    _confirmar_tudo(row)
    servico.publicar(row)
    novo = servico.importar_documento(sessao, copy.deepcopy(golden))
    assert novo.id == row.id  # mesmo edital, substituido
    assert novo.publicado is False
    assert novo.conteudo_revisado is False


# --- arvore -------------------------------------------------------------------


def test_editar_titulo(row):
    servico.editar_titulo(row, "adm-7-5", "Vinculação e discricionariedade (revisto)")
    no = servico._achar_no(row.documento, "adm-7-5")
    assert no["titulo"] == "Vinculação e discricionariedade (revisto)"


def test_editar_titulo_vazio_e_rejeitado(row):
    with pytest.raises(servico.ErroRevisao):
        servico.editar_titulo(row, "adm-7-5", "   ")


def test_promover_subtopico_vira_topico(row):
    servico.promover(row, "adm-7-5")
    no = servico._achar_no(row.documento, "adm-7-5")
    assert no["nivel"] == "topico"
    assert no["parent_id"] == "adm"
    assert no["ordem"] == 22  # depois do topico 21


def test_promover_topico_nao_vira_materia(row):
    with pytest.raises(servico.ErroRevisao):
        servico.promover(row, "adm-7")


def test_rebaixar_para_o_irmao_anterior(row):
    servico.rebaixar(row, "adm-21")
    no = servico._achar_no(row.documento, "adm-21")
    assert no["nivel"] == "subtopico"
    assert no["parent_id"] == "adm-7"
    assert no["ordem"] == 6  # adm-7-5 tem ordem 5


def test_rebaixar_sem_irmao_anterior_e_rejeitado(row):
    with pytest.raises(servico.ErroRevisao):
        servico.rebaixar(row, "adm-7")


def test_editar_arvore_fecha_a_trava_de_novo(row):
    servico.confirmar_arvore(row)
    assert row.conteudo_revisado is True
    servico.editar_titulo(row, "adm-7", "Atos administrativos")
    assert row.conteudo_revisado is False


# --- travas e publicacao --------------------------------------------------------


def test_publicar_travado_levanta_excecao(row):
    with pytest.raises(servico.TravaPublicacao) as exc:
        servico.publicar(row)
    assert len(exc.value.travas) == 4


def test_fluxo_completo_de_publicacao(row):
    _confirmar_tudo(row)
    assert servico.travas(row) == []
    servico.publicar(row)
    assert row.publicado is True
    assert row.documento["edital"]["conteudo_revisado"] is True
    assert row.documento["edital"]["radar_desatualizado"] is False


def test_radar_desatualizado_trava_publicacao(row):
    servico.confirmar_arvore(row)
    servico.confirmar_corte(row)
    servico.confirmar_datas(row)
    servico.rodar_radar(row, FetcherFake(SITE_DESATUALIZADO))
    with pytest.raises(servico.TravaPublicacao) as exc:
        servico.publicar(row)
    assert any("retificação não incorporada" in t for t in exc.value.travas)


def test_confirmar_corte_com_data_editada(row):
    servico.confirmar_corte(row, legislacao_ate="2026-04-01")
    assert row.documento["edital"]["corte_conteudo"]["legislacao_ate"] == "2026-04-01"
    assert row.corte_revisado is True


# --- rotas --------------------------------------------------------------------


@pytest.fixture()
def cliente(engine, sessao, golden):
    row = servico.importar_documento(sessao, copy.deepcopy(golden))
    sessao.commit()
    return TestClient(criar_app(engine)), row


def test_paginas_do_painel(cliente):
    client, row = cliente
    assert "pge-al-1-2026" in client.get("/").text
    hub = client.get(f"/editais/{row.id}")
    assert hub.status_code == 200
    assert "Travas de publicação" in hub.text
    arvore = client.get(f"/editais/{row.id}/conteudo")
    assert "Direito Administrativo" in arvore.text


def test_editar_titulo_pela_rota(cliente):
    client, row = cliente
    resposta = client.post(
        f"/editais/{row.id}/conteudo/adm-7-5/titulo",
        data={"titulo": "Novo título literal"},
    )
    assert "Novo título literal" in resposta.text


def test_publicar_travado_mostra_erro(cliente):
    client, row = cliente
    resposta = client.post(f"/editais/{row.id}/publicar")
    assert "Publicação travada" in resposta.text


def test_api_so_expoe_publicados(cliente, sessao):
    client, row = cliente
    assert client.get("/api/editais").json() == []
    assert client.get(f"/api/editais/{row.slug}").status_code == 404

    _confirmar_tudo(row)
    servico.publicar(row)
    sessao.commit()

    lista = client.get("/api/editais").json()
    assert [e["slug"] for e in lista] == ["pge-al-1-2026"]
    documento = client.get(f"/api/editais/{row.slug}").json()
    assert documento["edital"]["conteudo_revisado"] is True
