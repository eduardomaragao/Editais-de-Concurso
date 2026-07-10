/// Cliente da API do backend. So editais PUBLICADOS chegam aqui.
library;

import 'dart:convert';

import 'package:http/http.dart' as http;

import 'modelos.dart';

class Api {
  /// Em dev: painel local. Trocar via --dart-define=API_BASE=https://...
  static const base =
      String.fromEnvironment('API_BASE', defaultValue: 'http://localhost:8123');

  final http.Client _client;
  Api([http.Client? client]) : _client = client ?? http.Client();

  Future<List<Map<String, dynamic>>> listarEditais() async {
    final resposta = await _client.get(Uri.parse('$base/api/editais'));
    if (resposta.statusCode != 200) {
      throw Exception('API respondeu ${resposta.statusCode}');
    }
    return List<Map<String, dynamic>>.from(
        jsonDecode(utf8.decode(resposta.bodyBytes)) as List);
  }

  Future<Edital> obterEdital(String slug) async {
    final resposta = await _client.get(Uri.parse('$base/api/editais/$slug'));
    if (resposta.statusCode != 200) {
      throw Exception('Edital $slug indisponível (${resposta.statusCode})');
    }
    return Edital(
        jsonDecode(utf8.decode(resposta.bodyBytes)) as Map<String, dynamic>);
  }
}
