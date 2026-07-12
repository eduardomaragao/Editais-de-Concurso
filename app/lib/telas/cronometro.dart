import 'dart:async';

import 'package:android_intent_plus/android_intent.dart';
import 'package:flutter/foundation.dart' show kIsWeb, defaultTargetPlatform, TargetPlatform;
import 'package:flutter/material.dart';

import '../armazenamento.dart';
import '../compartilhar.dart';
import '../gamificacao.dart' as g;
import '../modelos.dart';
import '../tema.dart';
import '../tempo.dart' as tempo;

/// Relogio de estudo: cronometra a sessao com a materia escolhida, modo
/// foco (abre o Nao Perturbe do sistema) e metricas de horas por
/// dia/semana/mes/ano — compartilhaveis nos Stories.
class CronometroPage extends StatefulWidget {
  final String slug;
  final Edital edital;
  const CronometroPage({super.key, required this.slug, required this.edital});

  @override
  State<CronometroPage> createState() => _CronometroPageState();
}

class _CronometroPageState extends State<CronometroPage> {
  late final Armazenamento _armazenamento = Armazenamento(widget.slug);
  late final List<No> _materias = montarArvore(widget.edital.conteudo);

  tempo.Sessoes _sessoes = {};
  Set<String> _concluidos = {};
  String _materiaSelecionada = 'geral';
  int _segundos = 0;
  Timer? _tique;
  bool _carregado = false;

  bool get _rodando => _tique != null;

  @override
  void initState() {
    super.initState();
    Future.wait([
      _armazenamento.carregarSessoes(),
      _armazenamento.carregarProgresso(),
    ]).then((r) => setState(() {
          _sessoes = r[0] as tempo.Sessoes;
          _concluidos = r[1] as Set<String>;
          _carregado = true;
        }));
  }

  @override
  void dispose() {
    _tique?.cancel();
    if (_segundos > 0) {
      // saiu da tela com o relogio andando: a sessao nao se perde
      _armazenamento.registrarSessao(_materiaSelecionada, _segundos);
    }
    super.dispose();
  }

  void _iniciar() {
    _tique = Timer.periodic(
        const Duration(seconds: 1), (_) => setState(() => _segundos++));
    setState(() {});
  }

  void _pausar() {
    _tique?.cancel();
    _tique = null;
    setState(() {});
  }

