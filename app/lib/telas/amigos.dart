import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../armazenamento.dart';
import '../social_api.dart';
import '../tema.dart';

const mensagensRapidas = [
  'Vai que dá! 🚀',
  'Não para agora! 🔥',
  'Tô de olho no seu progresso 👀',
  'Bora revisar junto? 📚',
  'Falta pouco, segura firme! 💪',
];

/// Amigos: ranking de pontos no edital, codigo para adicionar e incentivos.
class AmigosPage extends StatefulWidget {
  final String slug;
  const AmigosPage({super.key, required this.slug});

  @override
  State<AmigosPage> createState() => _AmigosPageState();
}

class _AmigosPageState extends State<AmigosPage> {
  CredenciaisSociais? _credenciais;
  List<Amigo> _amigos = [];
  bool _carregado = false;
  String? _erro;

  @override
  void initState() {
    super.initState();
    _carregar();
  }

  Future<void> _carregar() async {
    _credenciais = await CredenciaisSociais.carregar();
    if (_credenciais != null) {
      try {
        _amigos = await SocialApi.listarAmigos(widget.slug);
        _erro = null;
      } catch (erro) {
        _erro = '$erro';
      }
    }
    if (mounted) setState(() => _carregado = true);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Amigos')),
      body: !_carregado
          ? const Center(child: CircularProgressIndicator())
          : _credenciais == null
              ? _telaRegistro()
              : _telaAmigos(),
    );
  }

  // --- registro (primeira vez) ---------------------------------------------

  Widget _telaRegistro() {
    final apelido = TextEditingController();
    return ListView(padding: const EdgeInsets.all(16), children: [
      Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Estudar junto rende mais',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 6),
            const Text('Crie seu perfil para comparar progresso com amigos e '
                'trocar incentivos. Só o resumo (pontos e %) é compartilhado — '
                'o que você marcou fica no seu aparelho.'),
            const SizedBox(height: 12),
            TextField(
                controller: apelido,
                decoration: const InputDecoration(
                    labelText: 'Seu apelido', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () async {
                try {
                  await SocialApi.registrar(apelido.text.trim());
                  await _carregar();
                } catch (erro) {
                  if (!mounted) return;
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text('$erro')));
                }
              },
              child: const Text('Criar perfil'),
            ),
          ]),
        ),
      ),
    ]);
  }

  // --- lista de amigos -------------------------------------------------------

  Widget _telaAmigos() {
    return RefreshIndicator(
      onRefresh: _carregar,
      child: ListView(padding: const EdgeInsets.all(12), children: [
        Card(
          color: const Color(0xFFF6F1E4),
          child: ListTile(
            title: Text('Seu código de amigo: ${_credenciais!.codigo}',
                style: const TextStyle(fontWeight: FontWeight.w700)),
            subtitle: const Text('Passe para um amigo adicionar você'),
            trailing: IconButton(
              icon: const Icon(Icons.copy),
              onPressed: () async {
                await Clipboard.setData(
                    ClipboardData(text: _credenciais!.codigo));
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Código copiado!')));
                }
              },
            ),
          ),
        ),
        Card(
          child: ListTile(
            leading: const Icon(Icons.person_add, color: verde),
            title: const Text('Adicionar amigo pelo código'),
            onTap: _adicionarAmigo,
          ),
        ),
        const SizedBox(height: 8),
        if (_erro != null)
          Card(
              child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('Não deu para carregar: $_erro'))),
        if (_amigos.isEmpty && _erro == null)
          const Card(
              child: Padding(
                  padding: EdgeInsets.all(14),
                  child: Text('Nenhum amigo ainda — troque códigos e '
                      'transformem o edital numa maratona em grupo.'))),
        for (var i = 0; i < _amigos.length; i++) _cardAmigo(i),
      ]),
    );
  }

  Widget _cardAmigo(int posicao) {
    final amigo = _amigos[posicao];
    final medalha = switch (posicao) {
      0 => '🥇',
      1 => '🥈',
      2 => '🥉',
      _ => '  ',
    };
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text(medalha, style: const TextStyle(fontSize: 20)),
            const SizedBox(width: 6),
            Expanded(
                child: Text(amigo.apelido,
                    style: const TextStyle(
                        fontWeight: FontWeight.w700, fontSize: 15))),
            Text('${amigo.pontos} pts',
                style: const TextStyle(color: dourado, fontWeight: FontWeight.w700)),
            IconButton(
              tooltip: 'Mandar incentivo',
              icon: const Icon(Icons.local_fire_department, color: dourado),
              onPressed: () => _mandarIncentivo(amigo),
            ),
          ]),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: amigo.percentual,
              minHeight: 8,
              backgroundColor: const Color(0xFFEEE8DA),
              color: verde,
            ),
          ),
          const SizedBox(height: 4),
          Text(
              '${(amigo.percentual * 100).round()}% do edital · '
              '${amigo.concluidos} itens',
              style: const TextStyle(fontSize: 11, color: Color(0xFF8A8574))),
        ]),
      ),
    );
  }

  Future<void> _adicionarAmigo() async {
    final codigo = TextEditingController();
    final confirmado = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Adicionar amigo'),
        content: TextField(
            controller: codigo,
            textCapitalization: TextCapitalization.characters,
            decoration: const InputDecoration(
                labelText: 'Código do amigo (ex.: A7KM2Q)')),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(false),
              child: const Text('Cancelar')),
          FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(true),
              child: const Text('Adicionar')),
        ],
      ),
    );
    if (confirmado != true) return;
    try {
      final apelido = await SocialApi.adicionarAmigo(codigo.text.trim());
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$apelido agora é seu amigo! 🎉')));
      }
      await _carregar();
    } catch (erro) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$erro')));
      }
    }
  }

  Future<void> _mandarIncentivo(Amigo amigo) async {
    final personalizada = TextEditingController();
    final mensagem = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      builder: (sheetContext) => Padding(
        padding: EdgeInsets.only(
            left: 16, right: 16, top: 16,
            bottom: MediaQuery.of(sheetContext).viewInsets.bottom + 16),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Text('Incentivo para ${amigo.apelido}',
              style: Theme.of(sheetContext).textTheme.titleMedium),
          const SizedBox(height: 8),
          for (final rapida in mensagensRapidas)
            ListTile(
                dense: true,
                title: Text(rapida),
                onTap: () => Navigator.of(sheetContext).pop(rapida)),
          TextField(
            controller: personalizada,
            decoration: const InputDecoration(labelText: 'Ou escreva a sua'),
            onSubmitted: (texto) => Navigator.of(sheetContext).pop(texto),
          ),
        ]),
      ),
    );
    if (mensagem == null || mensagem.trim().isEmpty) return;
    try {
      await SocialApi.enviarIncentivo(amigo.codigo, mensagem.trim(),
          edital: widget.slug);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Incentivo enviado para ${amigo.apelido}! 💌')));
      }
    } catch (erro) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$erro')));
      }
    }
  }
}
