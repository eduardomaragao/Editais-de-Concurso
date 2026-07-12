/// Metricas do relogio de estudo. As sessoes vivem agregadas por dia e
/// materia: {"2026-07-12": {"adm": 3600, "geral": 600}}.
library;

import 'armazenamento.dart' show chaveDoDia;

typedef Sessoes = Map<String, Map<String, int>>;

int _totalDoDia(Map<String, int> materias) =>
    materias.values.fold(0, (soma, s) => soma + s);

int segundosEntre(Sessoes sessoes, DateTime de, DateTime ate) {
  final chaveDe = chaveDoDia(de);
  final chaveAte = chaveDoDia(ate);
  var total = 0;
  sessoes.forEach((dia, materias) {
    if (dia.compareTo(chaveDe) >= 0 && dia.compareTo(chaveAte) <= 0) {
      total += _totalDoDia(materias);
    }
  });
  return total;
}

int segundosHoje(Sessoes sessoes, DateTime hoje) =>
    segundosEntre(sessoes, hoje, hoje);

/// Semana corrente, comecando na segunda-feira.
int segundosNaSemana(Sessoes sessoes, DateTime hoje) {
  final segunda = hoje.subtract(Duration(days: hoje.weekday - 1));
  return segundosEntre(sessoes, segunda, hoje);
}

int segundosNoMes(Sessoes sessoes, DateTime hoje) =>
    segundosEntre(sessoes, DateTime(hoje.year, hoje.month, 1), hoje);

int segundosNoAno(Sessoes sessoes, DateTime hoje) =>
    segundosEntre(sessoes, DateTime(hoje.year, 1, 1), hoje);

int segundosTotais(Sessoes sessoes) =>
    sessoes.values.fold(0, (soma, materias) => soma + _totalDoDia(materias));

double horasTotais(Sessoes sessoes) => segundosTotais(sessoes) / 3600;

/// Soma por materia num periodo (para o "top materias" do card).
Map<String, int> segundosPorMateria(Sessoes sessoes,
    {DateTime? de, DateTime? ate}) {
  final chaveDe = de != null ? chaveDoDia(de) : null;
  final chaveAte = ate != null ? chaveDoDia(ate) : null;
  final total = <String, int>{};
  sessoes.forEach((dia, materias) {
    if (chaveDe != null && dia.compareTo(chaveDe) < 0) return;
    if (chaveAte != null && dia.compareTo(chaveAte) > 0) return;
    materias.forEach((materia, segundos) {
      total[materia] = (total[materia] ?? 0) + segundos;
    });
  });
  return total;
}

/// Dias em que houve estudo cronometrado (alimenta a constancia).
Set<String> diasComSessao(Sessoes sessoes) => {
      for (final entrada in sessoes.entries)
        if (_totalDoDia(entrada.value) > 0) entrada.key,
    };

String formatarDuracao(int segundos) {
  final horas = segundos ~/ 3600;
  final minutos = (segundos % 3600) ~/ 60;
  if (horas == 0 && minutos == 0) return '${segundos % 60}s';
  if (horas == 0) return '${minutos}min';
  return '${horas}h ${minutos.toString().padLeft(2, '0')}min';
}

String formatarCronometro(int segundos) {
  final horas = segundos ~/ 3600;
  final minutos = ((segundos % 3600) ~/ 60).toString().padLeft(2, '0');
  final resto = (segundos % 60).toString().padLeft(2, '0');
  return horas > 0 ? '$horas:$minutos:$resto' : '$minutos:$resto';
}
