"""Persistencia do painel de revisao.

Dev: SQLite em backend/data/editais.db (zero setup). Producao: Postgres via
variavel de ambiente EDITAIS_DATABASE_URL (instalar o extra [postgres]).
O parser continua biblioteca pura e nao depende deste pacote.
"""

import json
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


DATA_DIR = Path(__file__).resolve().parents[3] / "data"


def url_padrao() -> str:
    return os.environ.get("EDITAIS_DATABASE_URL", f"sqlite:///{DATA_DIR / 'editais.db'}")


def criar_engine(url: str | None = None):
    url = url or url_padrao()
    if url.startswith("sqlite:///"):
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        url,
        json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False),
    )


def criar_sessionmaker(engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)
