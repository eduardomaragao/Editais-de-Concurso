/// Acesso tipado ao documento do contrato (edital.schema.json).
/// O JSON e a fonte da verdade; aqui so ha getters de conveniencia.
library;

class Edital {
  final Map<String, dynamic> doc;
  Edital(this.doc);

  Map<String, dynamic> get info => doc['edital'] as Map<String, dynamic>;
  String get orgao => info['orgao'] as String;
  String get cargo => info['cargo'] as String;
  String get banca => info['banca'] as String? ?? '';
  String get numero => info['numero'] as String;
  String? get versaoArquivo => info['versao_arquivo'] as String?;
  bool? get radarDesatualizado => info['radar_desatualizado'] as bool?;
  String? get ultimaRetificacao => info['ultima_retificacao_publicada'] as String?;

  Map<String, dynamic> get corte =>
      (info['corte_conteudo'] as Map<String, dynamic>? ?? const {});

  List<Map<String, dynamic>> get cronograma =>
      List<Map<String, dynamic>>.from(doc['cronograma'] as List? ?? const []);

  List<Map<String, dynamic>> get conteudo =>
      List<Map<String, dynamic>>.from(doc['conteudo'] as List? ?? const []);

  List<Map<String, dynamic>> get fasesProva => List<Map<String, dynamic>>.from(
      (doc['dados_prova'] as Map<String, dynamic>?)?['fases'] as List? ?? const []);

  List<Map<String, dynamic>> get provasAnteriores =>
      List<Map<String, dynamic>>.from(doc['provas_anteriores'] as List? ?? const []);
}

/// No da arvore de conteudo, ja aninhado.
class No {
  final Map<String, dynamic> dados;
  final List<No> filhos;
  No(this.dados, this.filhos);

  String get id => dados['id'] as String;
  String get titulo => dados['titulo'] as String;
  String get nivel => dados['nivel'] as String;
  List<String> get fases => List<String>.from(dados['fases'] as List? ?? const []);

  /// Todos os ids da subarvore (incluindo o proprio).
  Iterable<String> get idsSubarvore sync* {
    yield id;
    for (final filho in filhos) {
      yield* filho.idsSubarvore;
    }
  }
}

/// Achatado (parent_id) -> aninhado, ordenado por `ordem`.
List<No> montarArvore(List<Map<String, dynamic>> nos) {
  final porPai = <String?, List<Map<String, dynamic>>>{};
  for (final no in nos) {
    porPai.putIfAbsent(no['parent_id'] as String?, () => []).add(no);
  }
  for (final grupo in porPai.values) {
    grupo.sort((a, b) => ((a['ordem'] as int?) ?? 0).compareTo((b['ordem'] as int?) ?? 0));
  }
  No montar(Map<String, dynamic> dados) => No(
        dados,
        (porPai[dados['id']] ?? const []).map(montar).toList(),
      );
  return (porPai[null] ?? const []).map(montar).toList();
}
