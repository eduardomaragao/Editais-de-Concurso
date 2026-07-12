/// Motor de gamificacao. Pontos e insignias sao FUNCAO PURA do progresso
/// atual + diario de estudo — recalculados sempre, nunca acumulados, entao
/// nao ha como o placar divergir do estudo real.
library;

import 'modelos.dart';

const pontosPorNo = 10;
const bonusTopicoCompleto = 25;
const bonusMateriaCompleta = 200;
const bonusEditalCompleto = 1000;

class Insignia {
  final String id;
  final String emoji;
  final String titulo;
  final String descricao;
  final bool conquistada;
  final String categoria;
  const Insignia(this.id, this.emoji, this.titulo, this.descricao,
      this.conquistada, {this.categoria = 'Geral'});
}

int pontos(List<No> materias, Set<String> concluidos) {
  var total = 0;
  var editalCompleto = true;
  for (final materia in materias) {
    var materiaCompleta = true;
    for (final topico in materia.filhos) {
      final ids = topico.idsSubarvore.toList();
      final feitos = ids.where(concluidos.contains).length;
      total += feitos * pontosPorNo;
      if (feitos == ids.length) {
        total += bonusTopicoCompleto;
      } else {
        materiaCompleta = false;
      }
    }
    if (materia.filhos.isEmpty) materiaCompleta = false;
    if (materiaCompleta) {
      total += bonusMateriaCompleta;
    } else {
      editalCompleto = false;
    }
  }
  if (materias.isNotEmpty && editalCompleto) total += bonusEditalCompleto;
  return total;
}

double percentual(List<No> materias, Set<String> concluidos) {
  var total = 0;
  var feitos = 0;
  for (final materia in materias) {
    for (final id in materia.idsSubarvore.skip(1)) {
      total++;
      if (concluidos.contains(id)) feitos++;
    }
  }
  return total == 0 ? 0 : feitos / total;
}

double percentualMateria(No materia, Set<String> concluidos) {
  final ids = materia.idsSubarvore.skip(1).toList();
  if (ids.isEmpty) return 0;
  return ids.where(concluidos.contains).length / ids.length;
}

int materiasCompletas(List<No> materias, Set<String> concluidos) => materias
    .where((m) =>
        m.filhos.isNotEmpty && percentualMateria(m, concluidos) >= 1.0)
    .length;

/// Sequencia de dias consecutivos com estudo (itens marcados OU sessao no
/// relogio — `diasExtras`), terminando hoje ou ontem (estudou ontem e ainda
/// nao hoje = sequencia viva).
int sequenciaDias(Map<String, List<String>> diario, DateTime hoje,
    {Set<String> diasExtras = const {}}) {
  final diasComEstudo = {
    ...diario.entries.where((e) => e.value.isNotEmpty).map((e) => e.key),
    ...diasExtras,
  }.map(DateTime.parse).toSet();
  var dia = DateTime(hoje.year, hoje.month, hoje.day);
  if (!diasComEstudo.contains(dia)) {
    dia = dia.subtract(const Duration(days: 1)); // sequencia viva de ontem
  }
  var sequencia = 0;
  while (diasComEstudo.contains(dia)) {
    sequencia++;
    dia = dia.subtract(const Duration(days: 1));
  }
  return sequencia;
}

// Escadas de conquista: (marco, emoji, apelido opcional).
const _escadaConstancia = [
  (3, '⚡', 'Faísca'),
  (7, '💪', 'Uma semana'),
  (14, '🚀', 'Duas semanas'),
  (21, '🎯', 'Três semanas'),
  (30, '🛡️', 'Um mês'),
  (45, '🏹', 'Mês e meio'),
  (75, '🧗', 'Escalando'),
  (90, '🏔️', 'Um trimestre'),
  (120, '🦅', 'Quatro meses'),
  (150, '🗿', 'Inabalável'),
  (180, '🌗', 'Meio ano'),
  (210, '🌔', 'Sete meses'),
  (240, '🌕', 'Oito meses'),
  (270, '☀️', 'Nove meses'),
  (300, '🌠', 'Trezentos'),
  (330, '🌌', 'Onze meses'),
  (365, '🌟', 'Um ano inteiro'),
];