  Future<void> _encerrar() async {
    _pausar();
    if (_segundos == 0) return;
    final duracao = _segundos;
    _sessoes =
        await _armazenamento.registrarSessao(_materiaSelecionada, duracao);
    setState(() => _segundos = 0);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Sessão de ${tempo.formatarDuracao(duracao)} '
              'registrada em ${_nomeMateria(_materiaSelecionada)}! 📚')));
    }
  }

  Future<void> _modoFoco() async {
    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      try {
        await const AndroidIntent(action: 'android.settings.ZEN_MODE_SETTINGS')
            .launch();
        return;
      } catch (_) {/* cai no aviso abaixo */}
    }
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('No celular, este botão abre o "Não Perturbe" do '
              'sistema para silenciar as notificações enquanto você estuda.')));
    }
  }

  String _nomeMateria(String id) {
    if (id == 'geral') return 'Estudo geral';
    final materia =
        _materias.where((m) => m.id == id).map((m) => m.titulo).firstOrNull;
    return materia ?? id;
  }

  @override
  Widget build(BuildContext context) {
    if (!_carregado) {
      return Scaffold(
          appBar: AppBar(title: const Text('Relógio de estudo')),
          body: const Center(child: CircularProgressIndicator()));
    }
    final hoje = DateTime.now();
    return Scaffold(
      appBar: AppBar(title: const Text('Relógio de estudo')),
      body: ListView(padding: const EdgeInsets.all(12), children: [
        _cardCronometro(),
        Card(
          child: ListTile(
            leading: const Icon(Icons.do_not_disturb_on, color: verde),
            title: const Text('Modo foco'),
            subtitle: const Text(
                'Silencie as notificações do celular enquanto estuda'),
            trailing: const Icon(Icons.chevron_right),
            onTap: _modoFoco,
          ),
        ),
        const SizedBox(height: 8),
        Text('Suas horas', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 6),
        _cardMetricas(hoje),
        Card(
          child: ListTile(
            leading: const Icon(Icons.ios_share, color: dourado),
            title: const Text('Postar horas nos Stories'),
            onTap: () => _postarHoras(hoje),
          ),
        ),
      ]),
    );
  }

  Widget _cardCronometro() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(children: [
          DropdownButtonFormField<String>(
            initialValue: _materiaSelecionada,
            decoration: const InputDecoration(
                labelText: 'O que você está estudando?',
                border: OutlineInputBorder()),
            items: [
              const DropdownMenuItem(value: 'geral', child: Text('Estudo geral')),
              for (final materia in _materias)
                DropdownMenuItem(
                    value: materia.id,
                    child: Text(materia.titulo,
                        overflow: TextOverflow.ellipsis)),
            ],
            onChanged: _rodando
                ? null // troca de materia so com o relogio parado
                : (valor) =>
                    setState(() => _materiaSelecionada = valor ?? 'geral'),
          ),
          const SizedBox(height: 16),
          Text(tempo.formatarCronometro(_segundos),
              style: const TextStyle(
                  fontSize: 56,
                  fontWeight: FontWeight.w800,
                  color: verde,
                  fontFeatures: [FontFeature.tabularFigures()])),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            if (!_rodando)
              FilledButton.icon(
                  onPressed: _iniciar,
                  icon: const Icon(Icons.play_arrow),
                  label: Text(_segundos == 0 ? 'Começar' : 'Continuar'))
            else
              FilledButton.icon(
                  style: FilledButton.styleFrom(backgroundColor: dourado),
                  onPressed: _pausar,
                  icon: const Icon(Icons.pause),
                  label: const Text('Pausar')),
            const SizedBox(width: 10),
            OutlinedButton.icon(
                onPressed: _segundos > 0 ? _encerrar : null,
                icon: const Icon(Icons.stop),
                label: const Text('Encerrar')),
          ]),
        ]),
      ),
    );
  }

  Widget _cardMetricas(DateTime hoje) {
    Widget metrica(String rotulo, int segundos) => Expanded(
          child: Column(children: [
            Text(tempo.formatarDuracao(segundos),
                style: const TextStyle(
                    fontWeight: FontWeight.w800, fontSize: 16, color: verde)),
            Text(rotulo, style: const TextStyle(fontSize: 11)),
          ]),
        );
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 14),
        child: Row(children: [
          metrica('hoje', tempo.segundosHoje(_sessoes, hoje)),
          metrica('semana', tempo.segundosNaSemana(_sessoes, hoje)),
          metrica('mês', tempo.segundosNoMes(_sessoes, hoje)),
          metrica('ano', tempo.segundosNoAno(_sessoes, hoje)),
        ]),
      ),
    );
  }

  void _postarHoras(DateTime hoje) {
    final porMateria = tempo.segundosPorMateria(_sessoes,
        de: hoje.subtract(const Duration(days: 6)), ate: hoje);
    final top = porMateria.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    mostrarCardStories(
      context,
      CardStories(
        titulo: 'Minhas horas de estudo',
        destaque: tempo.formatarDuracao(tempo.segundosHoje(_sessoes, hoje)),
        subtitulo:
            'hoje · ${widget.edital.orgao} — ${(g.percentual(_materias, _concluidos) * 100).round()}% do edital',
        percentual: g.percentual(_materias, _concluidos),
        itens: [
          'Semana: ${tempo.formatarDuracao(tempo.segundosNaSemana(_sessoes, hoje))}',
          'Mês: ${tempo.formatarDuracao(tempo.segundosNoMes(_sessoes, hoje))}',
          'Ano: ${tempo.formatarDuracao(tempo.segundosNoAno(_sessoes, hoje))}',
          for (final entrada in top.take(2))
            '${_nomeMateria(entrada.key)}: ${tempo.formatarDuracao(entrada.value)} na semana',
        ],
      ),
    );
  }
}
