import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:table_calendar/table_calendar.dart';

import '../armazenamento.dart';
import '../ics.dart';
import '../modelos.dart';
import '../tema.dart';

/// Datas: calendario com marcadores, cronograma do edital + datas do
/// candidato (simulados, revisoes...), status por evento e agenda (.ics).
class DatasPage extends StatefulWidget {
  final String slug;
  final Edital edital;
  const DatasPage({super.key, required this.slug, required this.edital});

  @override
  State<DatasPage> createState() => _DatasPageState();
}

class _DatasPageState extends State<DatasPage> {
  late final Armazenamento _armazenamento = Armazenamento(widget.slug);
  List<Map<String, dynamic>> _meus = [];
  DateTime _focado = DateTime.now();
  DateTime? _selecionado;

  @override
  void initState() {
    super.initState();
    _armazenamento.carregarEventos().then((e) => setState(() => _meus = e));
  }

  List<Map<String, dynamic>> get _todos {
    final lista = [...widget.edital.cronograma, ..._meus];
    lista.sort((a, b) => (a['inicio'] as String).compareTo(b['inicio'] as String));
    return lista;
  }

  List<Map<String, dynamic>> _eventosDoDia(DateTime dia) {
    final chave = chaveDoDia(dia);
    return _todos.where((e) {
      final inicio = e['inicio'] as String;
      final fim = (e['fim'] as String?) ?? inicio;
      return chave.compareTo(inicio) >= 0 && chave.compareTo(fim) <= 0;
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final hoje = DateTime.now();
    return Scaffold(
      appBar: AppBar(title: const Text('Datas')),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: verde,
        foregroundColor: Colors.white,
        onPressed: _adicionarData,
        icon: const Icon(Icons.add),
        label: const Text('Adicionar data'),
      ),
      body: ListView(padding: const EdgeInsets.all(12), children: [
        Card(
          child: TableCalendar<Map<String, dynamic>>(
            locale: 'pt_BR',
            firstDay: DateTime(hoje.year - 1),
            lastDay: DateTime(hoje.year + 2, 12, 31),
            focusedDay: _focado,
            selectedDayPredicate: (dia) =>
                _selecionado != null && isSameDay(dia, _selecionado),
            onDaySelected: (selecionado, focado) => setState(() {
              _selecionado = isSameDay(_selecionado, selecionado) ? null : selecionado;
              _focado = focado;
            }),
            onPageChanged: (focado) => _focado = focado,
            eventLoader: _eventosDoDia,
            availableCalendarFormats: const {CalendarFormat.month: 'Mês'},
            calendarStyle: CalendarStyle(
              todayDecoration: BoxDecoration(
                  color: verde.withValues(alpha: 0.35), shape: BoxShape.circle),
              selectedDecoration:
                  const BoxDecoration(color: verde, shape: BoxShape.circle),
              markerDecoration:
                  const BoxDecoration(color: dourado, shape: BoxShape.circle),
            ),
            headerStyle: const HeaderStyle(
                titleCentered: true, formatButtonVisible: false),
          ),
        ),
        if (_selecionado != null) ...[
          const SizedBox(height: 4),
          Text('Em ${_dataBr(chaveDoDia(_selecionado!))}',
              style: Theme.of(context).textTheme.titleMedium),
          if (_eventosDoDia(_selecionado!).isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 8),
              child: Text('Nada neste dia — que tal uma revisão?'),
            ),
          for (final evento in _eventosDoDia(_selecionado!))
            _linhaEvento(evento, hoje),
          const Divider(),
        ],
        Card(
          child: ListTile(
            leading: const Icon(Icons.calendar_month, color: verde),
            title: const Text('Adicionar à agenda'),
            subtitle: const Text(
                'Copia tudo em formato .ics (Google/Apple/Outlook)'),
            trailing: const Icon(Icons.copy),
            onTap: () async {
              final ics = gerarIcs(_todos, widget.edital.orgao);
              await Clipboard.setData(ClipboardData(text: ics));
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                    content: Text('Cronograma .ics copiado — cole num arquivo '
                        '.ics e importe na agenda.')));
              }
            },
          ),
        ),
        const SizedBox(height: 8),
        Text('Todas as datas', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 4),
        for (final evento in _todos) _linhaEvento(evento, hoje),
        const SizedBox(height: 72), // espaco para o FAB
      ]),
    );
  }

  Widget _linhaEvento(Map<String, dynamic> evento, DateTime hoje) {
    final status = statusEvento(evento, hoje);
    final meu = evento['meu'] == true;
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
        leading: Icon(meu ? Icons.push_pin_outlined : icone, color: cor),
        title: Text(evento['titulo'] as String? ?? evento['tipo'] as String),
        subtitle: Text('$periodo · $status${meu ? ' · sua data' : ''}',
            style: TextStyle(color: cor, fontWeight: FontWeight.w500)),
        trailing: meu
            ? IconButton(
                icon: const Icon(Icons.delete_outline, size: 20),
                onPressed: () {
                  setState(() => _meus.remove(evento));
                  _armazenamento.salvarEventos(_meus);
                },
              )
            : null,
      ),
    );
  }

  Future<void> _adicionarData() async {
    final titulo = TextEditingController();
    DateTime? inicio;
    DateTime? fim;
    final salvar = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setStateDialogo) => AlertDialog(
          title: const Text('Nova data'),
          content: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(
                controller: titulo,
                decoration: const InputDecoration(
                    labelText: 'Título (ex.: Simulado, Revisão de Civil)')),
            const SizedBox(height: 8),
            ListTile(
              dense: true,
              leading: const Icon(Icons.event),
              title: Text(inicio == null
                  ? 'Escolher o dia'
                  : 'Dia: ${_dataBr(chaveDoDia(inicio!))}'),
              onTap: () async {
                final escolhido = await showDatePicker(
                  context: dialogContext,
                  initialDate: _selecionado ?? DateTime.now(),
                  firstDate: DateTime(2025),
                  lastDate: DateTime(2030),
                );
                if (escolhido != null) {
                  setStateDialogo(() => inicio = escolhido);
                }
              },
            ),
            ListTile(
              dense: true,
              leading: const Icon(Icons.event_repeat),
              title: Text(fim == null
                  ? 'Até (opcional)'
                  : 'Até: ${_dataBr(chaveDoDia(fim!))}'),
              onTap: () async {
                final escolhido = await showDatePicker(
                  context: dialogContext,
                  initialDate: inicio ?? DateTime.now(),
                  firstDate: inicio ?? DateTime(2025),
                  lastDate: DateTime(2030),
                );
                if (escolhido != null) {
                  setStateDialogo(() => fim = escolhido);
                }
              },
            ),
          ]),
          actions: [
            TextButton(
                onPressed: () => Navigator.of(dialogContext).pop(false),
                child: const Text('Cancelar')),
            FilledButton(
                onPressed: () => Navigator.of(dialogContext).pop(true),
                child: const Text('Salvar')),
          ],
        ),
      ),
    );
    if (salvar != true || titulo.text.trim().isEmpty || inicio == null) return;
    setState(() {
      _meus.add({
        'tipo': 'outro',
        'titulo': titulo.text.trim(),
        'inicio': chaveDoDia(inicio!),
        'fim': fim != null ? chaveDoDia(fim!) : null,
        'meu': true,
      });
    });
    await _armazenamento.salvarEventos(_meus);
  }
}

String _dataBr(dynamic iso) {
  final partes = (iso as String).split('-');
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}
