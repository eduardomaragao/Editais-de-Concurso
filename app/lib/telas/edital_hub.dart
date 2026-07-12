import 'package:flutter/material.dart';

import '../api.dart';
import '../modelos.dart';
import '../social_api.dart';
import '../tema.dart';
import 'amigos.dart';
import 'conquistas.dart';
import 'conteudo.dart';
import 'cronometro.dart';
import 'dados_prova.dart';
import 'datas.dart';
import 'provas.dart';

class EditalHubPage extends StatefulWidget {
  final String slug;
  const EditalHubPage({super.key, required this.slug});

  @override
  State<EditalHubPage> createState() => _EditalHubPageState();
}

class _EditalHubPageState extends State<EditalHubPage> {
  late Future<Edital> _edital;

  @override
  void initState() {
    super.initState();
    _edital = Api().obterEdital(widget.slug);
    _mostrarIncentivos();
  }

  Future<void> _mostrarIncentivos() async {
    try {
      final incentivos = await SocialApi.buscarIncentivos();
      if (incentivos.isEmpty || !mounted) return;
      final primeiro = incentivos.first;
      final extra =
          incentivos.length > 1 ? ' (+${incentivos.length - 1} em Amigos)' : '';
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        duration: const Duration(seconds: 6),
        content:
            Text('💌 ${primeiro['de']}: "${primeiro['mensagem']}"$extra'),
      ));
    } catch (_) {
      // sem perfil ou sem rede — segue o jogo
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder(
      future: _edital,
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return Scaffold(
            appBar: AppBar(title: Text(widget.slug)),
            body: snapshot.hasError
                ? Center(child: Text('Erro: ${snapshot.error}'))
                : const Center(child: CircularProgressIndicator()),
          );
        }
        final edital = snapshot.data!;
        return Scaffold(
          appBar: AppBar(title: Text(edital.orgao)),
          body: ListView(
            padding: const EdgeInsets.all(12),
            children: [
              Text(edital.cargo, style: Theme.of(context).textTheme.headlineSmall),
              Text('Edital ${edital.numero} · ${edital.banca}',
                  style: Theme.of(context).textTheme.bodySmall),
              const SizedBox(height: 8),
              _seloRadar(edital),
              const SizedBox(height: 12),
              _cardCorte(context, edital),
              const SizedBox(height: 4),
              _cardNavegacao(context, Icons.menu_book, 'Conteúdo programático',
                  'Matérias, tópicos e progresso',
                  ConteudoPage(slug: widget.slug, edital: edital)),
              _cardNavegacao(context, Icons.timer, 'Relógio de estudo',
                  'Cronometre, foque e acompanhe suas horas',
                  CronometroPage(slug: widget.slug, edital: edital)),
              _cardNavegacao(context, Icons.event, 'Datas',
                  'Calendário, cronograma e suas datas',
                  DatasPage(slug: widget.slug, edital: edital)),
              _cardNavegacao(context, Icons.place, 'Dados da prova',
                  'Dia, horário e o seu local de prova',
                  DadosProvaPage(slug: widget.slug, edital: edital)),
              _cardNavegacao(context, Icons.history_edu, 'Provas anteriores',
                  'Objetivas · Subjetivas · Orais (2020+)',
                  ProvasPage(edital: edital)),
              _cardNavegacao(context, Icons.emoji_events, 'Conquistas',
                  'Pontos, insígnias e postar nos Stories',
                  ConquistasPage(slug: widget.slug, edital: edital)),
              _cardNavegacao(context, Icons.group, 'Amigos',
                  'Ranking, incentivos e competição saudável',
                  AmigosPage(slug: widget.slug)),
            ],
          ),
        );
      },
    );
  }

  Widget _seloRadar(Edital edital) {
    final desatualizado = edital.radarDesatualizado;
    final (cor, texto) = switch (desatualizado) {
      true => (
          Colors.red.shade700,
          'Atenção: retificação publicada (${edital.ultimaRetificacao}) ainda não incorporada.'
        ),
      false => (verde, 'Radar em dia — ${edital.versaoArquivo ?? "edital atualizado"}.'),
      null => (Colors.grey.shade600, 'Radar ainda não verificado.'),
    };
    return Row(children: [
      Icon(Icons.radar, size: 18, color: cor),
      const SizedBox(width: 6),
      Expanded(child: Text(texto, style: TextStyle(color: cor, fontSize: 13))),
    ]);
  }

  Widget _cardCorte(BuildContext context, Edital edital) {
    final corte = edital.corte;
    if (corte['informado'] != true) return const SizedBox.shrink();
    return Card(
      color: const Color(0xFFF6F1E4),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Corte de lei & jurisprudência',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 6),
          Text('Legislação até ${_dataBr(corte['legislacao_ate'])} · '
              'Jurisprudência até ${_dataBr(corte['jurisprudencia_ate'])}'),
          if (corte['afetado_por_retificacao'] == false)
            const Text('Retificações não movem este corte.',
                style: TextStyle(fontSize: 12, color: Color(0xFF8A8574))),
        ]),
      ),
    );
  }

  Widget _cardNavegacao(BuildContext context, IconData icone, String titulo,
      String subtitulo, Widget destino) {
    return Card(
      child: ListTile(
        leading: Icon(icone, color: verde),
        title: Text(titulo, style: Theme.of(context).textTheme.titleMedium),
        subtitle: Text(subtitulo),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => Navigator.of(context)
            .push(MaterialPageRoute(builder: (_) => destino)),
      ),
    );
  }
}

String _dataBr(dynamic iso) {
  if (iso == null) return '—';
  final partes = (iso as String).split('-');
  return '${partes[2]}/${partes[1]}/${partes[0]}';
}
