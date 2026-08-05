"""Gera preview.html juntando preview.body.html + fontes.css.

O CSP dos artifacts bloqueia CDN de fonte, entao as fontes entram como data URI
dentro do proprio <style>. Edite sempre o preview.body.html — o preview.html e
gerado.

    python3 build.py
"""
from pathlib import Path

aqui = Path(__file__).parent
corpo = (aqui / "preview.body.html").read_text(encoding="utf-8")
fontes = (aqui / "fontes.css").read_text(encoding="utf-8")

if "/*@FONTES@*/" not in corpo:
    raise SystemExit("marcador /*@FONTES@*/ sumiu do preview.body.html")

saida = corpo.replace("/*@FONTES@*/", fontes, 1)
(aqui / "preview.html").write_text(saida, encoding="utf-8")
print(f"preview.html gerado — {len(saida)/1024:.0f} KB")
