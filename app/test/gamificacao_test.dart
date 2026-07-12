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

  test('marcos do habito: comeca aos 20, consolida aos 40, fecha aos 60', () {
    Set<String> aos(int dias) => g
        .insignias(_arvore(), {}, dias)
        .where((i) => i.conquistada)
        .map((i) => i.id)
        .toSet();
    expect(aos(19), isNot(contains('habito-20')));
    expect(aos(20), contains('habito-20'));
    expect(aos(40), containsAll({'habito-20', 'habito-40'}));
    expect(aos(60), containsAll({'habito-20', 'habito-40', 'habito-60'}));
    expect(aos(365), containsAll({'constancia-180', 'constancia-365'}));
  });

  test('horas no relogio destravam as insignias de tempo', () {
    Set<String> com(double horas) => g
        .insignias(_arvore(), {}, 0, horas: horas)
        .where((i) => i.conquistada)
        .map((i) => i.id)
        .toSet();
    expect(com(9.9), isNot(contains('horas-10')));
    expect(com(120), containsAll({'horas-5', 'horas-10', 'horas-50', 'horas-100'}));
    expect(com(120), isNot(contains('horas-500')));
  });

  test('a escada da constancia nao tem buraco grande entre 180 e 365', () {
    final ids = g
        .insignias(_arvore(), {}, 0)
        .where((i) => i.categoria == 'Constância')
        .map((i) => i.id)
        .toSet();
    expect(
        ids,
        containsAll({
          'constancia-21', 'constancia-45', 'constancia-120',
          'constancia-210', 'constancia-240', 'constancia-270',
          'constancia-300', 'constancia-330', 'constancia-365',
        }));
    // aos 240 dias, tudo ate 240 conquistado; 270 ainda nao
    final aos240 = g
        .insignias(_arvore(), {}, 240)
        .where((i) => i.conquistada && i.categoria == 'Constância')
        .map((i) => i.id)
        .toSet();
    expect(aos240, contains('constancia-240'));
    expect(aos240, isNot(contains('constancia-270')));
  });

  test('pontos e materias tem escadas proprias', () {
    // edital sintetico completo = 1515 pontos, 2 materias
    final tudo = {'adm-1', 'adm-1-1', 'adm-2', 'amb-1'};
    final conquistadas = g
        .insignias(_arvore(), tudo, 0)
        .where((i) => i.conquistada)
        .map((i) => i.id)
        .toSet();
    expect(conquistadas, containsAll({'pontos-500', 'pontos-1000'}));
    expect(conquistadas, isNot(contains('pontos-2500')));
    expect(conquistadas, contains('materias-todas')); // as 2 de 2
    expect(conquistadas, isNot(contains('materias-3')));
  });

  test('toda insignia tem categoria', () {
    for (final insignia in g.insignias(_arvore(), {}, 0)) {
      expect(insignia.categoria, isNot('Geral'), reason: insignia.id);
    }
  });

  test('sessao no relogio mantem a sequencia sem marcar itens', () {
    final diario = {'2026-07-10': ['a']};
    expect(
        g.sequenciaDias(diario, DateTime(2026, 7, 11),
            diasExtras: {'2026-07-11'}),
        2);
  });
}
