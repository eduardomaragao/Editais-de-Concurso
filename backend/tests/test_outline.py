"""Testes do outline.py — os casos de aceite da PARSER_SPEC §4/§11.3.

A fixture item17_direito_administrativo.txt reconstroi o outline plano do
item 17 do edital PGE/AL (texto literal, com acentos) incluindo as
armadilhas reais: numeros de lei no meio de titulos, marcador de
retificacao e profundidade 3.
"""

from pathlib import Path

import pytest

from editais.parser import outline

FIXTURE = (
    Path(__file__).parent / "fixtures" / "item17_direito_administrativo.txt"
).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def adm() -> outline.DisciplinaParseada:
    [(titulo, corpo)] = outline.split_disciplinas(FIXTURE)
    return outline.parse_disciplina(corpo, "adm", titulo)


@pytest.fixture(scope="module")
def por_id(adm) -> dict:
    return {no["id"]: no for no in adm.nos}


# --- numero_valido: a regra do "proximo numero esperado" -------------------


@pytest.mark.parametrize(
    ("num", "estado", "esperado"),
    [
        ((1,), [], True),            # outline comeca em 1
        ((2,), [], False),
        ((2,), [1], True),           # proximo irmao
        ((3,), [1], False),          # pulo
        ((1, 1), [1], True),         # primeiro filho
        ((1, 2), [1], False),        # filho tem que comecar em .1
        ((1, 2), [1, 1], True),      # irmao no nivel 2
        ((2,), [1, 3], True),        # volta ao nivel 1
        ((1, 1, 1), [1, 1], True),   # primeiro neto
        ((14, 133), [12], False),    # Lei 14.133 depois do topico 12: rejeitada
        ((12, 1), [12], True),       # ... enquanto 12.1 seria aceito
    ],
)
def test_numero_valido(num, estado, esperado):
    assert outline.numero_valido(num, estado) is esperado


# --- casos de aceite no Direito Administrativo -----------------------------


def test_materia_e_25_topicos_em_ordem(adm):
    assert adm.nos[0] == {
        "id": "adm",
        "parent_id": None,
        "nivel": "materia",
        "titulo": "DIREITO ADMINISTRATIVO",
    }
    topicos = [n for n in adm.nos if n["nivel"] == "topico"]
    assert [t["ordem"] for t in topicos] == list(range(1, 26))
    assert all(t["parent_id"] == "adm" for t in topicos)


def test_topico_7_atos_administrativos_com_subtopicos(adm, por_id):
    topico = por_id["adm-7"]
    assert topico["titulo"] == "Atos administrativos"
    assert topico["ordem"] == 7
    assert topico["nivel"] == "topico"

    filhos = [n for n in adm.nos if n["parent_id"] == "adm-7"]
    assert [f["ordem"] for f in filhos] == list(range(1, 12))
    assert [f["titulo"] for f in filhos[:5]] == [
        "Elementos",
        "Pressupostos",
        "Atributos",
        "Classificação",
        "Vinculação e discricionariedade",
    ]
    vinculacao = por_id["adm-7-5"]
    assert vinculacao["nivel"] == "subtopico"
    assert vinculacao["ordem"] == 5


def test_topico_21_responsabilidade_civil_sem_filhos(adm, por_id):
    topico = por_id["adm-21"]
    assert topico["titulo"] == "Responsabilidade civil do Estado"
    assert topico["ordem"] == 21
    assert not [n for n in adm.nos if n["parent_id"] == "adm-21"]


def test_lei_14133_nao_vira_no(adm, por_id):
    topico = por_id["adm-12"]
    assert topico["titulo"] == "Licitações e contratos administrativos: Lei nº 14.133/2021"
    assert not any(no["id"].startswith("adm-12-") for no in adm.nos)


def test_profundidade_3_vira_subtopico_do_no_imediatamente_acima(por_id):
    neto = por_id["adm-4-1-1"]
    assert neto == {
        "id": "adm-4-1-1",
        "parent_id": "adm-4-1",
        "nivel": "subtopico",
        "titulo": "Finalidade, limites e objeto",
        "ordem": 1,
    }


def test_marcador_de_retificacao_sai_do_titulo_e_vai_para_versioning(adm, por_id):
    assert por_id["adm-10"]["titulo"] == "Militares do estado"
    assert adm.marcadores_retificacao == ["nº 3"]


def test_nos_validam_contra_o_schema(adm, def_validator):
    validador = def_validator("noConteudo")
    for no in adm.nos:
        erros = list(validador.iter_errors(no))
        assert erros == [], f"{no['id']}: {[e.message for e in erros]}"


# --- caso sintetico da spec: lei e artigo no meio do titulo ----------------


def test_sintetico_art_5_e_lei_9784_nao_quebram_titulo():
    texto = (
        "1 Princípios gerais da atuação administrativa previstos no art. 5º "
        "da Constituição Federal. 2 Processo administrativo: Lei nº 9.784/1999 "
        "e Decreto nº 20.910/1932 Prescrição contra a fazenda pública. "
        "3 Encerramento do procedimento."
    )
    disciplina = outline.parse_disciplina(texto, "x", "SINTÉTICO")
    topicos = [n for n in disciplina.nos if n["nivel"] == "topico"]
    assert [t["ordem"] for t in topicos] == [1, 2, 3]
    # "1932 Prescrição" parece marcador (numero + espaco + maiuscula), mas a
    # validacao sequencial rejeita; o titulo fica inteiro.
    assert topicos[1]["titulo"] == (
        "Processo administrativo: Lei nº 9.784/1999 e Decreto nº 20.910/1932 "
        "Prescrição contra a fazenda pública"
    )
    assert not any(n["nivel"] == "subtopico" for n in disciplina.nos)


def test_outline_que_nao_comeca_em_1_nao_gera_nos():
    disciplina = outline.parse_disciplina("3 Foo. 4 Bar.", "x", "X")
    assert disciplina.nos == [disciplina.materia]


# --- split de disciplinas e parse_item17 -----------------------------------

DOIS_ITENS = (
    "DIREITO ADMINISTRATIVO: 1 Estado. 1.1 Funções. 2 Atos administrativos. "
    "DIREITO AMBIENTAL: 1 Princípios do direito ambiental. 2 Competência "
    "ambiental. 2.1 Competência legislativa. 2.2 Competência material. "
    "3 Política Nacional do Meio Ambiente: Lei nº 6.938/1981."
)


def test_split_disciplinas_ignora_siglas_com_dois_pontos():
    partes = outline.split_disciplinas(DOIS_ITENS)
    assert [titulo for titulo, _ in partes] == [
        "DIREITO ADMINISTRATIVO",
        "DIREITO AMBIENTAL",
    ]


def test_parse_item17_gera_ids_e_ordem_por_disciplina():
    adm_d, amb = outline.parse_item17(DOIS_ITENS)
    assert adm_d.materia["id"] == "direito-administrativo"
    assert adm_d.materia["ordem"] == 1
    assert amb.materia["id"] == "direito-ambiental"
    assert amb.materia["ordem"] == 2
    ambientais = {n["id"]: n for n in amb.nos}
    assert ambientais["direito-ambiental-2-1"]["titulo"] == "Competência legislativa"
    assert ambientais["direito-ambiental-3"]["titulo"] == (
        "Política Nacional do Meio Ambiente: Lei nº 6.938/1981"
    )
