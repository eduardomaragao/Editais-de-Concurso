"""Semeia o banco local com o edital do piloto (PGE/AL).

Uso: .venv\\Scripts\\python.exe scripts\\seed_pge_al.py [--publicar]

--publicar: SO PARA DEV — confirma as travas e publica com um radar fake
"em dia", para o app Flutter (que so ve publicados) ter o que consumir.
Em producao quem faz isso e o Eduardo, no painel.
"""

import sys
from pathlib import Path

from editais.admin import servico
from editais.db import Base, criar_engine, criar_sessionmaker
from editais.radar.core import EditalPublicado

PDF = (
    Path(__file__).resolve().parents[2]
    / "editais" / "pge-al-2026" / "PGE_AL_2026_Edital_1_Abertura_Atualizado.pdf"
)


class _RadarFakeEmDia:
    def fetch_editais(self):
        return [EditalPublicado(3, "2026-05-06", "Edital nº 3 - Retificação")]


engine = criar_engine()
Base.metadata.create_all(engine)
with criar_sessionmaker(engine)() as sessao:
    row = servico.importar_pdf(sessao, PDF)
    if "--publicar" in sys.argv:
        servico.confirmar_arvore(row)
        servico.confirmar_corte(row)
        servico.confirmar_datas(row)
        servico.rodar_radar(row, _RadarFakeEmDia())
        servico.publicar(row)
    sessao.commit()
    status = "PUBLICADO (dev)" if row.publicado else f"{len(servico.travas(row))} travas"
    print(f"ok: edital {row.slug} (id {row.id}), "
          f"{len(row.documento['conteudo'])} nos, {status}")
