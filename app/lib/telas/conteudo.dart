import 'package:flutter/material.dart';

import '../armazenamento.dart';
import '../gamificacao.dart' as g;
import '../modelos.dart';
import '../social_api.dart';
import '../tema.dart';

/// Conteudo programatico: grade de quadros por materia (recolhidas).
/// Tocar num quadro abre a materia com a arvore de topicos: checkbox a
/// ESQUERDA marca o topico inteiro, expandir a DIREITA mostra os
/// subtopicos literais, marcaveis um a um.
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
  bool _carregado = false;

  @override
  void initState() {
    super.initState();
    _armazenamento.carregarProgresso().then((p) => setState(() {
          _concluidos = p;
          _carregado = true;
        }));
  }

  @override
  Widget build(BuildContext context) {
    if (!_carregado) {
      return Scaffold(
        appBar: AppBar(title: const Text('Conteúdo')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }
    final pctGeral = g.percentual(_materias, _concluidos);
    return Scaffold(
      appBar: AppBar(title: const Text('Conteúdo programático')),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
          child: Row(children: [
            Expanded(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(5),
                child: LinearProgressIndicator(
                  value: pctGeral,
                  minHeight: 10,
                  backgroundColor: const Color(0xFFEEE8DA),
                  color: pctGeral >= 1 ? dourado : verde,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Text('${(pctGeral * 100).round()}%',
                style: const TextStyle(
                    fontWeight: FontWeight.w800, color: verde)),
          ]),
        ),
        Expanded(
          child: GridView.count(
            padding: const EdgeInsets.all(12),
            crossAxisCount: 2,
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 1.25,
            children: [for (final materia in _materias) _quadroMateria(materia)],
          ),
        ),
      ]),
    );
  }

  Widget _quadroMateria(No materia) {
    final pct = g.percentualMateria(materia, _concluidos);
    final completa = pct >= 1;
    return Card(
      color: completa ? const Color(0xFFF9F3E3) : Colors.white,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () async {
          await Navigator.of(context).push(MaterialPageRoute(
              builder: (_) => MateriaPage(
                    slug: widget.slug,
                    materia: materia,
                    materias: _materias,
                    concluidos: _concluidos,
                    armazenamento: _armazenamento,
                  )));
          setState(() {}); // volta com o progresso novo
        },
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Expanded(
                  child: Text(nomeCurtoMateria(materia.titulo),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleMedium),
                ),
                if (completa) const Text('🏆', style: TextStyle(fontSize: 18)),
              ]),
              const Spacer(),
              if (materia.fases.isNotEmpty)
                Text(materia.fases.join(' · '),
                    style: const TextStyle(
                        fontSize: 11,
                        color: dourado,
                        fontWeight: FontWeight.w700)),
              const SizedBox(height: 6),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: pct,
                  minHeight: 8,
                  backgroundColor: const Color(0xFFEEE8DA),
                  color: completa ? dourado : verde,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                  '${(pct * 100).round()}% · '
                  '${materia.idsSubarvore.skip(1).where(_concluidos.contains).length}'
                  '/${materia.idsSubarvore.length - 1} itens',
                  style:
                      const TextStyle(fontSize: 11, color: Color(0xFF8A8574))),
            ],
          ),
        ),
      ),
    );
  }
}

/// "DIREITO PROCESSUAL DO TRABALHO" -> "Processual do Trabalho"
String nomeCurtoMateria(String titulo) {
  var texto = titulo.trim();
  final semPrefixo = texto.toUpperCase().startsWith('DIREITO ')
      ? texto.substring(8)
      : texto;
  const minusculas = {'do', 'da', 'de', 'dos', 'das', 'e', 'no', 'na'};
  return semPrefixo
      .toLowerCase()
      .split(' ')
      .map((palavra) => minusculas.contains(palavra)
          ? palavra
          : (palavra.isEmpty
              ? palavra
              : palavra[0].toUpperCase() + palavra.substring(1)))
      .join(' ');
}

/// A arvore de uma materia, com o progresso compartilhado com a grade.
class MateriaPage extends StatefulWidget {
  final String slug;
  final No materia;
  final List<No> materias; // arvore inteira, para pontos/percentual do sync
  final Set<String> concluidos; // MESMA instancia da grade
  final Armazenamento armazenamento;
  const MateriaPage({
    super.key,
    required this.slug,
    required this.materia,
    required this.materias,
    required this.concluidos,
    required this.armazenamento,
  });

  @override
  State<MateriaPage> createState() => _MateriaPageState();
}

class _MateriaPageState extends State<MateriaPage> {
  final Set<String> _expandidos = {};

  void _alternar(No no) {
    final ids = no.idsSubarvore.toList();
    final tudoMarcado = ids.every(widget.concluidos.contains);
    setState(() {
      if (tudoMarcado) {
        widget.concluidos.removeAll(ids);
      } else {
        widget.concluidos.addAll(ids);
      }
    });
    widget.armazenamento.salvarProgresso(widget.concluidos);
    widget.armazenamento.registrarNoDiario(
      marcados: tudoMarcado ? const [] : ids,
      desmarcados: tudoMarcado ? ids : const [],
    );
    SocialApi.sincronizarProgresso(
      widget.slug,
      pontos: g.pontos(widget.materias, widget.concluidos),
      percentual: g.percentual(widget.materias, widget.concluidos),
      concluidos: widget.concluidos.length,
    );
  }

  bool? _estado(No no) {
    final ids = no.idsSubarvore.toList();
    final marcados = ids.where(widget.concluidos.contains).length;
    if (marcados == 0) return false;
    if (marcados == ids.length) return true;
    return null; // parcial
  }

  @override
  Widget build(BuildContext context) {
    final pct = g.percentualMateria(widget.materia, widget.concluidos);
    return Scaffold(
      appBar: AppBar(title: Text(nomeCurtoMateria(widget.materia.titulo))),
      body: ListView(padding: const EdgeInsets.all(12), children: [
        Row(children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(5),
              child: LinearProgressIndicator(
                value: pct,
                minHeight: 10,
                backgroundColor: const Color(0xFFEEE8DA),
                color: pct >= 1 ? dourado : verde,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Text('${(pct * 100).round()}%',
              style: const TextStyle(fontWeight: FontWeight.w800, color: verde)),
        ]),
        const SizedBox(height: 8),
        Card(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: Column(children: [
              for (final topico in widget.materia.filhos)
                _linhaNo(topico, recuo: 0),
            ]),
          ),
        ),
      ]),
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
                    color:
                        _estado(no) == true ? const Color(0xFF8A8574) : null,
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
