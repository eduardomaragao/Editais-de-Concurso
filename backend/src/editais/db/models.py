"""Modelo do edital em revisao.

O documento inteiro (contrato do schema) vive numa coluna JSON — o contrato
e a fonte da verdade, o banco so o carrega. As travas de revisao (arvore,
corte, datas) sao colunas proprias porque nao pertencem ao contrato: o
schema so conhece `edital.conteudo_revisado`, que e espelhado na publicacao.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
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


# --- rede de amigos (gamificacao) -------------------------------------------
# O progresso de estudo continua sendo do USUARIO e vive no aparelho; aqui
# so entra o resumo que o candidato escolhe sincronizar para comparar com
# amigos (pontos, percentual) e os incentivos trocados.


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    apelido: Mapped[str] = mapped_column(String(40))
    codigo: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class Amizade(Base):
    __tablename__ = "amizades"
    __table_args__ = (UniqueConstraint("usuario_id", "amigo_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    amigo_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class ProgressoSync(Base):
    __tablename__ = "progresso_sync"
    __table_args__ = (UniqueConstraint("usuario_id", "edital_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    edital_slug: Mapped[str] = mapped_column(String(120), index=True)
    pontos: Mapped[int] = mapped_column(Integer, default=0)
    percentual: Mapped[float] = mapped_column(Float, default=0.0)
    concluidos: Mapped[int] = mapped_column(Integer, default=0)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_agora, onupdate=_agora
    )


class Incentivo(Base):
    __tablename__ = "incentivos"

    id: Mapped[int] = mapped_column(primary_key=True)
    de_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    para_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    mensagem: Mapped[str] = mapped_column(String(200))
    edital_slug: Mapped[str | None] = mapped_column(String(120), default=None)
    lido: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