const _escadaHoras = [
  (5, '⏱️', null),
  (10, '⏲️', null),
  (25, '⌛', null),
  (50, '⏳', null),
  (100, '🕰️', null),
  (200, '📚', null),
  (300, '🧠', null),
  (500, '🎖️', null),
  (750, '🏅', null),
  (1000, '🏛️', 'Mil horas!'),
];

const _escadaPontos = [
  (500, '🔸', null),
  (1000, '🔶', null),
  (2500, '💠', null),
  (5000, '🏵️', null),
  (10000, '🎇', null),
  (15000, '👑', 'Placar de rei'),
];

List<Insignia> insignias(List<No> materias, Set<String> concluidos,
    int sequencia, {double horas = 0}) {
  final pct = percentual(materias, concluidos);
  final completas = materiasCompletas(materias, concluidos);
  final totalMaterias = materias.length;
  final pontuacao = pontos(materias, concluidos);

  return [
    // --- progresso no edital ---
    Insignia('primeiro-passo', '🌱', 'Primeiro passo',
        'Concluiu o primeiro item do edital', concluidos.isNotEmpty,
        categoria: 'Progresso'),
    Insignia('ritmo', '🔥', 'Pegando ritmo', '10% do edital', pct >= 0.10,
        categoria: 'Progresso'),
    Insignia('um-quarto', '🥉', 'Um quarto vencido', '25% do edital',
        pct >= 0.25, categoria: 'Progresso'),
    Insignia('metade', '🥈', 'Metade do caminho', '50% do edital', pct >= 0.50,
        categoria: 'Progresso'),
    Insignia('reta-final', '🥇', 'Reta final', '75% do edital', pct >= 0.75,
        categoria: 'Progresso'),
    Insignia('edital-domado', '🏆', 'Edital domado', '100% do edital',
        pct >= 1.0, categoria: 'Progresso'),

    // --- materias fechadas ---
    Insignia('materia-completa', '📗', 'Matéria completa',
        'Fechou uma matéria inteira ($completas até agora)', completas >= 1,
        categoria: 'Matérias'),
    Insignia('materias-3', '📚', 'Trio fechado', '3 matérias completas',
        completas >= 3, categoria: 'Matérias'),
    Insignia('materias-5', '🎓', 'Meia banca', '5 matérias completas',
        completas >= 5, categoria: 'Matérias'),
    Insignia('materias-todas', '🧑‍⚖️', 'Todas as matérias',
        'Fechou as $totalMaterias matérias do edital',
        totalMaterias > 0 && completas >= totalMaterias,
        categoria: 'Matérias'),

    // --- constancia (dias seguidos) ---
    for (final (dias, emoji, apelido) in _escadaConstancia)
      Insignia('constancia-$dias', emoji, 'Constância $dias — $apelido',
          '$dias dias seguidos de estudo', sequencia >= dias,
          categoria: 'Constância'),

    // --- criacao do habito (20 -> 40 -> 60 dias) ---
    Insignia('habito-20', '🌿', 'Criando o hábito',
        '20 dias seguidos — a criação do hábito começou', sequencia >= 20,
        categoria: 'Hábito'),
    Insignia('habito-40', '🌳', 'Hábito em consolidação',
        '40 dias seguidos — está virando parte de você', sequencia >= 40,
        categoria: 'Hábito'),
    Insignia('habito-60', '💎', 'Hábito criado',
        '60 dias seguidos — estudar agora é rotina', sequencia >= 60,
        categoria: 'Hábito'),

    // --- horas no relogio de estudo ---
    for (final (h, emoji, apelido) in _escadaHoras)
      Insignia('horas-$h', emoji,
          apelido ?? '$h horas no relógio',
          '$h horas de estudo cronometradas', horas >= h,
          categoria: 'Horas de estudo'),

    // --- pontos ---
    for (final (p, emoji, apelido) in _escadaPontos)
      Insignia('pontos-$p', emoji, apelido ?? '$p pontos',
          'Alcançou $p pontos', pontuacao >= p,
          categoria: 'Pontos'),
  ];
}
