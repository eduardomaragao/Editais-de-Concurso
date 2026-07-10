import 'package:flutter/material.dart';

import '../api.dart';
import 'edital_hub.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _api = Api();
  late Future<List<Map<String, dynamic>>> _editais;

  @override
  void initState() {
    super.initState();
    _editais = _api.listarEditais();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Meus editais')),
      body: FutureBuilder(
        future: _editais,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(
                child: Padding(
              padding: const EdgeInsets.all(24),
              child: Text('Não foi possível carregar os editais.\n${snapshot.error}',
                  textAlign: TextAlign.center),
            ));
          }
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          final editais = snapshot.data!;
          if (editais.isEmpty) {
            return const Center(child: Text('Nenhum edital publicado ainda.'));
          }
          return ListView(
            padding: const EdgeInsets.all(12),
            children: [
              for (final e in editais)
                Card(
                  child: ListTile(
                    title: Text('${e['orgao']} — ${e['cargo']}',
                        style: Theme.of(context).textTheme.titleMedium),
                    subtitle: Text('Edital ${e['numero']}'),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(MaterialPageRoute(
                        builder: (_) => EditalHubPage(slug: e['slug'] as String))),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}
