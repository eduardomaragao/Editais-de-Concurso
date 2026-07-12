import 'package:editais_app/modelos.dart';
import 'package:editais_app/telas/conteudo.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

Edital _edital() => Edital({
      'edital': {'orgao': 'PGE/AL', 'cargo': 'X', 'banca': 'C', 'numero': '1/2026'},
      'cronograma': [],
      'conteudo': [
        for (var m = 1; m <= 6; m++) ...[
          {
            'id': 'm$m',
            'parent_id': null,
            'nivel': 'materia',
            'titulo': 'DIREITO MATÉRIA $m',
            'ordem': m,
          },
          {
            'id': 'm$m-1',
            'parent_id': 'm$m',
            'nivel': 'topico',
            'titulo': 'Tópico',
            'ordem': 1,
          },
        ],
      ],
    });

Future<void> _bombear(WidgetTester tester, Size tamanho) async {
  tester.view.physicalSize = tamanho;
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
  SharedPreferences.setMockInitialValues({});
  await tester.pumpWidget(MaterialApp(
      home: ConteudoPage(slug: 'teste', edital: _edital())));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('celular: 2 colunas de quadros proporcionais', (tester) async {
    await _bombear(tester, const Size(380, 800));
    final cards = find.byType(Card);
    expect(cards, findsNWidgets(6));
    final larguras = [for (final c in cards.evaluate()) tester.getSize(find.byWidget(c.widget)).width];
    expect(larguras.first, lessThan(200));
    // 2 colunas: dois X distintos
    final xs = {
      for (final c in cards.evaluate())
        tester.getTopLeft(find.byWidget(c.widget)).dx.round()
    };
    expect(xs.length, 2);
  });

  testWidgets('desktop: quadros continuam pequenos, mais colunas', (tester) async {
    await _bombear(tester, const Size(1280, 800));
    final cards = find.byType(Card);
    final larguras = [for (final c in cards.evaluate()) tester.getSize(find.byWidget(c.widget)).width];
    // nunca quadros gigantes: cada um abaixo de 200px mesmo em tela larga
    expect(larguras.every((l) => l < 200), isTrue, reason: '$larguras');
    final xs = {
      for (final c in cards.evaluate())
        tester.getTopLeft(find.byWidget(c.widget)).dx.round()
    };
    expect(xs.length, greaterThanOrEqualTo(4)); // 4+ colunas no desktop
  });
}
