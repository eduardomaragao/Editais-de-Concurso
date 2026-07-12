"""Testes da API social: registro, amizade por codigo, progresso e incentivos."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from editais.admin.app import criar_app
from editais.db import Base


@pytest.fixture()
def cliente():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return TestClient(criar_app(engine))


def _registrar(cliente, apelido):
    resposta = cliente.post("/api/social/usuarios", json={"apelido": apelido})
    assert resposta.status_code == 201
    return resposta.json()


def _cabecalho(usuario):
    return {"X-Token": usuario["token"]}


@pytest.fixture()
def dupla(cliente):
    edu = _registrar(cliente, "Edu")
    ana = _registrar(cliente, "Ana")
    resposta = cliente.post(
        "/api/social/amigos", json={"codigo": ana["codigo"]}, headers=_cabecalho(edu)
    )
    assert resposta.status_code == 201
    return edu, ana


def test_registro_devolve_codigo_e_token(cliente):
    usuario = _registrar(cliente, "Edu")
    assert len(usuario["codigo"]) == 6
    assert usuario["token"]


def test_token_invalido_e_401(cliente):
    resposta = cliente.get(
        "/api/social/amigos", params={"edital": "x"}, headers={"X-Token": "errado"}
    )
    assert resposta.status_code == 401


def test_amizade_e_mutua(cliente, dupla):
    edu, ana = dupla
    # Ana ve Edu sem precisar adicionar de volta
    lista = cliente.get(
        "/api/social/amigos", params={"edital": "pge"}, headers=_cabecalho(ana)
    ).json()
    assert [a["apelido"] for a in lista] == ["Edu"]


def test_nao_pode_adicionar_a_si_mesmo_nem_duplicar(cliente, dupla):
    edu, ana = dupla
    proprio = cliente.post(
        "/api/social/amigos", json={"codigo": edu["codigo"]}, headers=_cabecalho(edu)
    )
    assert proprio.status_code == 400
    de_novo = cliente.post(
        "/api/social/amigos", json={"codigo": edu["codigo"]}, headers=_cabecalho(ana)
    )
    assert de_novo.status_code == 409


def test_codigo_com_hifen_e_minusculas_funciona(cliente, dupla):
    edu, ana = dupla
    bia = _registrar(cliente, "Bia")
    codigo_formatado = f"{ana['codigo'][:3].lower()}-{ana['codigo'][3:].lower()}"
    resposta = cliente.post(
        "/api/social/amigos", json={"codigo": codigo_formatado}, headers=_cabecalho(bia)
    )
    assert resposta.status_code == 201


def test_progresso_aparece_no_ranking_dos_amigos(cliente, dupla):
    edu, ana = dupla
    cliente.put(
        "/api/social/progresso",
        json={"edital": "pge-al-1-2026", "pontos": 350, "percentual": 0.42, "concluidos": 30},
        headers=_cabecalho(ana),
    )
    lista = cliente.get(
        "/api/social/amigos",
        params={"edital": "pge-al-1-2026"},
        headers=_cabecalho(edu),
    ).json()
    assert lista[0]["apelido"] == "Ana"
    assert lista[0]["pontos"] == 350
    assert lista[0]["percentual"] == 0.42


def test_progresso_e_upsert(cliente, dupla):
    edu, ana = dupla
    for pontos in (10, 250):
        cliente.put(
            "/api/social/progresso",
            json={"edital": "pge", "pontos": pontos, "percentual": 0.1, "concluidos": 1},
            headers=_cabecalho(ana),
        )
    lista = cliente.get(
        "/api/social/amigos", params={"edital": "pge"}, headers=_cabecalho(edu)
    ).json()
    assert lista[0]["pontos"] == 250


def test_incentivo_so_entre_amigos(cliente, dupla):
    edu, ana = dupla
    bia = _registrar(cliente, "Bia")
    resposta = cliente.post(
        "/api/social/incentivos",
        json={"codigo": edu["codigo"], "mensagem": "Vai!"},
        headers=_cabecalho(bia),
    )
    assert resposta.status_code == 403


def test_fluxo_de_incentivo(cliente, dupla):
    edu, ana = dupla
    cliente.post(
        "/api/social/incentivos",
        json={"codigo": ana["codigo"], "mensagem": "Não para agora! 🔥"},
        headers=_cabecalho(edu),
    )
    recebidos = cliente.get("/api/social/incentivos", headers=_cabecalho(ana)).json()
    assert len(recebidos) == 1
    assert recebidos[0]["de"] == "Edu"
    assert recebidos[0]["mensagem"] == "Não para agora! 🔥"
    # marcados como lidos: segunda chamada vem vazia
    assert cliente.get("/api/social/incentivos", headers=_cabecalho(ana)).json() == []
