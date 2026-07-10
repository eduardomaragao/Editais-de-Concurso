"""Golden test de ponta a ponta (PARSER_SPEC §11.1 e §11.2).

parse_edital(PDF real) tem que (1) validar contra o schema e (2) bater com
os campos-chave de referencia/pge_al.instance.json. O golden e ASCII e o
parser emite texto literal com acentos, entao textos sao comparados apos
normalizacao; o golden tambem e uma AMOSTRA (6 nos de conteudo, 4 eventos),
entao a comparacao e por contencao, nunca por igualdade total.
"""

import unicodedata

import pytest

from conftest import PDF_PATH
from editais.parser import assemble, validate

pytestmark = pytest.mark.skipif(
    not PDF_PATH.exists(), reason="PDF consolidado nao esta no repo"
)


def _ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def _norm(s: str) -> str:
    return " ".join(_ascii(s).lower().split())


@pytest.fixture(scope="module")
def resultado():
    return assemble.parse_edital(PDF_PATH)


@pytest.fixture(scope="module")
def doc(resultado):
    return resultado.documento


def test_documento_valida_contra_o_schema(doc):
    assert validate.erros(doc) == []


def test_identificacao_bate_com_o_golden(doc, golden):
    e, g = doc["edital"], golden["edital"]
    assert e["orgao"] == g["orgao"]
    assert e["numero"] == g["numero"]
    assert e["publicacao"] == g["publicacao"]
    assert e["banca"] == g["banca"]
    assert e["vagas"] == g["vagas"]
    assert e["remuneracao"] == g["remuneracao"]
    assert e["taxa"] == g["taxa"]
    assert _ascii(e["local_fases"]) == g["local_fases"]
    assert e["validade_anos"] == g["validade_anos"]
    assert e["conteudo_revisado"] is False


def test_versionamento_bate_com_o_golden(doc, golden):
    assert doc["edital"]["retificacoes_incorporadas"] == (
        golden["edital"]["retificacoes_incorporadas"]  # ["no 2", "no 3"]
    )
    assert doc["edital"]["versao_arquivo"] == golden["edital"]["versao_arquivo"]


def test_corte_bate_com_o_golden(doc, golden):
    c, g = dict(doc["edital"]["corte_conteudo"]), dict(golden["edital"]["corte_conteudo"])
    c["trecho"] = _norm(c["trecho"])
    g["trecho"] = _norm(g["trecho"])
    assert c == g


def test_conteudo_contem_os_nos_do_golden(doc, golden):
    materias = {
        _norm(n["titulo"]): n for n in doc["conteudo"] if n["nivel"] == "materia"
    }
    assert len(materias) == 11
    adm = materias["direito administrativo"]
    assert adm["fases"] == ["P1", "P2", "P4"]
    assert materias["direito ambiental"]["fases"] == ["P1"]

    filhos_adm = {
        n["ordem"]: n for n in doc["conteudo"] if n["parent_id"] == adm["id"]
    }
    assert _norm(filhos_adm[7]["titulo"]) == "atos administrativos"
    assert _norm(filhos_adm[21]["titulo"]) == "responsabilidade civil do estado"
    netos_7 = [n for n in doc["conteudo"] if n["parent_id"] == filhos_adm[7]["id"]]
    assert _norm(netos_7[4]["titulo"]) == "vinculacao e discricionariedade"


def test_cronograma_contem_os_eventos_do_golden(doc, golden):
    chaves = {(e["tipo"], e["inicio"], e.get("fim")) for e in doc["cronograma"]}
    assert ("inscricoes", "2026-04-13", "2026-05-18") in chaves
    assert ("isencao", "2026-04-13", "2026-04-22") in chaves
    # datas de prova sao as do ARQUIVO (consolidado ate o nº 3); o golden
    # traz as remarcadas pelo nº 5 — quem reconcilia e o radar, nao o parser
    assert ("prova_objetiva", "2026-07-11", None) in chaves
    assert ("provas_discursivas", "2026-07-12", None) in chaves


def test_dados_prova(doc):
    fases = {f["fase"]: f for f in doc["dados_prova"]["fases"]}
    assert sorted(fases) == ["P1", "P2", "P3", "P4", "P5"]
    p1 = fases["P1"]
    assert (p1["tipo"], p1["duracao"], p1["turno"], p1["questoes"]) == (
        "objetiva", "5h", "tarde", 100
    )
    assert (fases["P2"]["duracao"], fases["P2"]["turno"], fases["P2"]["questoes"]) == (
        "4h", "manha", 5
    )
    assert (fases["P3"]["turno"], fases["P3"]["questoes"]) == ("tarde", 1)
    assert _ascii(fases["P4"]["duracao"]) == "ate 20 min"
    assert fases["P4"]["questoes"] == 4
    assert _ascii(p1["formato"]) == "multipla escolha, com cinco opcoes (A, B, C, D e E)"
    assert fases["P5"]["tipo"] == "titulos"
    assert _ascii(fases["P5"]["formato"]) == "maximo de 10,00 pontos"
    assert doc["dados_prova"]["locais"] == []  # USUARIO


def test_isencoes(doc):
    i = doc["isencoes"]
    assert i["tem_isencao"] is True
    assert (i["inicio"], i["fim"]) == ("2026-04-13", "2026-04-22")
    assert len(i["hipoteses"]) == 6
    assert _norm(i["hipoteses"][0]).startswith("desempregado")


def test_links(doc):
    assert doc["links"]["pagina_banca"] == "http://www.cebraspe.org.br/concursos/pge_al_26"
    assert doc["links"]["site_curso"] is None  # CURADORIA


def test_relatorio_de_revisao(resultado):
    relatorio = resultado.relatorio_revisao
    assert any("[conteudo]" in linha and "agrupada" in linha for linha in relatorio)
    assert any("Arvore de conteudo" in linha for linha in relatorio)
    assert any("Corte" in linha for linha in relatorio)
