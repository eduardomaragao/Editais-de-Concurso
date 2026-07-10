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
}
