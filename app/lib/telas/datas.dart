import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../ics.dart';
import '../modelos.dart';
import '../tema.dart';

class DatasPage extends StatelessWidget {
  final Edital edital;
  const DatasPage({super.key, required this.edital});

  @override
  Widget build(BuildContext context) {
    final hoje = DateTime.now();
    final eventos = edital.cronograma;
    return Scaffold(
      appBar: AppBar(title: const Text('Datas')),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          Card(
            child: ListTile(
              leading: const Icon(Icons.calendar_month, color: verde),
              title: const Text('Adicionar à agenda'),
              subtitle:
                  const Text('Copia o cronograma em formato .ics (Google/Apple/Outlook)'),
              trailing: const Icon(Icons.copy),
              onTap: () async {
                final ics = gerarIcs(eventos, edital.orgao);
                await Clipboard.setData(ClipboardData(text: ics));
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                      content: Text(
                          'Cronograma .ics copiado — cole num arquivo .ics e importe na agenda.')));
                }
              },
            ),
          ),
          const SizedBox(height: 8),
          for (final evento in eventos) _linhaEvento(context, evento, hoje),
        ],
      ),
    );
  }

  Widget _linhaEvento(
      BuildContext context, Map<String, dynamic> evento, DateTime hoje) {
    final status = statusEvento(evento, hoje);
    final (cor, icone) = switch (status) {
      'encerrado' => (const Color(0xFF8A8574), Icons.check_circle_outline),
      'em andamento' => (dourado, Icons.play_circle_outline),
      _ => (verde, Icons.schedule),
    };
    final periodo = evento['fim'] != null
        ? '${_dataBr(evento['inicio'])} a ${_dataBr(evento['fim'])}'
        : _dataBr(evento['inicio']);
    return Card(
      margin: const EdgeInsets.only(bottom: 6),
      child: ListTile(
        dense: true,
        leading: Icon(icone, color: cor),
        title: Text(evento['titulo'] as String? ?? evento['tipo'] as String),
        subtitle: Text('$periodo · $status',
            style: TextStyle(color: cor, fontWeight: FontWeight.w500)),
      ),
    );
  }
}

String _dataBr(dynamic iso) {
  final partes = (iso as String).split('-');
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}
