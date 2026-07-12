/// Dados do USUARIO, locais ao aparelho: progresso de estudo (ids de nos
/// concluidos) e locais de prova (CEP + sala), por edital.
library;

import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

class Armazenamento {
  final String slug;
  Armazenamento(this.slug);

  String get _chaveProgresso => 'progresso:$slug';
  String get _chaveLocais => 'locais:$slug';

  Future<Set<String>> carregarProgresso() async {
    final prefs = await SharedPreferences.getInstance();
    return (prefs.getStringList(_chaveProgresso) ?? const []).toSet();
  }

  Future<void> salvarProgresso(Set<String> concluidos) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_chaveProgresso, concluidos.toList()..sort());
  }

  Future<List<Map<String, dynamic>>> carregarLocais() async {
    final prefs = await SharedPreferences.getInstance();
    final bruto = prefs.getString(_chaveLocais);
    if (bruto == null) return [];
    return List<Map<String, dynamic>>.from(jsonDecode(bruto) as List);
  }

  Future<void> salvarLocais(List<Map<String, dynamic>> locais) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_chaveLocais, jsonEncode(locais));
  }

  // --- diario de estudo: {"2026-07-12": [ids concluidos naquele dia]} ------

  String get _chaveDiario => 'diario:$slug';

  Future<Map<String, List<String>>> carregarDiario() async {
    final prefs = await SharedPreferences.getInstance();
    final bruto = prefs.getString(_chaveDiario);
    if (bruto == null) return {};
    return (jsonDecode(bruto) as Map<String, dynamic>)
        .map((dia, ids) => MapEntry(dia, List<String>.from(ids as List)));
  }

  /// Registra no diario de hoje o que foi marcado/desmarcado agora.
  /// Desmarcar so apaga do dia de hoje — o que foi estudado em dias
  /// anteriores e historia, fica.
  Future<Map<String, List<String>>> registrarNoDiario(
      {required Iterable<String> marcados,
      required Iterable<String> desmarcados}) async {
    final diario = await carregarDiario();
    final hoje = DateTime.now();
    final chave = '${hoje.year.toString().padLeft(4, '0')}-'
        '${hoje.month.toString().padLeft(2, '0')}-'
        '${hoje.day.toString().padLeft(2, '0')}';
    final deHoje = {...(diario[chave] ?? const <String>[])};
    deHoje.addAll(marcados);
    deHoje.removeAll(desmarcados.toSet());
    diario[chave] = deHoje.toList()..sort();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_chaveDiario, jsonEncode(diario));
    return diario;
  }
}

/// Credenciais da rede de amigos (globais, nao por edital).
class CredenciaisSociais {
  final String apelido;
  final String codigo;
  final String token;
  CredenciaisSociais(this.apelido, this.codigo, this.token);

  static Future<CredenciaisSociais?> carregar() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('social:token');
    if (token == null) return null;
    return CredenciaisSociais(
      prefs.getString('social:apelido') ?? '',
      prefs.getString('social:codigo') ?? '',
      token,
    );
  }

  Future<void> salvar() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('social:apelido', apelido);
    await prefs.setString('social:codigo', codigo);
    await prefs.setString('social:token', token);
  }
}
