# Plantas de banheiro → SketchUp (.skp)

Modelos gerados a partir das duas plantas cotadas (fotos enviadas em 04/08/2026).
Unidades em **centímetros**, pé-direito de **250 cm**.

O formato `.skp` é proprietário da Trimble e não pode ser gerado diretamente por
ferramenta externa — mas qualquer um dos arquivos abaixo vira `.skp` com um
clique dentro do próprio SketchUp:

## Como obter o .skp

**Opção A — SketchUp Free (web, gratuito):** em [app.sketchup.com](https://app.sketchup.com),
crie um modelo novo → ícone de pasta → **Insert** → escolha o `.stl` → salve.
O arquivo salvo já é um `.skp` (dá para baixar em Download → SKP).

**Opção B — SketchUp desktop (Pro/Go):** `Janela → Console Ruby`, cole o
conteúdo do arquivo `.rb` correspondente e dê Enter. O modelo é desenhado em
geometria nativa (grupos "Paredes" e "Loucas e box") — salve como `.skp`.
É a opção que gera o modelo mais limpo e editável.

**Opção C — importar a planta 2D:** `Arquivo → Importar` → `.dxf`
(unidade: centímetros). Vem só o traçado 2D, para você mesmo levantar as paredes.

## Arquivos

| Ambiente | 2D | 3D (p/ web) | Script nativo |
|---|---|---|---|
| Banheiro 282 × 176 | `banheiro_282x176.dxf` | `banheiro_282x176.stl` | `banheiro_282x176.rb` |
| Banheiro 274 × 165 | `banheiro_274x165.dxf` | `banheiro_274x165.stl` | `banheiro_274x165.rb` |

Os `_preview.png` mostram a conferência do traçado (verde = vidro do box,
azul = louças/bancada).

## O que foi modelado e o que é aproximado

- **Exatos (das cotas):** dimensões internas dos ambientes, vão da porta
  (76,7 cm na planta 1; 100 cm na planta 2), box de banho (87×93 e 85,4×92),
  posição do vaso (cota 160 / 45,5) e bancada 48×89 da planta 1.
- **Assumidos:** espessura de parede **12 cm** (não estava cotada; as marcações
  amarelas 2,5 / 3,2 / 8,5 parecem ser outra coisa — confirmar), vão da porta
  sem verga (vai até o teto — corte a 210 cm no SketchUp se quiser),
  vidro do box com 200 cm de altura.
- **Aproximados (ajustar no SketchUp):** posição exata do lavatório oval da
  planta 2 (a cota 45 dá a largura, não a posição — no desenho ele fica em
  frente ao vão da porta), altura/profundidade das louças, aberturas dos boxes.
- Na planta 2 as laterais têm cotas diferentes (164,6 e 169,7); foi adotado
  **165** de profundidade — conferir se o ambiente é mesmo retangular.

Gerador: `gerar_plantas.py` (nesta pasta) — edite as medidas lá e rode
`python3 gerar_plantas.py` para regenerar tudo.
