# Plantas de banheiro → SketchUp

Modelos gerados a partir das duas plantas cotadas (fotos enviadas em 04/08/2026).
Cotas originais em **centímetros**. Pé-direito: **253 cm** no banheiro de 282 e
**253,8 cm** no de 274.

## Os arquivos .skp (prontos)

Gerados pelo conector Trimble SketchUp, em geometria nativa. Baixe pelo link:

| Ambiente | Arquivo |
|---|---|
| Banheiro 282 × 176 × 253 | [banheiro_282x176_v2.skp](https://api.sketchup.com/mcp/v1/sketchup/dl/318c21b5-abd3-4b98-8601-f76c749bd874/009-save/banheiro_282x176_v2.skp?t=D-24WIWGn9urWz_8r3nyFw) |
| Banheiro 274 × 165 × 253,8 | [banheiro_274x165_v2.skp](https://api.sketchup.com/mcp/v1/sketchup/dl/318c21b5-abd3-4b98-8601-f76c749bd874/012-save/banheiro_274x165_v2.skp?t=VNsleutEKDa25Znz5Noxtw) |

Os links são temporários — baixe e guarde os arquivos. Ao abrir, troque a unidade
para centímetros em `Janela → Informações do modelo → Unidades`; o SketchUp
guarda tudo em polegadas internamente, mas as medidas reais estão corretas.

Cada modelo é um grupo (`Banheiro_...`) com as peças nomeadas dentro: `Piso`,
as quatro paredes, `Vaso_Bacia`, `Vaso_Caixa_Acoplada`, `Box_Vidro_Lateral`,
`Box_Vidro_Frontal`, mais `Coluna_Predio` + `Bancada` + `Cuba` (banheiro 1) ou
`Lavatorio` (banheiro 2). Todas as peças passam na validação de sólido do
SketchUp, então funcionam com as Ferramentas de Sólidos e com exportação
para CAD.

### Banheiro 282 × 176 — correção do Eduardo (04/08)

A primeira versão colocava a porta no meio da parede da frente. Está errado:
ali fica uma **coluna do prédio**, que se projeta para dentro do ambiente
2,5 cm na borda esquerda e 3,2 cm na direita (é o que as marcações amarelas do
desenho significam), ocupando os 76,7 cm entre 96,8 e 173,5 a partir da parede
esquerda. A parede da frente é inteira.

A porta fica na **parede direita** (oposta à do box), logo depois do vaso, com
**76 × 215 cm**: vão de y = 89 a y = 165 a partir da parede da frente, deixando
11 cm de parede até o fundo e a bancada nos 89 cm antes dela.

### Banheiro 274 × 165 — correção do Eduardo (04/08)

A marcação amarela **8,5** também é um recuo projetado para dentro do ambiente,
e na área da porta ele envolve o vão. A porta tem **78,8 × 214 cm** e fica
dentro do segmento de 90,1 da parede da frente, sobrando **11,3 cm** de parede.
Modelado como `Recuo_Lateral` (os 11,3 cm cheios, do piso ao teto),
`Recuo_Verga` (acima da porta) e `Recuo_Soleira` — três peças em vez de uma só,
para o recuo não invadir o vão. Quem passa pela porta atravessa
12,7 + 8,5 = 21,2 cm de espessura.

O que ainda não sei: até onde o recuo de 8,5 se estende para a direita. Modelei
só os 90,1 cm do segmento da porta. Se ele corre por mais trecho da parede da
frente, é só alongar a peça.

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

**Exato (das cotas e das correções do Eduardo):** dimensões internas e
pé-direito dos dois ambientes, porta do banheiro 1 (76 × 215, parede direita),
coluna do prédio (76,7 de largura, projeção 2,5 → 3,2 cm), porta do banheiro 2
(78,8 × 214, com recuo de 8,5 e sobra de 11,3 nos 90,1), box de banho (87 × 93
e 85,4 × 92), eixo do vaso (160 cm da parede direita na planta 1; 45,5 cm da
esquerda na planta 2) e bancada 48 × 89 da planta 1.

**Assumido:** espessura de parede **12,7 cm** (não estava cotada), soleira de
1,5 cm, vidro do box com 200 cm, bancada a 75 cm e lavatório a 85 cm do piso.

**Interpretação que vale conferir:**

- **Planta 2 — a sobra de 11,3 cm** foi colocada à esquerda da porta (junto ao
  canto). Se a porta é que encosta no canto e a sobra fica do outro lado, é só
  inverter.
- **Planta 2 — extensão do recuo de 8,5.** Modelado só nos 90,1 cm do segmento
  da porta; se ele continua pela parede da frente, precisa alongar.
- **Somatório das cotas da base.** Na planta 1 dá 277 contra 282 de largura
  total; na planta 2 dá 280,1 contra 274. Sobra/falta de 5–6 cm nos dois casos,
  provavelmente por causa de onde cada cota foi medida (face interna × externa).
- **Planta 2 — profundidade.** As laterais têm cotas diferentes (164,6 e 169,7)
  e o desenho mostra um recorte na parede direita. Modelei como retângulo de
  **165 cm**; se houver mesmo um degrau na parede, precisa entrar.
- **Planta 1 — bancada.** As cotas 48 e 89 foram lidas como profundidade e
  comprimento da bancada encostada na parede direita, ocupando o trecho antes
  da porta. No desenho a cuba aparece menor e mais ao centro do que isso.

O box de banho foi modelado com os dois vidros fechados (porta de correr
fechada), que é como o desenho mostra.

Gerador dos formatos alternativos: `gerar_plantas.py` — edite as medidas lá e
rode `python3 gerar_plantas.py` para regenerar.
