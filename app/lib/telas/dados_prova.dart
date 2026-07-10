import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';

import '../armazenamento.dart';
import '../modelos.dart';
import '../tema.dart';

/// Dados da prova: o que vem do edital (dia/horario/duracao por fase) +
/// o local do CANDIDATO (CEP + sala), que gera deep links de Uber, 99 e
/// Google Maps. Suporta mais de um local (objetiva, oral...).
class DadosProvaPage extends StatefulWidget {
  final String slug;
  final Edital edital;
  const DadosProvaPage({super.key, required this.slug, required this.edital});

  @override
  State<DadosProvaPage> createState() => _DadosProvaPageState();
}

class _DadosProvaPageState extends State<DadosProvaPage> {
  late final Armazenamento _armazenamento = Armazenamento(widget.slug);
  List<Map<String, dynamic>> _locais = [];

  @override
  void initState() {
    super.initState();
    _armazenamento.carregarLocais().then((l) => setState(() => _locais = l));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dados da prova')),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          Text('Do edital', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 6),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Table(
                columnWidths: const {0: IntrinsicColumnWidth()},
                children: [
                  for (final fase in widget.edital.fasesProva)
                    TableRow(children: [
                      Padding(
                        padding: const EdgeInsets.all(6),
                        child: Text('${fase['fase']}',
                            style: const TextStyle(
                                fontWeight: FontWeight.w700, color: verde)),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(6),
                        child: Text([
                          fase['tipo'],
                          fase['duracao'],
                          if (fase['turno'] != null) 'turno da ${fase['turno']}',
                          fase['formato'],
                        ].whereType<String>().join(' · ')),
                      ),
                    ]),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(
                child: Text('Meus locais de prova',
                    style: Theme.of(context).textTheme.titleMedium)),
            FilledButton.icon(
              onPressed: _adicionarLocal,
              icon: const Icon(Icons.add),
              label: const Text('Adicionar'),
            ),
          ]),
          const SizedBox(height: 6),
          if (_locais.isEmpty)
            const Card(
              child: Padding(
                padding: EdgeInsets.all(14),
                child: Text('Quando a banca divulgar o seu local, cadastre aqui '
                    '(CEP + sala) para gerar as rotas de Uber, 99 e Maps.'),
              ),
            ),
          for (var i = 0; i < _locais.length; i++) _cardLocal(i),
        ],
      ),
    );
  }

  Widget _cardLocal(int indice) {
    final local = _locais[indice];
    final endereco = [
      local['endereco'],
      local['numero'],
    ].whereType<String>().where((s) => s.isNotEmpty).join(', ');
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(
                child: Text(local['identificacao'] as String? ?? 'Local',
                    style: const TextStyle(fontWeight: FontWeight.w700))),
            IconButton(
              icon: const Icon(Icons.delete_outline, size: 20),
              onPressed: () {
                setState(() => _locais.removeAt(indice));
                _armazenamento.salvarLocais(_locais);
              },
            ),
          ]),
          Text(endereco.isEmpty ? 'Sem endereço' : endereco),
          if ((local['sala'] as String?)?.isNotEmpty == true)
            Text('Sala: ${local['sala']}'),
          const SizedBox(height: 8),
          Wrap(spacing: 8, runSpacing: 4, children: [
            _botaoRota('Uber', Uri.parse(
                'https://m.uber.com/ul/?action=setPickup&pickup=my_location'
                '&dropoff[formatted_address]=${Uri.encodeComponent(endereco)}')),
            _botaoRota('99', Uri.parse('https://99app.com/')),
            _botaoRota('Maps (carro)', _maps(endereco, 'driving')),
            _botaoRota('Maps (transporte)', _maps(endereco, 'transit')),
          ]),
        ]),
      ),
    );
  }

  Uri _maps(String endereco, String modo) => Uri.parse(
      'https://www.google.com/maps/dir/?api=1&destination='
      '${Uri.encodeComponent(endereco)}&travelmode=$modo');

  Widget _botaoRota(String rotulo, Uri uri) => OutlinedButton(
        onPressed: () => launchUrl(uri, mode: LaunchMode.externalApplication),
        child: Text(rotulo, style: const TextStyle(fontSize: 12)),
      );

  Future<void> _adicionarLocal() async {
    final novo = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (_) => const _DialogoLocal(),
    );
    if (novo != null) {
      setState(() => _locais.add(novo));
      await _armazenamento.salvarLocais(_locais);
    }
  }
}

class _DialogoLocal extends StatefulWidget {
  const _DialogoLocal();

  @override
  State<_DialogoLocal> createState() => _DialogoLocalState();
}

class _DialogoLocalState extends State<_DialogoLocal> {
  final _identificacao = TextEditingController(text: 'Prova objetiva');
  final _cep = TextEditingController();
  final _endereco = TextEditingController();
  final _numero = TextEditingController();
  final _sala = TextEditingController();
  bool _buscandoCep = false;

  Future<void> _buscarCep() async {
    final cep = _cep.text.replaceAll(RegExp(r'\D'), '');
    if (cep.length != 8) return;
    setState(() => _buscandoCep = true);
    try {
      final resposta =
          await http.get(Uri.parse('https://viacep.com.br/ws/$cep/json/'));
      final dados = jsonDecode(resposta.body) as Map<String, dynamic>;
      if (dados['erro'] != true) {
        _endereco.text = [
          dados['logradouro'],
          dados['bairro'],
          dados['localidade'],
          dados['uf'],
        ].whereType<String>().where((s) => s.isNotEmpty).join(', ');
      }
    } catch (_) {
      // sem rede: o candidato digita o endereco na mao
    } finally {
      if (mounted) setState(() => _buscandoCep = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Meu local de prova'),
      content: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(
              controller: _identificacao,
              decoration: const InputDecoration(labelText: 'Identificação')),
          TextField(
            controller: _cep,
            decoration: InputDecoration(
              labelText: 'CEP',
              suffixIcon: _buscandoCep
                  ? const Padding(
                      padding: EdgeInsets.all(10),
                      child: SizedBox(
                          width: 16, height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2)))
                  : IconButton(
                      icon: const Icon(Icons.search), onPressed: _buscarCep),
            ),
            keyboardType: TextInputType.number,
            onSubmitted: (_) => _buscarCep(),
          ),
          TextField(
              controller: _endereco,
              decoration: const InputDecoration(labelText: 'Endereço')),
          TextField(
              controller: _numero,
              decoration:
                  const InputDecoration(labelText: 'Número / complemento')),
          TextField(
              controller: _sala,
              decoration: const InputDecoration(labelText: 'Sala de aplicação')),
        ]),
      ),
      actions: [
        TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancelar')),
        FilledButton(
          onPressed: () => Navigator.of(context).pop({
            'identificacao': _identificacao.text,
            'cep': _cep.text,
            'endereco': _endereco.text,
            'numero': _numero.text,
            'sala': _sala.text,
          }),
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}
