#!/usr/bin/env python3
"""Gera DXF (2D), STL (3D) e script Ruby do SketchUp para as duas plantas de banheiro.

Unidades: centímetros. Pé-direito informado pelo Eduardo: 253 cm no ambiente
de 282 e 253,8 cm no de 274 (campo "H" de cada planta).
Origem (0,0) = canto interno inferior-esquerdo de cada ambiente; eixo Y aponta
para a parede do fundo (topo da imagem).
"""
import math
import os

ESPESSURA_PAREDE = 12.0 # assumida (não cotada nas imagens)
VIDRO = 0.8             # espessura do vidro do box
H_VIDRO = 200.0

OUT = os.environ.get("OUT_DIR", ".")


# ---------------------------------------------------------------- geometria

def paredes(W, D, T, porta, H):
    """Caixas (x0,y0,x1,y1,z0,z1) das 4 paredes, com vão de porta na parede
    inferior de x=a até x=a+w (vão até o teto — sem verga, ajustar no SketchUp)."""
    a, w = porta
    return [
        (-T, -T, 0, D + T, 0, H),          # esquerda
        (W, -T, W + T, D + T, 0, H),       # direita
        (0, D, W, D + T, 0, H),            # fundo (topo da imagem)
        (0, -T, a, 0, 0, H),               # frente, trecho esquerdo
        (a + w, -T, W, 0, 0, H),           # frente, trecho direito
    ]


