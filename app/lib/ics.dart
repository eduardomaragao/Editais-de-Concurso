/// Exportacao do cronograma para .ics (Google/Apple/Outlook).
library;

/// Gera o conteudo VCALENDAR com um VEVENT por evento do cronograma.
/// Eventos de dia inteiro; intervalo usa DTEND exclusivo (fim + 1 dia).
String gerarIcs(List<Map<String, dynamic>> eventos, String tituloEdital) {
  final linhas = <String>[
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//eduardoaragao.com//Editais//PT',
    'CALSCALE:GREGORIAN',
  ];
  for (final evento in eventos) {
    final inicio = evento['inicio'] as String?;
    if (inicio == null) continue;
    final titulo = (evento['titulo'] as String?) ?? (evento['tipo'] as String);
    final fim = evento['fim'] as String?;
    linhas.addAll([
      'BEGIN:VEVENT',
      'UID:${evento['tipo']}-$inicio@editais.eduardoaragao.com',
      'DTSTART;VALUE=DATE:${_data(inicio)}',
      'DTEND;VALUE=DATE:${_data(_diaSeguinte(fim ?? inicio))}',
      'SUMMARY:${_escapar('[$tituloEdital] $titulo')}',
      'END:VEVENT',
    ]);
  }
  linhas.add('END:VCALENDAR');
  return linhas.join('\r\n');
}

String _data(String iso) => iso.replaceAll('-', '');

String _diaSeguinte(String iso) {
  final data = DateTime.parse(iso).add(const Duration(days: 1));
  return '${data.year.toString().padLeft(4, '0')}-'
      '${data.month.toString().padLeft(2, '0')}-'
      '${data.day.toString().padLeft(2, '0')}';
}

String _escapar(String texto) =>
    texto.replaceAll('\\', '\\\\').replaceAll(';', '\\;').replaceAll(',', '\\,');

/// Status de um evento em relacao a hoje: encerrado, em andamento ou futuro.
String statusEvento(Map<String, dynamic> evento, DateTime hoje) {
  final inicio = DateTime.parse(evento['inicio'] as String);
  final fim = evento['fim'] != null ? DateTime.parse(evento['fim'] as String) : inicio;
  final dia = DateTime(hoje.year, hoje.month, hoje.day);
  if (dia.isAfter(fim)) return 'encerrado';
  if (dia.isBefore(inicio)) return 'futuro';
  return 'em andamento';
}
