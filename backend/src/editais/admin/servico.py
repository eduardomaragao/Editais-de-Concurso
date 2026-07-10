"""Operacoes de revisao do painel admin.

Toda mutacao no documento passa por aqui: edita uma copia, valida contra o
schema e so entao grava — um clique errado nunca corrompe o rascunho.
Editar a arvore depois de confirmada derruba a confirmacao (a trava fecha
de novo). Publicar exige TODAS as travas abertas, inclusive radar rodado e
nao desatualizado (regra inviolavel nº 4 do CLAUDE.md).
"""

import copy
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from editais.db.models import EditalRow
from editais.parser import assemble, validate
from editais.radar import core as radar


class ErroRevisao(Exception):
    """Operacao invalida ou que deixaria o documento invalido."""


class TravaPublicacao(Exception):
    def __init__(self, travas: list[str]):
        self.travas = travas
        super().__init__("; ".join(travas))


# --- importacao -------------------------------------------------------------


def importar_pdf(sessao: Session, caminho_pdf: str | Path) -> EditalRow:
    resultado = assemble.parse_edital(caminho_pdf)
    return importar_documento(
        sessao,
        resultado.documento,
        relatorio=resultado.relatorio_revisao,
        candidatas=resultado.candidatas_corte,
        arquivo_pdf=str(caminho_pdf),
    )


def importar_documento(
    sessao: Session,
    documento: dict,
    relatorio: list | None = None,
    candidatas: dict | None = None,
    arquivo_pdf: str | None = None,
) -> EditalRow:
    """Cria o rascunho; reupload do mesmo edital substitui o documento e
    FECHA todas as travas de novo (revisao recomeca — e o fluxo pos-retificacao)."""
    slug = _slug_edital(documento)
    row = sessao.scalar(select(EditalRow).where(EditalRow.slug == slug))
    if row is None:
        row = EditalRow(slug=slug)
        sessao.add(row)
    row.documento = documento
    row.relatorio = relatorio or []
    row.candidatas_corte = candidatas or {}
    row.arquivo_pdf = arquivo_pdf
    row.conteudo_revisado = False
    row.corte_revisado = False
    row.datas_revisadas = False
    row.publicado = False
    row.publicado_em = None
    sessao.flush()
    return row


def listar(sessao: Session) -> list[EditalRow]:
    return list(sessao.scalars(select(EditalRow).order_by(EditalRow.criado_em)))


def obter(sessao: Session, edital_id: int) -> EditalRow:
    row = sessao.get(EditalRow, edital_id)
    if row is None:
        raise ErroRevisao(f"Edital {edital_id} nao encontrado.")
    return row


def obter_por_slug(sessao: Session, slug: str) -> EditalRow | None:
    return sessao.scalar(select(EditalRow).where(EditalRow.slug == slug))


# --- revisao da arvore (promover / rebaixar / editar titulo) ----------------


def editar_titulo(row: EditalRow, no_id: str, titulo: str) -> None:
    titulo = " ".join(titulo.split())
    if not titulo:
        raise ErroRevisao("Titulo nao pode ficar vazio.")
    doc = copy.deepcopy(row.documento)
    _achar_no(doc, no_id)["titulo"] = titulo
    _gravar_conteudo(row, doc)


def promover(row: EditalRow, no_id: str) -> None:
    """Sobe o no um nivel: subtopico vira topico (ou subtopico do avo).
    Os filhos continuam pendurados nele."""
    doc = copy.deepcopy(row.documento)
    no = _achar_no(doc, no_id)
    if no["nivel"] == "materia":
        raise ErroRevisao("Materia ja esta no topo.")
    pai = _achar_no(doc, no["parent_id"])
    if pai["nivel"] == "materia":
        raise ErroRevisao("Topico nao pode virar materia.")
    no["parent_id"] = pai["parent_id"]
    avo = _achar_no(doc, pai["parent_id"])
    no["nivel"] = "topico" if avo["nivel"] == "materia" else "subtopico"
    no["ordem"] = _proxima_ordem(doc, no["parent_id"], excluido=no_id)
    _gravar_conteudo(row, doc)


