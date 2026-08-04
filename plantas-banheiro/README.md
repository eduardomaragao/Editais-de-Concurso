# Plantas de banheiro → SketchUp

Modelos gerados a partir das duas plantas cotadas (fotos enviadas em 04/08/2026).
Cotas originais em **centímetros**. Pé-direito: **253 cm** no banheiro de 282 e
**253,8 cm** no de 274.

## Os arquivos .skp (prontos)

Gerados pelo conector Trimble SketchUp, em geometria nativa. Baixe pelo link:

| Ambiente | Arquivo |
|---|---|
| Banheiro 282 × 176 × 253 | [banheiro_282x176.skp](https://api.sketchup.com/mcp/v1/sketchup/dl/318c21b5-abd3-4b98-8601-f76c749bd874/003-save/banheiro_282x176.skp?t=oAUdOgsV6I7HIPLob4se1Q) |
| Banheiro 274 × 165 × 253,8 | [banheiro_274x165.skp](https://api.sketchup.com/mcp/v1/sketchup/dl/318c21b5-abd3-4b98-8601-f76c749bd874/006-save/banheiro_274x165.skp?t=Nkhx8yLz1wkYo_UjnUpskQ) |

Os links são temporários — baixe e guarde os arquivos. Ao abrir, troque a unidade
para centímetros em `Janela → Informações do modelo → Unidades`; o SketchUp
guarda tudo em polegadas internamente, mas as medidas reais estão corretas.

Cada modelo é um grupo (`Banheiro_...`) com as peças nomeadas dentro:
`Piso`, `Parede_Frente` (com o vão da porta recortado), `Parede_Fundo`,
`Parede_Esquerda`, `Parede_Direita`, `Vaso_Bacia`, `Vaso_Caixa_Acoplada`,
`Box_Vidro_Lateral`, `Box_Vidro_Frontal`, `Bancada`/`Cuba` ou `Lavatorio`.
Todas as peças passam na validação de sólido do SketchUp, então funcionam com as
Ferramentas de Sólidos e com exportação para CAD.

## Formatos alternativos (mesma geometria, gerados localmente)

Ficam nesta pasta e servem se você quiser reconstruir ou editar fora do SketchUp:

| Ambiente | 2D | 3D | Script nativo |
|---|---|---|---|
| Banheiro 282 × 176 | `banheiro_282x176.dxf` | `banheiro_282x176.stl` | `banheiro_282x176.rb` |
| Banheiro 274 × 165 | `banheiro_274x165.dxf` | `banheiro_274x165.stl` | `banheiro_274x165.rb` |

O `.rb` roda no Console Ruby do SketchUp desktop; o `.stl` importa no SketchUp
Free (web); o `.dxf` traz só o traçado 2D. Os `_preview.png` mostram a
conferência do traçado.

## O que é exato e o que é interpretação

**Exato (direto das cotas):** dimensões internas e pé-direito dos dois ambientes,
vão da porta (76,7 cm na planta 1; 90,1 cm na planta 2), box de banho (87 × 93 e
85,4 × 92), eixo do vaso (160 cm da parede direita na planta 1; 45,5 cm da
esquerda na planta 2) e bancada 48 × 89 da planta 1.

**Assumido:** espessura de parede **12,7 cm** (não estava cotada), porta com
210 cm de altura e soleira de 1,5 cm, vidro do box com 200 cm, bancada a 75 cm e
lavatório a 85 cm do piso.

**Interpretação que vale conferir:**

- **Planta 2 — posição da porta.** As cotas da base (90,1 / 100 / 90) não dizem
  qual segmento é a porta. Adotei o **segmento da esquerda (90,1)**, porque o do
  meio é onde está desenhado o lavatório e o da direita (90) bate com a largura
  do box (85,4). Se a porta for na verdade o vão de 100 cm no meio, é uma linha
  para corrigir.
- **Somatório das cotas da base.** Na planta 1 dá 277 contra 282 de largura
  total; na planta 2 dá 280,1 contra 274. Sobra/falta de 5–6 cm nos dois casos,
  provavelmente por causa de onde cada cota foi medida (face interna × externa).
- **Planta 2 — profundidade.** As laterais têm cotas diferentes (164,6 e 169,7)
  e o desenho mostra um recorte na parede direita. Modelei como retângulo de
  **165 cm**; se houver mesmo um degrau na parede, precisa entrar.
- **Planta 1 — bancada.** As cotas 48 e 89 foram lidas como profundidade e
  comprimento da bancada encostada na parede direita. No desenho a cuba aparece
  menor e mais ao centro do que isso.
- **Marcações amarelas** (2,5 / 3,2 na planta 1; 8,5 na planta 2) não foram
  modeladas — não deu para identificar o que são (desnível? espessura?).

O box de banho foi modelado com os dois vidros fechados (porta de correr
fechada), que é como o desenho mostra.

Gerador dos formatos alternativos: `gerar_plantas.py` — edite as medidas lá e
rode `python3 gerar_plantas.py` para regenerar.