def oval(cx, cy, rx, ry, n=32):
    return [(cx + rx * math.cos(2 * math.pi * i / n),
             cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


# Planta 1 — 282 x 176 (imagem 05d80bd8)
P1 = {
    "nome": "banheiro_282x176",
    "W": 282.0, "D": 176.0, "H": 253.0,
    "porta": (96.8, 76.7),           # cotas 96,8 / 76,7 / 103,5 na base
    "caixas": [
        # box de banho 87 x 93 no canto superior esquerdo (vidro)
        (87 - VIDRO, 176 - 93, 87, 176, 0, H_VIDRO),
        (0, 176 - 93, 40, 176 - 93 + VIDRO, 0, H_VIDRO),   # abertura de 47 cm
        # vaso sanitário (centro da cota 160 a partir da parede direita)
        (103, 176 - 68, 141, 176, 0, 42),
        # bancada da pia junto à parede direita: 48 de fundo x 89 de comprimento
        (282 - 48, 0, 282, 89, 0, 75),
        # cuba de apoio sobre a bancada
        (282 - 42, 25, 282 - 6, 61, 75, 90),
    ],
    "ovais2d": [],
}

# Planta 2 — 274 x 165 (imagem c412608f; 164,6 à esquerda / 169,7 à direita —
# adotado 165, conferir no modelo)
P2 = {
    "nome": "banheiro_274x165",
    "W": 274.0, "D": 165.0, "H": 253.8,
    "porta": (90.1, 100.0),          # cotas 90,1 / 100 / 90 na base
    "caixas": [
        # vaso sanitário, centro a 45,5 da parede esquerda, junto ao fundo
        (45.5 - 19, 165 - 68, 45.5 + 19, 165, 0, 42),
        # box de banho 85,4 x 92 no canto inferior direito (vidro)
        (274 - 85.4, 0, 274 - 85.4 + VIDRO, 92, 0, H_VIDRO),
        (274 - 85.4, 92 - VIDRO, 274 - 40, 92, 0, H_VIDRO),  # abertura de 40 cm
        # lavatório oval (cota 45) — posição aproximada, ajustar no SketchUp
        (150 - 22.5, 10, 150 + 22.5, 45, 0, 85),
    ],
    "ovais2d": [(150, 27.5, 22.5, 17.5)],
}


# ---------------------------------------------------------------- DXF (2D)

def dxf(plan):
    W, D, T = plan["W"], plan["D"], ESPESSURA_PAREDE
    a, w = plan["porta"]
    linhas = []

    def rect(x0, y0, x1, y1):
        linhas.extend([(x0, y0, x1, y0), (x1, y0, x1, y1),
                       (x1, y1, x0, y1), (x0, y1, x0, y0)])

    rect(-T, -T, W + T, D + T)                     # face externa
    # face interna com vão da porta na parede da frente
    linhas += [(0, 0, a, 0), (a + w, 0, W, 0),      # frente
               (W, 0, W, D), (W, D, 0, D), (0, D, 0, 0)]
    linhas += [(a, 0, a, -T), (a + w, 0, a + w, -T)]  # ombreiras
    for (x0, y0, x1, y1, _z0, _z1) in plan["caixas"]:
        rect(x0, y0, x1, y1)

    ents = []
    for (x1, y1, x2, y2) in linhas:
        ents.append(f"0\nLINE\n8\n0\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n"
                    f"11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
    for (cx, cy, rx, ry) in plan["ovais2d"]:
        pts = oval(cx, cy, rx, ry)
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            ents.append(f"0\nLINE\n8\n0\n10\n{x1:.2f}\n20\n{y1:.2f}\n30\n0.0\n"
                        f"11\n{x2:.2f}\n21\n{y2:.2f}\n31\n0.0\n")
    return "0\nSECTION\n2\nENTITIES\n" + "".join(ents) + "0\nENDSEC\n0\nEOF\n"


# ---------------------------------------------------------------- STL (3D)

def stl_caixa(f, x0, y0, x1, y1, z0, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 2, 1), (0, 3, 2),  # base (normal -z)
             (4, 5, 6), (4, 6, 7),  # topo
             (0, 1, 5), (0, 5, 4),  # frente
             (2, 3, 7), (2, 7, 6),  # trás
             (3, 0, 4), (3, 4, 7),  # esquerda
             (1, 2, 6), (1, 6, 5)]  # direita
    for (i, j, k) in faces:
        f.write("facet normal 0 0 0\nouter loop\n")
        for idx in (i, j, k):
            f.write("vertex %.2f %.2f %.2f\n" % v[idx])
        f.write("endloop\nendfacet\n")


def stl(plan, caminho):
    with open(caminho, "w") as f:
        f.write(f"solid {plan['nome']}\n")
        for c in paredes(plan["W"], plan["D"], ESPESSURA_PAREDE, plan["porta"], plan["H"]):
            stl_caixa(f, *c)
        for c in plan["caixas"]:
            stl_caixa(f, *c)
        f.write(f"endsolid {plan['nome']}\n")


# ---------------------------------------------------------------- Ruby (SketchUp)

RUBY_TOPO = """# %s — gerado a partir da planta cotada (unidades: cm, pé-direito %s cm)
# Como usar: SketchUp desktop > Janela > Console Ruby > cole tudo e Enter.
# Depois é só salvar o modelo como .skp.
model = Sketchup.active_model
model.start_operation("%s", true)

def caixa(ents, x0, y0, x1, y1, z0, z1)
  face = ents.add_face [x0.cm, y0.cm, z0.cm], [x1.cm, y0.cm, z0.cm],
                       [x1.cm, y1.cm, z0.cm], [x0.cm, y1.cm, z0.cm]
  face.reverse! if face.normal.z < 0
  face.pushpull((z1 - z0).cm)
end

"""


def ruby(plan):
    out = [RUBY_TOPO % (plan["nome"], ("%g" % plan["H"]), plan["nome"])]
    out.append('paredes = model.active_entities.add_group\nparedes.name = "Paredes"\n')
    for c in paredes(plan["W"], plan["D"], ESPESSURA_PAREDE, plan["porta"], plan["H"]):
        out.append("caixa(paredes.entities, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f)\n" % c)
    out.append('\nloucas = model.active_entities.add_group\nloucas.name = "Loucas e box"\n')
    for c in plan["caixas"]:
        out.append("caixa(loucas.entities, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f)\n" % c)
    out.append('\nmodel.commit_operation\nmodel.active_view.zoom_extents\n')
    return "".join(out)


# ---------------------------------------------------------------- preview PNG

def preview(plan, caminho):
    from PIL import Image, ImageDraw
    esc = 3
    T = ESPESSURA_PAREDE
    W, D = plan["W"], plan["D"]
    img = Image.new("RGB", (int((W + 2 * T + 40) * esc) // 1,
                            int((D + 2 * T + 40) * esc) // 1), "white")
    dr = ImageDraw.Draw(img)

    def pt(x, y):  # y invertido (imagem cresce para baixo)
        return ((x + T + 20) * esc, (D + T + 20 - y) * esc)

    def rect(x0, y0, x1, y1, cor="black", larg=2):
        dr.rectangle([pt(x0, y1), pt(x1, y0)], outline=cor, width=larg)

    rect(-T, -T, W + T, D + T, larg=3)
    a, w = plan["porta"]
    dr.line([pt(0, 0), pt(a, 0)], fill="black", width=3)
    dr.line([pt(a + w, 0), pt(W, 0)], fill="black", width=3)
    dr.line([pt(W, 0), pt(W, D)], fill="black", width=3)
    dr.line([pt(W, D), pt(0, D)], fill="black", width=3)
    dr.line([pt(0, D), pt(0, 0)], fill="black", width=3)
    for (x0, y0, x1, y1, _z0, z1) in plan["caixas"]:
        rect(x0, y0, x1, y1, cor="green" if z1 == H_VIDRO else "blue")
    for (cx, cy, rx, ry) in plan["ovais2d"]:
        dr.ellipse([pt(cx - rx, cy + ry), pt(cx + rx, cy - ry)], outline="red", width=2)
    img.save(caminho)


for plan in (P1, P2):
    base = os.path.join(OUT, plan["nome"])
    with open(base + ".dxf", "w") as f:
        f.write(dxf(plan))
    stl(plan, base + ".stl")
    with open(base + ".rb", "w") as f:
        f.write(ruby(plan))
    preview(plan, base + "_preview.png")
    print("gerado:", base + ".{dxf,stl,rb,_preview.png}")
