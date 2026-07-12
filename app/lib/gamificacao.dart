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
  const Insignia(this.id, this.emoji, this.titulo, this.descricao, this.conquistada);
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

List<Insignia> insignias(List<No> materias, Set<String> concluidos,
    int sequencia, {double horas = 0}) {
  final pct = percentual(materias, concluidos);
  final completas = materiasCompletas(materias, concluidos);
  return [
    // --- progresso no edital ---
    Insignia('primeiro-passo', '🌱', 'Primeiro passo',
        'Concluiu o primeiro item do edital', concluidos.isNotEmpty),
    Insignia('ritmo', '🔥', 'Pegando ritmo', '10% do edital', pct >= 0.10),
    Insignia('um-quarto', '🥉', 'Um quarto vencido', '25% do edital', pct >= 0.25),
    Insignia('metade', '🥈', 'Metade do caminho', '50% do edital', pct >= 0.50),
    Insignia('reta-final', '🥇', 'Reta final', '75% do edital', pct >= 0.75),
    Insignia('edital-domado', '🏆', 'Edital domado', '100% do edital', pct >= 1.0),
    Insignia('materia-completa', '📗', 'Matéria completa',
        'Fechou uma matéria inteira ($completas até agora)', completas >= 1),
    // --- constancia (dias seguidos) ---
    Insignia('constancia-3', '⚡', 'Constância 3', '3 dias seguidos de estudo',
        sequencia >= 3),
    Insignia('constancia-7', '💪', 'Constância 7', '7 dias seguidos de estudo',
        sequencia >= 7),
    Insignia('constancia-14', '🚀', 'Constância 14',
        '14 dias seguidos de estudo', sequencia >= 14),
    Insignia('constancia-30', '🛡️', 'Constância 30',
        '30 dias seguidos de estudo', sequencia >= 30),
    Insignia('constancia-90', '🏔️', 'Constância 90',
        '90 dias seguidos de estudo', sequencia >= 90),
    Insignia('constancia-180', '🌗', 'Constância 180',
        'Meio ano de estudo sem falhar um dia', sequencia >= 180),
    Insignia('constancia-365', '🌟', 'Constância 365',
        'Um ano inteiro, todos os dias', sequencia >= 365),
    // --- criacao do habito (20 -> 40 -> 60 dias) ---
    Insignia('habito-20', '🌿', 'Criando o hábito',
        '20 dias seguidos — a criação do hábito começou', sequencia >= 20),
    Insignia('habito-40', '🌳', 'Hábito em consolidação',
        '40 dias seguidos — está virando parte de você', sequencia >= 40),
    Insignia('habito-60', '💎', 'Hábito criado',
        '60 dias seguidos — estudar agora é rotina', sequencia >= 60),
    // --- horas no relogio de estudo ---
    Insignia('horas-10', '⏱️', '10 horas no relógio',
        '10 horas de estudo cronometradas', horas >= 10),
    Insignia('horas-100', '⏳', '100 horas no relógio',
        '100 horas de estudo cronometradas', horas >= 100),
    Insignia('horas-500', '🕰️', '500 horas no relógio',
        'Meio milhar de horas de estudo', horas >= 500),
  ];
}