def rebaixar(row: EditalRow, no_id: str) -> None:
    """Desce o no um nivel: vira subtopico do irmao imediatamente anterior."""
    doc = copy.deepcopy(row.documento)
    no = _achar_no(doc, no_id)
    if no["nivel"] == "materia":
        raise ErroRevisao("Materia nao pode ser rebaixada.")
    irmaos_anteriores = [
        n
        for n in doc["conteudo"]
        if n["parent_id"] == no["parent_id"]
        and n["id"] != no_id
        and (n.get("ordem") or 0) < (no.get("ordem") or 0)
    ]
    if not irmaos_anteriores:
        raise ErroRevisao("Nao ha irmao anterior para receber o no.")
    novo_pai = max(irmaos_anteriores, key=lambda n: n.get("ordem") or 0)
    no["parent_id"] = novo_pai["id"]
    no["nivel"] = "subtopico"
    no["ordem"] = _proxima_ordem(doc, novo_pai["id"], excluido=no_id)
    _gravar_conteudo(row, doc)


# --- confirmacoes e travas ---------------------------------------------------


def confirmar_arvore(row: EditalRow) -> None:
    row.conteudo_revisado = True


def confirmar_corte(
    row: EditalRow,
    legislacao_ate: str | None = None,
    jurisprudencia_ate: str | None = None,
) -> None:
    doc = copy.deepcopy(row.documento)
    corte = doc["edital"]["corte_conteudo"]
    if legislacao_ate:
        corte["legislacao_ate"] = legislacao_ate
    if jurisprudencia_ate:
        corte["jurisprudencia_ate"] = jurisprudencia_ate
    _validar(doc)
    row.documento = doc
    row.corte_revisado = True


def confirmar_datas(row: EditalRow) -> None:
    row.datas_revisadas = True


def rodar_radar(row: EditalRow, fetcher: radar.FetcherBanca) -> radar.RadarResultado:
    doc = copy.deepcopy(row.documento)
    resultado = radar.verificar(doc, fetcher)
    _validar(doc)
    row.documento = doc
    return resultado


def travas(row: EditalRow) -> list[str]:
    pendentes = []
    if not row.conteudo_revisado:
        pendentes.append("Árvore de conteúdo não revisada.")
    if not row.corte_revisado:
        pendentes.append("Corte de lei/jurisprudência não confirmado.")
    if not row.datas_revisadas:
        pendentes.append("Data/hora das provas não confirmadas.")
    radar_flag = row.documento["edital"].get("radar_desatualizado")
    if radar_flag is None:
        pendentes.append("Radar ainda não rodado.")
    elif radar_flag:
        pendentes.append(
            "Radar: existe retificação não incorporada — reenvie o consolidado."
        )
    return pendentes


def publicar(row: EditalRow) -> None:
    pendentes = travas(row)
    if pendentes:
        raise TravaPublicacao(pendentes)
    doc = copy.deepcopy(row.documento)
    doc["edital"]["conteudo_revisado"] = True  # espelha a trava no contrato
    _validar(doc)
    row.documento = doc
    row.publicado = True
    row.publicado_em = datetime.now(timezone.utc)


# --- helpers -----------------------------------------------------------------


def _achar_no(doc: dict, no_id: str) -> dict:
    for no in doc["conteudo"]:
        if no["id"] == no_id:
            return no
    raise ErroRevisao(f"Nó {no_id!r} não existe na árvore.")


def _proxima_ordem(doc: dict, parent_id: str | None, excluido: str) -> int:
    ordens = [
        n.get("ordem") or 0
        for n in doc["conteudo"]
        if n["parent_id"] == parent_id and n["id"] != excluido
    ]
    return max(ordens, default=0) + 1


def _gravar_conteudo(row: EditalRow, doc: dict) -> None:
    _validar(doc)
    row.documento = doc
    # mexeu na arvore, a confirmacao cai — precisa revisar de novo
    row.conteudo_revisado = False


def _validar(doc: dict) -> None:
    erros = validate.erros(doc)
    if erros:
        raise ErroRevisao("Alteração deixaria o documento inválido: " + "; ".join(erros))


def _slug_edital(documento: dict) -> str:
    orgao = documento["edital"]["orgao"]
    numero = documento["edital"]["numero"]
    bruto = f"{orgao}-{numero}"
    ascii_ = unicodedata.normalize("NFKD", bruto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_.lower()).strip("-")
