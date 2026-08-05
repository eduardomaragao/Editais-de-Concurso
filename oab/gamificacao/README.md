# Gamificação do app de questões da OAB

Peça isolada, feita para ser **olhada primeiro e colada no app depois**. Não
depende de nada do app de editais — vive sozinha nesta pasta.

| arquivo | o que é |
| --- | --- |
| `preview.html` | a visualização (gerado — abra no navegador ou publique) |
| `preview.body.html` | a fonte da visualização (edite este) |
| `gamificacao_oab.dart` | o motor em Dart puro, sem Flutter, para entrar no app |
| `fontes.css` | Bodoni Moda + IBM Plex embutidas como data URI |
| `build.py` | junta `preview.body.html` + `fontes.css` → `preview.html` |
| `build_fontes.py` | rebaixa as fontes do Google Fonts e regera `fontes.css` |

```bash
python3 build.py        # depois de mexer no preview.body.html
```

## A ideia

O prêmio maior não é troféu genérico: é a **carteira vermelha**, montada peça
por peça. Cada peça cobra um tipo diferente de esforço, então não dá para chegar
ao fim só moendo questão nem só acertando pouco em muita matéria.

**146 insígnias em 7 categorias:**

| categoria | quantas | mede |
| --- | --- | --- |
| Carteira | 8 | a trilha principal — as peças da carteira |
| Volume | 30 | questões respondidas (10 → 25.000) |
| Acertos | 25 | acertos na vida toda (5 → 20.000) |
| Maratona | 12 | questões seguidas na mesma sessão (5 → 300) |
| Pontaria | 12 | acertos consecutivos sem erro (3 → 100) |
| Domínio | 51 | 17 matérias × 3 níveis |
| Ordem secreta | 8 | ocultas até caírem |

Os nomes saem todos do vocabulário do processo e da Ordem — *Petição Inicial*,
*Trânsito em Julgado*, *Sustentação Oral*, *Juramento* — em vez de "Nível 12".

### As 8 peças da carteira

| peça | insígnia | critério |
| --- | --- | --- |
| O couro | Autos Abertos | 1ª questão respondida |
| A moldura em ouro | Bacharel | 250 respondidas |
| A fotografia | Retrato nos Autos | 1.000 respondidas, 60% de acerto |
| O nome | Nome na Ordem | 3 matérias dominadas |
| O número | Número de Inscrição | 2.500 respondidas, 65% de acerto |
| A seccional | Seccional | 8 matérias dominadas |
| A assinatura | Juramento | 5.000 respondidas, 70%, maratona de 100 |
| O selo e o brasão | Carteira Vermelha | 17 matérias dominadas + 10.000 respondidas |

A trilha é **sequencial**: a peça 5 não entra antes da 4, mesmo que o critério
dela já esteja batido. A carteira monta na ordem, como uma carteira de verdade.

### Domínio de matéria — a meta sai do banco

A meta é uma fatia do banco daquela matéria, com piso e teto (para matéria
pequena não virar piada nem matéria gigante virar penitência):

| nível | fatia do banco | piso · teto | acerto |
| --- | --- | --- | --- |
| Domínio | 10% | 20 · 100 | 80% |
| Excelência | 20% | 40 · 180 | 85% |
| Cátedra | 35% | 70 · 300 | 90% |

Constitucional com 800 questões → Domínio com **80 respondidas e 64 acertos**,
exatamente como você descreveu. Cadastrou questão nova, a meta anda sozinha.

Duas decisões que valem revisão sua:

1. **Janela móvel.** O acerto é medido nas *últimas* `meta` questões daquela
   matéria, não na média da vida. Quem foi mal no começo não carrega o tropeço
   para sempre — basta voltar e fazer um bloco novo bem feito. Por isso o app
   precisa guardar as últimas 300 respostas por matéria (`janelaMaxima`).
2. **Catraca.** Como a janela pode piorar, o critério pode deixar de valer
   depois de valer — e insígnia conquistada não pode cair. O app grava
   `resultado.paraGuardar` e devolve em `permanentes` na chamada seguinte.

## Como plugar no app

```dart
final r = calcularOab(estatisticas, banco, permanentes: jaConquistadas);

r.pontos;                        // placar total
r.conquistadas;                  // insígnias que valem agora
r.daCategoria(CategoriaOab.volume);
r.pecasAbertas;                  // 0..8
r.ultimaPeca?.titulo;
r.proxima(CategoriaOab.acertos); // o "faltam N" da tela
jaConquistadas.addAll(r.paraGuardar);
```

Insígnia e ponto são **função do histórico**, recalculados do zero a cada
chamada — nunca acumulados. O placar não tem como divergir do estudo real, e
mudar uma regra reescreve o passado de todo mundo de forma consistente. (Mesmo
princípio do `gamificacao.dart` do app de editais.)

**Pontos:** acerto vale 10, erro vale 2 (esforço conta), e cada insígnia paga
por raridade — 60 / 180 / 500 / 1.400 / 3.500 por tier, dobrado nas peças da
carteira.

## O que ainda é decisão sua

- **Banco de questões de exemplo.** A tabela usa números plausíveis por matéria
  (900 de Ética, 800 de Constitucional…). Troque pelos reais — o cálculo já lê
  de `banco[id]`.
- **As 8 secretas** dependem de eventos que só o app observa (hora do dia,
  revisão de erro, simulado). No `preview.html` elas são aproximadas a partir
  dos números do simulador só para a página ficar viva; no app, quem dispara é
  o próprio app, mandando o id em `segredos`.
- **Glifos.** Os 12 desenhos (balança, coluna, livro, pena, martelo, selo,
  escudo, tocha, ampulheta, alvo, coroa, louros) estão como `<symbol>` no
  `preview.body.html`. Para o Flutter, viram SVG asset ou `CustomPainter`.
- **Carteira.** O cartão do preview é uma **insígnia de estudo** — não
  reproduz o documento nem a marca oficial da OAB, e traz microtexto dizendo
  isso. Mantenha essa distinção no app.

## Identidade visual

Oxblood da carteira `#7C1D2B` · ouro de folha `#C79A44` · papel de autos
`#F1ECE3` · couro escuro `#170709` (tema escuro). Bodoni Moda nos títulos
(cara de diploma gravado), IBM Plex Sans no corpo, IBM Plex Mono nos números.
Os medalhões escalam em cinco metais: bronze → prata → ouro → esmalte vinho →
ápice iridescente.
