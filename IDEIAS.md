# Banco de ideias — Eduardo + Claude

Registro de ideias de projetos levantadas nas conversas. Atualizado em **03/08/2026**.
Este arquivo é o lugar canônico para não perder ideia nenhuma — sempre que surgir uma nova, registrar aqui.

---

## 1. Radar de Teses Vinculantes ⭐ (favorita da sessão de 03/08/2026)

**Contexto:** o Combo Teses (Teses Vinculantes STF/STJ + Súmulas e OJs do TST) vende
regularmente pela Eduzz, e manter o material atualizado é trabalho manual recorrente.
Existe um projeto Supabase chamado "Teses Vinculantes STF e STJ" que foi pausado por
inatividade — a ideia já rondava.

**A ideia:** serviço que monitora STF, STJ e TST (informativos, repercussão geral,
repetitivos, IAC, súmulas novas/canceladas) e:
- detecta tese nova ou superada e avisa;
- gera automaticamente o **rascunho de atualização** do material (automatizar o gatilho
  do modo 4 da skill `revisao-material-juridico`);
- pode virar diferencial do produto: "atualização contínua" para quem compra.

Mesmo DNA do radar de retificações do app de Editais, apontado para os tribunais.
Reaproveita infraestrutura e conhecimento já construídos neste repo.

## 2. "Onde Guardei?" — inventário da casa (ideia do Eduardo, 03/08/2026)

**Dor real:** costume de esquecer onde guardou as coisas em casa.

**A ideia:** app/registro de onde está cada item, com mapeamento da casa:
- hierarquia de lugares: cômodo → móvel → gaveta/caixa/prateleira;
- busca instantânea ("onde está o carregador reserva?" → "Escritório > estante > caixa azul");
- registro rápido na hora de guardar (texto ou voz; foto opcional do item/lugar);
- possíveis extras: etiquetas QR nas caixas, foto do interior da gaveta com
  reconhecimento por IA, lista de empréstimos ("emprestei o livro X para Y").

**Avaliação inicial:** escopo pequeno, valor diário alto, ótimo candidato a projeto
rápido (PWA ou app Flutter simples com banco local + backup). O desafio não é técnico,
é de hábito — o app precisa tornar o registro mais rápido que a preguiça (voz ajuda).

## 3. App de dieta + treino + preços de alimentos (ideia antiga, espec. avançada)

**Status da busca (03/08/2026):** o Eduardo lembra de ter especificado essa ideia de
forma bem avançada com alguma IA, faltando só implementar. Procurado neste repositório
(nada), no Gmail (nada direto). **Não foi nesta base de trabalho.** Pistas:
- e-mails do Lovable insistindo "Your project hasn't moved" — pode ser que a espec.
  esteja em um projeto Lovable parado; conferir em lovable.dev;
- se foi em conversa do claude.ai, procurar no histórico de chats do site (esta sessão
  não tem acesso ao histórico de conversas).

**O que se sabe da ideia:** controle de treino + dieta, com registro de **preços de
alimentos** (planejamento de compra/custo da dieta) e afins. Quando a espec. original
for localizada, colar/resumir aqui.

## 4. Caça-apartamento inteligente

Agente que filtra os anúncios (QuintoAndar manda recomendações diárias) pelos critérios
reais: custo total (aluguel + condomínio + IPTU), distância dos pontos fixos (trabalho,
Tênis Clube Paulista), características (andar, vaga...), tempo de deslocamento — e
entrega só o que vale visita.

## 5. Cockpit financeiro pessoal

Painel que lê os e-mails de boletos/faturas (C6, QuintoAndar, clube...), monta o
calendário de vencimentos do mês e avisa do que está chegando; do outro lado, o resumo
das vendas Eduzz. Entradas e saídas em um lugar só.

## 6. Diário de leituras / "Direito & Clássicos"

Biblioteca pessoal, fila de leitura e notas (livros da Realpolitik, interesse em
clássicos/Ciclo Épico de Troia), com o capricho visual do app de Editais. Variante de
conteúdo: um cantinho público "Direito & Clássicos".

## 7. Flashcards das Teses (repetição espaçada)

Transformar o material de teses vinculantes em deck de flashcards com repetição
espaçada (Anki-like). **Importante (correção do Eduardo, 03/08/2026): isso pertence ao
aplicativo de Teses, NÃO ao app de Editais** — o app de Editais é gratuito; o modo
revisão é benefício de quem compra o material de teses, então fica dentro do produto
de Teses. Sinergia direta com a ideia 1 (Radar de Teses). Padrões de gamificação do
app de Editais (pontos, constância, insígnias) podem servir de referência técnica.
**Status: só anotar por enquanto — não implementar.**

## 8. Corretor de peças/discursivas para alunos

Ferramenta em que o aluno envia a peça ou resposta discursiva e recebe correção
estruturada (espelho, critérios de banca, apontamentos de estilo), com revisão final
do professor. Escala a correção sem perder o toque humano — human-in-the-loop, como o
painel de revisão dos editais.

---

**Convenção:** ao iniciar qualquer uma dessas ideias, criar repositório/pasta própria e
mover a espec. detalhada para lá, deixando aqui só o link e o status.
