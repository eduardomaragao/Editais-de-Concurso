/// Compartilhar progresso nos Stories: renderiza um card 9:16 com a
/// identidade do produto, captura como PNG e abre o share sheet do sistema
/// (Instagram Stories aparece la). No navegador (dev), se o share nao for
/// suportado, avisa.
library;

import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:share_plus/share_plus.dart';

import 'tema.dart';

class CardStories extends StatelessWidget {
  final String titulo;
  final String destaque; // ex.: "42%"
  final String subtitulo;
  final double percentual;
  final List<String> itens;
  const CardStories({
    super.key,
    required this.titulo,
    required this.destaque,
    required this.subtitulo,
    required this.percentual,
    this.itens = const [],
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 324,
      height: 576, // 9:16 — vira 1080x1920 com pixelRatio 10/3
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF17553F), Color(0xFF0C3625)],
        ),
      ),
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('EDITAIS', style: TextStyle(
              color: dourado, fontSize: 13, fontWeight: FontWeight.w700,
              letterSpacing: 3)),
          const SizedBox(height: 40),
          Text(titulo, style: const TextStyle(
              color: Colors.white, fontSize: 24, fontWeight: FontWeight.w700,
              height: 1.2)),
          const SizedBox(height: 24),
          Text(destaque, style: const TextStyle(
              color: dourado, fontSize: 64, fontWeight: FontWeight.w800,
              height: 1)),
          const SizedBox(height: 8),
          Text(subtitulo, style: const TextStyle(
              color: Color(0xFFCFE0D8), fontSize: 15)),
          const SizedBox(height: 20),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: percentual.clamp(0.0, 1.0),
              minHeight: 12,
              backgroundColor: Colors.white.withValues(alpha: 0.15),
              color: dourado,
            ),
          ),
          const SizedBox(height: 24),
          for (final item in itens.take(5))
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('✓ ', style: TextStyle(color: dourado, fontSize: 14)),
                Expanded(
                  child: Text(item,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.white, fontSize: 13)),
                ),
              ]),
            ),
          const Spacer(),
          const Text('rumo à aprovação · eduardoaragao.com',
              style: TextStyle(color: Color(0xFF9DBBAD), fontSize: 11)),
        ],
      ),
    );
  }
}

/// Abre um preview do card com o botao de compartilhar.
Future<void> mostrarCardStories(BuildContext context, CardStories card) {
  final chave = GlobalKey();
  return showDialog(
    context: context,
    builder: (dialogContext) => Dialog(
      backgroundColor: Colors.transparent,
      child: SingleChildScrollView(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          RepaintBoundary(key: chave, child: card),
          const SizedBox(height: 12),
          FilledButton.icon(
            style: FilledButton.styleFrom(backgroundColor: dourado),
            icon: const Icon(Icons.ios_share),
            label: const Text('Compartilhar (Stories)'),
            onPressed: () => _compartilhar(dialogContext, chave),
          ),
        ]),
      ),
    ),
  );
}

Future<void> _compartilhar(BuildContext context, GlobalKey chave) async {
  try {
    final boundary =
        chave.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final imagem = await boundary.toImage(pixelRatio: 10 / 3); // 1080x1920
    final bytes = (await imagem.toByteData(format: ui.ImageByteFormat.png))!
        .buffer
        .asUint8List();
    await SharePlus.instance.share(ShareParams(files: [
      XFile.fromData(bytes, mimeType: 'image/png', name: 'meu-estudo.png'),
    ]));
  } catch (erro) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Compartilhamento indisponível aqui ($erro). '
              'No celular, o share abre direto no Instagram.')));
    }
  }
}
