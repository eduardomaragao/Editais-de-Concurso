import 'package:editais_app/tempo.dart' as tempo;
import 'package:flutter_test/flutter_test.dart';

void main() {
  // hoje = sabado 2026-07-11; semana comeca na segunda 2026-07-06
  final hoje = DateTime(2026, 7, 11);
  final sessoes = <String, Map<String, int>>{
    '2026-07-11': {'adm': 3600, 'geral': 1800}, // hoje: 1h30
    '2026-07-06': {'civ': 7200}, // segunda desta semana: 2h
    '2026-07-05': {'adm': 600}, // domingo passado: fora da semana
    '2026-06-20': {'adm': 3600}, // mes passado
    '2025-12-31': {'adm': 3600}, // ano passado
  };

  test('hoje, semana, mes, ano e total', () {
    expect(tempo.segundosHoje(sessoes, hoje), 5400);
    expect(tempo.segundosNaSemana(sessoes, hoje), 5400 + 7200);
    expect(tempo.segundosNoMes(sessoes, hoje), 5400 + 7200 + 600);
    expect(tempo.segundosNoAno(sessoes, hoje), 5400 + 7200 + 600 + 3600);
    expect(tempo.segundosTotais(sessoes), 5400 + 7200 + 600 + 3600 + 3600);
  });

  test('por materia num periodo', () {
    final semana = tempo.segundosPorMateria(sessoes,
        de: DateTime(2026, 7, 6), ate: hoje);
    expect(semana, {'adm': 3600, 'geral': 1800, 'civ': 7200});
  });

  test('dias com sessao alimentam a constancia', () {
    expect(tempo.diasComSessao(sessoes), contains('2026-07-11'));
    expect(tempo.diasComSessao({'2026-07-11': {}}), isEmpty);
  });

  test('formatacao', () {
    expect(tempo.formatarDuracao(45), '45s');
    expect(tempo.formatarDuracao(1800), '30min');
    expect(tempo.formatarDuracao(5400), '1h 30min');
    expect(tempo.formatarCronometro(75), '01:15');
    expect(tempo.formatarCronometro(3675), '1:01:15');
  });
}
