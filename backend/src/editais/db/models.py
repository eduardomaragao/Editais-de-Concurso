"""Modelo do edital em revisao.

O documento inteiro (contrato do schema) vive numa coluna JSON — o contrato
e a fonte da verdade, o banco so o carrega. As travas de revisao (arvore,
corte, datas) sao colunas proprias porque nao pertencem ao contrato: o
schema so conhece `edital.conteudo_revisado`, que e espelhado na publicacao.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from editais.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class EditalRow(Base):
    __tablename__ = "editais"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    documento: Mapped[dict] = mapped_column(JSON)
    relatorio: Mapped[list] = mapped_column(JSON, default=list)
    candidatas_corte: Mapped[dict] = mapped_column(JSON, default=dict)
    arquivo_pdf: Mapped[str | None] = mapped_column(String(500), default=None)

    # Travas de revisao (human-in-the-loop). Nada publica com alguma em False.
    conteudo_revisado: Mapped[bool] = mapped_column(Boolean, default=False)
    corte_revisado: Mapped[bool] = mapped_column(Boolean, default=False)
    datas_revisadas: Mapped[bool] = mapped_column(Boolean, default=False)

    publicado: Mapped[bool] = mapped_column(Boolean, default=False)
    publicado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora, onupdate=_agora
    )
