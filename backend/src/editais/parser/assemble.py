"""Composicao do dict final (PARSER_SPEC §10).

parse_edital(pdf) roda o pipeline inteiro (pdf_text -> sectioner ->
extratores), compoe o documento no formato do contrato, valida contra o
schema (invalido = erro fatal, nao emite rascunho) e devolve tambem o
relatorio de revisao: tudo que os extratores marcaram para conferencia
humana, com prefixo do modulo de origem.

Campos que nao sao do parser: provas_anteriores=[] (CURADORIA),
dados_prova.locais=[] (USUARIO), links.site_curso=None (CURADORIA),
radar (ultima_retificacao_publicada / radar_desatualizado) fica de fora —
quem preenche e o servico do radar, depois.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from editais.parser import pdf_text, sectioner, versioning
from editais.parser.extractors import (
    conteudo,
    corte,
    cronograma,
    dados_prova,
    identificacao,
    isencoes,
)
from editais.parser.validate import validar

RE_URL_BANCA = re.compile(r"https?://[^\s,)]+")


@dataclass
class ResultadoParse:
    documento: dict  # valido contra edital.schema.json
    relatorio_revisao: list[str] = field(default_factory=list)
    candidatas_corte: dict = field(default_factory=dict)  # tela de conferencia


def parse_edital(pdf_path: str | Path) -> ResultadoParse:
    texto = pdf_text.texto_limpo(pdf_path)
    secoes = sectioner.dividir(texto.texto)

    ident = identificacao.extrair_identificacao(secoes)
    versao = versioning.extrair_versao(texto.texto)
    crono = cronograma.extrair_cronograma(secoes.anexos.get("I", ""))
    arvore = conteudo.extrair_conteudo(secoes)
    dados = dados_prova.extrair_dados_prova(secoes)
    isen = isencoes.extrair_isencoes(secoes, crono.eventos)
    corte_res = corte.extrair_corte(
        secoes.itens.get(16, texto.texto), publicacao=ident.edital.get("publicacao")
    )

    documento = {
        "edital": {
            **ident.edital,
            "versao_arquivo": versao.versao_arquivo,
            "retificacoes_incorporadas": versao.retificacoes_incorporadas,
            "conteudo_revisado": False,  # trava: so o Eduardo destrava
            "corte_conteudo": corte_res.corte,
        },
        "cronograma": crono.eventos,
        "dados_prova": dados.dados_prova,
        "conteudo": arvore.nos,
        "provas_anteriores": [],
        "isencoes": isen.isencoes,
        "links": {
            "site_curso": None,
            "edital_oficial": None,
            "pagina_banca": _url_banca(secoes.itens.get(1, "")),
        },
    }
    validar(documento)

    relatorio = _relatorio(
        [
            ("identificacao", ident.pendencias),
            ("versioning", versao.pendencias),
            ("cronograma", crono.pendencias),
            ("conteudo", arvore.pendencias),
            ("dados_prova", dados.pendencias),
            ("isencoes", isen.pendencias),
            ("corte", corte_res.pendencias),
        ]
    )
    relatorio.extend(
        [
            "[revisao] Arvore de conteudo: estrutura e titulos literais — REVISAO obrigatoria.",
            "[revisao] Corte de lei/jurisprudencia — REVISAO obrigatoria.",
            "[revisao] Data/hora das provas — REVISAO obrigatoria.",
        ]
    )
    return ResultadoParse(
        documento=documento,
        relatorio_revisao=relatorio,
        candidatas_corte=corte_res.candidatas,
    )


def _relatorio(blocos: list[tuple[str, list[str]]]) -> list[str]:
    return [f"[{origem}] {p}" for origem, pendencias in blocos for p in pendencias]


def _url_banca(item1: str) -> str | None:
    m = RE_URL_BANCA.search(item1)
    return m.group(0) if m else None
