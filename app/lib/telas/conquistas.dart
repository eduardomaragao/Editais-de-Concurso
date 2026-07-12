import 'package:flutter/material.dart';

import '../armazenamento.dart';
import '../compartilhar.dart';
import '../gamificacao.dart' as g;
import '../modelos.dart';
import '../tema.dart';

/// Pontos, insignias e os cards de compartilhar nos Stories.
class ConquistasPage extends StatefulWidget {
  final String slug;
  final Edital edital;
  const ConquistasPage({super.key, required this.slug, required this.edital});

  @override
  State<ConquistasPage> createState() => _ConquistasPageState();
}

class _ConquistasPageState extends State<ConquistasPage> {
  late final List<No> _materias = montarArvore(widget.edital.conteudo);
  Set<String> _concluidos = {};
  Map<String, List<String>> _diario = {};
  bool _carregado = false;

  @override
  void initState() {
    super.initState();
    final armazenamento = Armazenamento(widget.slug);
    Future.wait([
      armazenamento.carregarProgresso(),
      armazenamento.carregarDiario(),
    ]).then((resultados) => setState(() {
          _concluidos = resultados[0] as Set<String>;
          _diario = resultados[1] as Map<String, List<String>>;
          _carregado = true;
        }));
  }

  @override
  Widget build(BuildContext context) {
    if (!_carregado) {
      return Scaffold(
          appBar: AppBar(title: const Text('Conquistas')),
          body: const Center(child: CircularProgressIndicator()));
    }
    final pontos = g.pontos(_materias, _concluidos);
    final pct = g.percentual(_materias, _concluidos);
    final sequencia = g.sequenciaDias(_diario, DateTime.now());
    final insignias = g.insignias(_materias, _concluidos, sequencia);
    final conquistadas = insignias.where((i) => i.conquistada).length;

    return Scaffold(
      appBar: AppBar(title: const Text('Conquistas')),
      body: ListView(padding: const EdgeInsets.all(12), children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(children: [
              Expanded(
                  child: Column(children: [
                Text('$pontos',
                    style: const TextStyle(
                        fontSize: 34, fontWeight: FontWeight.w800, color: verde)),
                const Text('pontos', style: TextStyle(fontSize: 12)),
              ])),
              Expanded(
                  child: Column(children: [
                Text('${(pct * 100).round()}%',
                    style: const TextStyle(
                        fontSize: 34, fontWeight: FontWeight.w800, color: dourado)),
                const Text('do edital', style: TextStyle(fontSize: 12)),
              ])),
              Expanded(
                  child: Column(children: [
                Text('$sequencia',
                    style: const TextStyle(
                        fontSize: 34, fontWeight: FontWeight.w800, color: verde)),
                Text(sequencia == 1 ? 'dia seguido' : 'dias seguidos',
                    style: const TextStyle(fontSize: 12)),
              ])),
            ]),
          ),
        ),
        const SizedBox(height: 8),
        Text('Insígnias ($conquistadas/${insignias.length})',
            style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          childAspectRatio: 2.6,
          mainAxisSpacing: 8,
          crossAxisSpacing: 8,
          children: [
            for (final insignia in insignias)
              Opacity(
                opacity: insignia.conquistada ? 1 : 0.35,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    child: Row(children: [
                      Text(insignia.emoji, style: const TextStyle(fontSize: 24)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(insignia.titulo,
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w700, fontSize: 13)),
                              Text(insignia.descricao,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(fontSize: 10)),
                            ]),
                      ),
                    ]),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 16),
        Text('Postar nos Stories', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        Card(
            child: ListTile(
          leading: const Icon(Icons.today, color: dourado),
          title: const Text('O que estudei hoje'),
          onTap: () => _postarHoje(pct),
        )),
        Card(
            child: ListTile(
          leading: const Icon(Icons.emoji_events, color: dourado),
          title: const Text('Meu progresso no edital'),
          onTap: () => _postarEdital(pontos, pct, sequencia),
        )),
        Card(
            child: ListTile(
          leading: const Icon(Icons.menu_book, color: dourado),
          title: const Text('Progresso de uma matéria'),
          onTap: _escolherMateria,
        )),
      ]),
    );
  }

  String get _hojeChave {
    final hoje = DateTime.now();
    return '${hoje.year.toString().padLeft(4, '0')}-'
        '${hoje.month.toString().padLeft(2, '0')}-'
        '${hoje.day.toString().padLeft(2, '0')}';
  }

  void _postarHoje(double pct) {
    final idsHoje = _diario[_hojeChave] ?? const [];
    final titulos = {
      for (final no in widget.edital.conteudo) no['id'] as String: no['titulo'] as String
    };
    mostrarCardStories(
      context,
      CardStories(
        titulo: 'Hoje eu estudei',
        destaque: '${idsHoje.length}',
        subtitulo: idsHoje.length == 1
            ? 'item do edital concluído'
            : 'itens do edital concluídos · ${(pct * 100).round()}% no total',
        percentual: pct,
        itens: [for (final id in idsHoje) titulos[id] ?? id],
      ),
    );
  }

  void _postarEdital(int pontos, double pct, int sequencia) {
    mostrarCardStories(
      context,
      CardStories(
        titulo: '${widget.edital.orgao} — rumo à aprovação',
        destaque: '${(pct * 100).round()}%',
        subtitulo: '$pontos pontos · $sequencia dia(s) seguidos de estudo',
        percentual: pct,
      ),
    );
  }

  void _escolherMateria() {
    showModalBottomSheet(
      context: context,
      builder: (_) => ListView(children: [
        for (final materia in _materias)
          ListTile(
            title: Text(materia.titulo),
            trailing: Text(
                '${(g.percentualMateria(materia, _concluidos) * 100).round()}%'),
            onTap: () {
              Navigator.of(context).pop();
              final pctMateria = g.percentualMateria(materia, _concluidos);
              final feitos = materia.idsSubarvore
                  .skip(1)
                  .where(_concluidos.contains)
                  .length;
              mostrarCardStories(
                context,
                CardStories(
                  titulo: materia.titulo,
                  destaque: '${(pctMateria * 100).round()}%',
                  subtitulo:
                      '$feitos itens concluídos · ${widget.edital.orgao}',
                  percentual: pctMateria,
                ),
              );
            },
          ),
      ]),
    );
  }
}
