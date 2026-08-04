# banheiro_274x165 — gerado a partir da planta cotada (unidades: cm, pé-direito 250 cm)
# Como usar: SketchUp desktop > Janela > Console Ruby > cole tudo e Enter.
# Depois é só salvar o modelo como .skp.
model = Sketchup.active_model
model.start_operation("banheiro_274x165", true)

def caixa(ents, x0, y0, x1, y1, z0, z1)
  face = ents.add_face [x0.cm, y0.cm, z0.cm], [x1.cm, y0.cm, z0.cm],
                       [x1.cm, y1.cm, z0.cm], [x0.cm, y1.cm, z0.cm]
  face.reverse! if face.normal.z < 0
  face.pushpull((z1 - z0).cm)
end

paredes = model.active_entities.add_group
paredes.name = "Paredes"
caixa(paredes.entities, -12.00, -12.00, 0.00, 177.00, 0.00, 250.00)
caixa(paredes.entities, 274.00, -12.00, 286.00, 177.00, 0.00, 250.00)
caixa(paredes.entities, 0.00, 165.00, 274.00, 177.00, 0.00, 250.00)
caixa(paredes.entities, 0.00, -12.00, 90.10, 0.00, 0.00, 250.00)
caixa(paredes.entities, 190.10, -12.00, 274.00, 0.00, 0.00, 250.00)

loucas = model.active_entities.add_group
loucas.name = "Loucas e box"
caixa(loucas.entities, 26.50, 97.00, 64.50, 165.00, 0.00, 42.00)
caixa(loucas.entities, 188.60, 0.00, 189.40, 92.00, 0.00, 200.00)
caixa(loucas.entities, 188.60, 91.20, 234.00, 92.00, 0.00, 200.00)
caixa(loucas.entities, 127.50, 10.00, 172.50, 45.00, 0.00, 85.00)

model.commit_operation
model.active_view.zoom_extents
