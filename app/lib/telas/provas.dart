import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../modelos.dart';

/// Provas anteriores (2020+), abas Objetivas / Subjetivas / Orais.
/// Oral: NUNCA a gravacao (proibido pela banca) — so pontos e espelho.
class ProvasPage extends StatelessWidget {
  final Edital edital;
  const ProvasPage({super.key, required this.edital});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Provas anteriores'),
          bottom: const TabBar(
            labelColor: Colors.white,
            unselectedLabelColor: Color(0xFFCFE0D8),
            indicatorColor: Color(0xFFB8862F),
            tabs: [
              Tab(text: 'Objetivas'),
              Tab(text: 'Subjetivas'),
              Tab(text: 'Orais'),
            ],
          ),
        ),
        body: TabBarView(children: [
          _aba(context, 'objetiva'),
          _aba(context, 'subjetiva'),
          _aba(context, 'oral'),
        ]),
      ),
    );
  }

  Widget _aba(BuildContext context, String tipo) {
    final provas =
        edital.provasAnteriores.where((p) => p['tipo'] == tipo).toList()
          ..sort((a, b) => (b['ano'] as int).compareTo(a['ano'] as int));
    if (provas.isEmpty) {
      return const Center(
          child: Padding(
        padding: EdgeInsets.all(24),
        child: Text('Nenhuma prova cadastrada ainda nesta categoria.',
            textAlign: TextAlign.center),
      ));
    }
    return ListView(
      padding: const EdgeInsets.all(12),
      children: [
        for (final prova in provas)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child:
                  Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('${prova['orgao'] ?? edital.orgao} · ${prova['ano']}',
                    style: Theme.of(context).textTheme.titleMedium),
                if (prova['banca'] != null) Text('Banca: ${prova['banca']}'),
                const SizedBox(height: 8),
                Wrap(spacing: 8, children: [
                  if (prova['arquivo_prova'] != null)
                    _botao(tipo == 'oral' ? 'Pontos' : 'Prova',
                        prova['arquivo_prova'] as String),
                  if (prova['arquivo_resposta'] != null)
                    _botao(
                      switch ((prova['arquivo_resposta']
                          as Map<String, dynamic>)['tipo']) {
                        'gabarito' => 'Gabarito',
                        'padrao_resposta' => 'Padrão de resposta',
                        _ => 'Espelho',
                      },
                      (prova['arquivo_resposta'] as Map<String, dynamic>)['url']
                          as String,
                    ),
                ]),
              ]),
            ),
          ),
      ],
    );
  }

  Widget _botao(String rotulo, String url) => OutlinedButton.icon(
        icon: const Icon(Icons.picture_as_pdf, size: 16),
        label: Text(rotulo),
        onPressed: () =>
            launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication),
      );
}
