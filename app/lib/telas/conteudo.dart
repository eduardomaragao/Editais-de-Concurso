import 'package:flutter/material.dart';

import '../armazenamento.dart';
import '../modelos.dart';
import '../tema.dart';

/// Arvore de conteudo: checkbox a ESQUERDA marca o topico inteiro (com os
/// subtopicos); expandir a DIREITA mostra os subtopicos literais, marcaveis
/// um a um. Progresso e do USUARIO, salvo por candidato + edital.
class ConteudoPage extends StatefulWidget {
  final String slug;
  final Edital edital;
  const ConteudoPage({super.key, required this.slug, required this.edital});

  @override
  State<ConteudoPage> createState() => _ConteudoPageState();
}

class _ConteudoPageState extends State<ConteudoPage> {
  late final Armazenamento _armazenamento = Armazenamento(widget.slug);
  late final List<No> _materias = montarArvore(widget.edital.conteudo);
  Set<String> _concluidos = {};
  final Set<String> _expandidos = {};
  bool _carregado = false;

  @override
  void initState() {
    super.initState();
    _armazenamento.carregarProgresso().then((p) {
      setState(() {
        _concluidos = p;
        _carregado = true;
      });
    });
  }

  void _alternar(No no) {
    final ids = no.idsSubarvore.toList();
    final tudoMarcado = ids.every(_concluidos.contains);
    setState(() {
      if (tudoMarcado) {
        _concluidos.removeAll(ids);
      } else {
        _concluidos.addAll(ids);
      }
    });
    _armazenamento.salvarProgresso(_concluidos);
  }

  bool? _estado(No no) {
    final ids = no.idsSubarvore.toList();
    final marcados = ids.where(_concluidos.contains).length;
    if (marcados == 0) return false;
    if (marcados == ids.length) return true;
    return null; // parcial
  }

  double _progresso(No materia) {
    final ids = materia.idsSubarvore.skip(1).toList(); // sem o no da materia
    if (ids.isEmpty) return 0;
    return ids.where(_concluidos.contains).length / ids.length;
  }

  @override
  Widget build(BuildContext context) {
    if (!_carregado) {
      return Scaffold(
        appBar: AppBar(title: const Text('Conteúdo')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Conteúdo programático')),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          for (final materia in _materias) _cardMateria(materia),
        ],
      ),
    );
  }

  Widget _cardMateria(No materia) {
    final progresso = _progresso(materia);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Expanded(
                    child: Text(materia.titulo,
                        style: Theme.of(context).textTheme.titleMedium)),
                if (materia.fases.isNotEmpty)
                  Text(materia.fases.join(' · '),
                      style: const TextStyle(
                          fontSize: 12,
                          color: dourado,
                          fontWeight: FontWeight.w600)),
              ]),
              const SizedBox(height: 6),
              LinearProgressIndicator(
                value: progresso,
                backgroundColor: const Color(0xFFEEE8DA),
                color: progresso >= 1 ? dourado : verde,
              ),
              Text('${(progresso * 100).round()}% concluído',
                  style: const TextStyle(fontSize: 11, color: Color(0xFF8A8574))),
            ]),
          ),
          const SizedBox(height: 4),
          for (final topico in materia.filhos) _linhaNo(topico, recuo: 0),
        ]),
      ),
    );
  }

  Widget _linhaNo(No no, {required int recuo}) {
    final expandido = _expandidos.contains(no.id);
    return Column(children: [
      InkWell(
        onTap: no.filhos.isEmpty ? () => _alternar(no) : null,
        child: Padding(
          padding: EdgeInsets.only(left: 8.0 + recuo * 22),
          child: Row(children: [
            Checkbox(
              tristate: true,
              value: _estado(no),
              activeColor: verde,
              onChanged: (_) => _alternar(no),
            ),
            Expanded(
              child: Text(no.titulo,
                  style: TextStyle(
                    fontSize: 14,
                    decoration: _estado(no) == true
                        ? TextDecoration.lineThrough
                        : null,
                    color: _estado(no) == true
                        ? const Color(0xFF8A8574)
                        : null,
                  )),
            ),
            if (no.filhos.isNotEmpty)
              IconButton(
                icon: Icon(expandido ? Icons.expand_less : Icons.expand_more,
                    color: verde),
                onPressed: () => setState(() {
                  expandido ? _expandidos.remove(no.id) : _expandidos.add(no.id);
                }),
              ),
          ]),
        ),
      ),
      if (expandido)
        for (final filho in no.filhos) _linhaNo(filho, recuo: recuo + 1),
    ]);
  }
}
