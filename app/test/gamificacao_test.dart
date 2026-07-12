import 'package:editais_app/gamificacao.dart' as g;
import 'package:editais_app/modelos.dart';
import 'package:flutter_test/flutter_test.dart';

List<No> _arvore() => montarArvore([
      {'id': 'adm', 'parent_id': null, 'nivel': 'materia', 'titulo': 'ADM', 'ordem': 1},
      {'id': 'adm-1', 'parent_id': 'adm', 'nivel': 'topico', 'titulo': 'Estado', 'ordem': 1},
      {'id': 'adm-1-1', 'parent_id': 'adm-1', 'nivel': 'subtopico', 'titulo': 'Funções', 'ordem': 1},
      {'id': 'adm-2', 'parent_id': 'adm', 'nivel': 'topico', 'titulo': 'Atos', 'ordem': 2},
      {'id': 'amb', 'parent_id': null, 'nivel': 'materia', 'titulo': 'AMB', 'ordem': 2},
      {'id': 'amb-1', 'parent_id': 'amb', 'nivel': 'topico', 'titulo': 'Princípios', 'ordem': 1},
    ]);

void main() {
  group('pontos', () {
    test('zero sem progresso', () {
      expect(g.pontos(_arvore(), {}), 0);
    });

    test('no avulso vale 10; topico completo ganha bonus', () {
      // adm-1-1 sozinho: 10. adm-1 + adm-1-1: 20 + bonus 25 = 45.
      expect(g.pontos(_arvore(), {'adm-1-1'}), 10);
      expect(g.pontos(_arvore(), {'adm-1', 'adm-1-1'}), 45);
    });

    test('materia completa e edital completo somam bonus', () {
      // adm completa: 3 nos (30) + 2 topicos (50) + materia (200) = 280
      expect(g.pontos(_arvore(), {'adm-1', 'adm-1-1', 'adm-2'}), 280);
      // tudo: 280 + amb (10 + 25 + 200) + edital 1000 = 1515
      final tudo = {'adm-1', 'adm-1-1', 'adm-2', 'amb-1'};
      expect(g.pontos(_arvore(), tudo), 1515);
    });
  });

  test('percentual ignora os nos de materia', () {
    expect(g.percentual(_arvore(), {}), 0);
    expect(g.percentual(_arvore(), {'adm-1', 'adm-1-1'}), 0.5); // 2 de 4
    expect(g.percentualMateria(_arvore()[0], {'adm-1'}), closeTo(1 / 3, 0.001));
  });

  group('sequenciaDias', () {
    test('conta dias consecutivos ate hoje', () {
      final diario = {
        '2026-07-10': ['a'],
        '2026-07-11': ['b'],
        '2026-07-12': ['c'],
      };
      expect(g.sequenciaDias(diario, DateTime(2026, 7, 12)), 3);
    });

    test('sequencia viva: estudou ontem, hoje ainda nao', () {
      final diario = {'2026-07-10': ['a'], '2026-07-11': ['b']};
      expect(g.sequenciaDias(diario, DateTime(2026, 7, 12)), 2);
    });

    test('quebra de um dia zera', () {
      final diario = {'2026-07-08': ['a'], '2026-07-11': ['b']};
      expect(g.sequenciaDias(diario, DateTime(2026, 7, 13)), 0);
    });

    test('dia com lista vazia nao conta', () {
      expect(g.sequenciaDias({'2026-07-12': []}, DateTime(2026, 7, 12)), 0);
    });
  });

  test('insignias refletem progresso e constancia', () {
    final tudo = {'adm-1', 'adm-1-1', 'adm-2', 'amb-1'};
    final conquistadas = g
        .insignias(_arvore(), tudo, 7)
        .where((i) => i.conquistada)
        .map((i) => i.id)
        .toSet();
    expect(
        conquistadas,
        containsAll({
          'primeiro-passo', 'metade', 'edital-domado',
          'materia-completa', 'constancia-3', 'constancia-7',
        }));
    expect(conquistadas, isNot(contains('constancia-30')));
  });
}
