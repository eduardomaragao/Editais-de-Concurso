/// Cliente da rede de amigos (/api/social). Sobe so o RESUMO do progresso
/// (pontos, percentual) — a arvore marcada fica no aparelho.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api.dart';
import 'armazenamento.dart';

class Amigo {
  final String apelido;
  final String codigo;
  final int pontos;
  final double percentual;
  final int concluidos;
  Amigo(this.apelido, this.codigo, this.pontos, this.percentual, this.concluidos);
}

class SocialApi {
  static Uri _u(String caminho) => Uri.parse('${Api.base}/api/social$caminho');

  static Future<CredenciaisSociais> registrar(String apelido) async {
    final r = await http.post(_u('/usuarios'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'apelido': apelido}));
    if (r.statusCode != 201) throw Exception(_detalhe(r));
    final dados = jsonDecode(utf8.decode(r.bodyBytes)) as Map<String, dynamic>;
    final credenciais = CredenciaisSociais(
        dados['apelido'] as String, dados['codigo'] as String, dados['token'] as String);
    await credenciais.salvar();
    return credenciais;
  }

  static Future<String> adicionarAmigo(String codigo) async {
    final r = await http.post(_u('/amigos'),
        headers: await _cabecalhos(),
        body: jsonEncode({'codigo': codigo}));
    if (r.statusCode != 201) throw Exception(_detalhe(r));
    return (jsonDecode(utf8.decode(r.bodyBytes)) as Map)['apelido'] as String;
  }

  static Future<List<Amigo>> listarAmigos(String slugEdital) async {
    final r = await http.get(
        _u('/amigos').replace(queryParameters: {'edital': slugEdital}),
        headers: await _cabecalhos());
    if (r.statusCode != 200) throw Exception(_detalhe(r));
    return [
      for (final a in jsonDecode(utf8.decode(r.bodyBytes)) as List)
        Amigo(a['apelido'] as String, a['codigo'] as String, a['pontos'] as int,
            (a['percentual'] as num).toDouble(), a['concluidos'] as int)
    ];
  }

  static Future<void> enviarIncentivo(String codigo, String mensagem,
      {String? edital}) async {
    final r = await http.post(_u('/incentivos'),
        headers: await _cabecalhos(),
        body: jsonEncode({'codigo': codigo, 'mensagem': mensagem, 'edital': edital}));
    if (r.statusCode != 201) throw Exception(_detalhe(r));
  }

  static Future<List<Map<String, dynamic>>> buscarIncentivos() async {
    final r = await http.get(_u('/incentivos'), headers: await _cabecalhos());
    if (r.statusCode != 200) throw Exception(_detalhe(r));
    return List<Map<String, dynamic>>.from(
        jsonDecode(utf8.decode(r.bodyBytes)) as List);
  }

  /// Fire-and-forget: se nao tem conta ou a rede falhou, silencia — o
  /// progresso local e a fonte da verdade.
  static Future<void> sincronizarProgresso(String slugEdital,
      {required int pontos,
      required double percentual,
      required int concluidos}) async {
    try {
      final credenciais = await CredenciaisSociais.carregar();
      if (credenciais == null) return;
      await http.put(_u('/progresso'),
          headers: {
            'Content-Type': 'application/json',
            'X-Token': credenciais.token,
          },
          body: jsonEncode({
            'edital': slugEdital,
            'pontos': pontos,
            'percentual': percentual,
            'concluidos': concluidos,
          }));
    } catch (_) {
      // offline: sincroniza na proxima
    }
  }

  static Future<Map<String, String>> _cabecalhos() async {
    final credenciais = await CredenciaisSociais.carregar();
    if (credenciais == null) throw Exception('Crie seu perfil primeiro.');
    return {'Content-Type': 'application/json', 'X-Token': credenciais.token};
  }

  static String _detalhe(http.Response r) {
    try {
      return (jsonDecode(utf8.decode(r.bodyBytes)) as Map)['detail'] as String;
    } catch (_) {
      return 'Erro ${r.statusCode}';
    }
  }
}
