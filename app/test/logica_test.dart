import 'package:editais_app/ics.dart';
import 'package:editais_app/modelos.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('montarArvore', () {
    final nos = [
      {'id': 'adm', 'parent_id': null, 'nivel': 'materia', 'titulo': 'Direito Administrativo', 'ordem': 1},
      {'id': 'adm-21', 'parent_id': 'adm', 'nivel': 'topico', 'titulo': 'Responsabilidade civil', 'ordem': 21},
      {'id': 'adm-7', 'parent_id': 'adm', 'nivel': 'topico', 'titulo': 'Atos administrativos', 'ordem': 7},
      {'id': 'adm-7-5', 'parent_id': 'adm-7', 'nivel': 'subtopico', 'titulo': 'Vinculação', 'ordem': 5},
    ];

    test('aninha e ordena por ordem', () {
      final materias = montarArvore(nos);
      expect(materias, hasLength(1));
      final adm = materias.first;
      expect(adm.filhos.map((n) => n.id), ['adm-7', 'adm-21']);
      expect(adm.filhos.first.filhos.single.id, 'adm-7-5');
    });

    test('idsSubarvore cobre o no e os descendentes', () {
      final adm = montarArvore(nos).first;
      expect(adm.idsSubarvore.toSet(), {'adm', 'adm-7', 'adm-7-5', 'adm-21'});
      expect(adm.filhos.first.idsSubarvore.toSet(), {'adm-7', 'adm-7-5'});
    });
  });

  group('statusEvento', () {
    final hoje = DateTime(2026, 7, 10);

    test('encerrado, em andamento e futuro', () {
      expect(statusEvento({'inicio': '2026-04-13', 'fim': '2026-05-18'}, hoje),
          'encerrado');
      expect(statusEvento({'inicio': '2026-07-01', 'fim': '2026-07-20'}, hoje),
          'em andamento');
      expect(statusEvento({'inicio': '2026-07-10', 'fim': null}, hoje),
          'em andamento');
      expect(statusEvento({'inicio': '2026-09-05', 'fim': null}, hoje), 'futuro');
    });
  });

  group('gerarIcs', () {
    test('gera um VEVENT por evento, dia inteiro, DTEND exclusivo', () {
      final ics = gerarIcs([
        {'tipo': 'prova_objetiva', 'titulo': 'Prova objetiva', 'inicio': '2026-07-11', 'fim': null},
        {'tipo': 'inscricoes', 'titulo': 'Inscrições', 'inicio': '2026-04-13', 'fim': '2026-05-18'},
      ], 'PGE/AL');
      expect('BEGIN:VEVENT'.allMatches(ics), hasLength(2));
      expect(ics, contains('DTSTART;VALUE=DATE:20260711'));
      expect(ics, contains('DTEND;VALUE=DATE:20260712')); // exclusivo
      expect(ics, contains('DTEND;VALUE=DATE:20260519'));
      expect(ics, contains('SUMMARY:[PGE/AL] Prova objetiva'));
      expect(ics, startsWith('BEGIN:VCALENDAR'));
      expect(ics, endsWith('END:VCALENDAR'));
    });
  });
}
