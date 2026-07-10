"""Semeia o banco local com o edital do piloto (PGE/AL).

Uso: .venv\\Scripts\\python.exe scripts\\seed_pge_al.py
"""

from pathlib import Path

from editais.admin import servico
from editais.db import Base, criar_engine, criar_sessionmaker

PDF = (
    Path(__file__).resolve().parents[2]
    / "editais" / "pge-al-2026" / "PGE_AL_2026_Edital_1_Abertura_Atualizado.pdf"
)

engine = criar_engine()
Base.metadata.create_all(engine)
with criar_sessionmaker(engine)() as sessao:
    row = servico.importar_pdf(sessao, PDF)
    sessao.commit()
    print(f"ok: edital {row.slug} (id {row.id}), {len(row.documento['conteudo'])} nos, "
          f"{len(servico.travas(row))} travas")
