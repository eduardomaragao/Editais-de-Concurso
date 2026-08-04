# banheiro_282x176 — gerado a partir da planta cotada (unidades: cm, pé-direito 253 cm)
# Como usar: SketchUp desktop > Janela > Console Ruby > cole tudo e Enter.
# Depois é só salvar o modelo como .skp.
model = Sketchup.active_model
model.start_operation("banheiro_282x176", true)

def caixa(ents, x0, y0, x1, y1, z0, z1)
  face = ents.add_face [x0.cm, y0.cm, z0.cm], [x1.cm, y0.cm, z0.cm],
                       [x1.cm, y1.cm, z0.cm], [x0.cm, y1.cm, z0.cm]
  face.reverse! if face.normal.z < 0
  face.pushpull((z1 - z0).cm)
end

paredes = model.active_entities.add_group
paredes.name = "Paredes"
caixa(paredes.entities, -12.00, -12.00, 0.00, 188.00, 0.00, 253.00)
caixa(paredes.entities, 282.00, -12.00, 294.00, 188.00, 0.00, 253.00)
caixa(paredes.entities, 0.00, 176.00, 282.00, 188.00, 0.00, 253.00)
caixa(paredes.entities, 0.00, -12.00, 96.80, 0.00, 0.00, 253.00)
caixa(paredes.entities, 173.50, -12.00, 282.00, 0.00, 0.00, 253.00)

loucas = model.active_entities.add_group
loucas.name = "Loucas e box"
caixa(loucas.entities, 86.20, 83.00, 87.00, 176.00, 0.00, 200.00)
caixa(loucas.entities, 0.00, 83.00, 40.00, 83.80, 0.00, 200.00)
caixa(loucas.entities, 103.00, 108.00, 141.00, 176.00, 0.00, 42.00)
caixa(loucas.entities, 234.00, 0.00, 282.00, 89.00, 0.00, 75.00)
caixa(loucas.entities, 240.00, 25.00, 276.00, 61.00, 75.00, 90.00)

model.commit_operation
model.active_view.zoom_extents
