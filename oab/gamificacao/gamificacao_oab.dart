/// Motor de gamificacao do app de questoes da OAB.
///
/// Sem nenhuma dependencia de Flutter — e Dart puro de proposito, para poder
/// entrar em qualquer camada do app (ou virar teste, ou virar funcao de API).
///
/// Principio, o mesmo do app de editais: insignia e ponto sao **funcao do
/// historico de respostas**, recalculados do zero a cada chamada, nunca
/// acumulados. Assim o placar nao tem como divergir do estudo real.
///
/// A unica excecao e o **domino de materia**: como ele mede acerto numa janela
/// movel (as ultimas N questoes daquela materia), o criterio pode deixar de
/// valer depois de valer. Insignia conquistada nao pode cair, entao o app
/// guarda os ids ja conquistados e passa em [permanentes] — a catraca fica
/// explicita aqui, em vez de escondida num contador que acumula sozinho.
///
/// Espelha o preview.html deste diretorio. Mudou a regra aqui, muda la.
library;

// ---------------------------------------------------------------- materias

class Materia {
  final String id;
  final String nome;
  final String curto;
  const Materia(this.id, this.nome, this.curto);
}

/// As 17 disciplinas da 1a fase do Exame de Ordem.
const materiasOab = <Materia>[
  Materia('etica', 'Ética e Estatuto da OAB', 'Ética'),
  Materia('filosofia', 'Filosofia do Direito', 'Filosofia'),
  Materia('constitucional', 'Direito Constitucional', 'Constitucional'),
  Materia('humanos', 'Direitos Humanos', 'Humanos'),
  Materia('internacional', 'Direito Internacional', 'Internacional'),
  Materia('tributario', 'Direito Tributário', 'Tributário'),
  Materia('administrativo', 'Direito Administrativo', 'Administrativo'),
  Materia('ambiental', 'Direito Ambiental', 'Ambiental'),
  Materia('civil', 'Direito Civil', 'Civil'),
  Materia('eca', 'ECA', 'ECA'),
  Materia('consumidor', 'Direito do Consumidor', 'Consumidor'),
  Materia('empresarial', 'Direito Empresarial', 'Empresarial'),
  Materia('processocivil', 'Direito Processual Civil', 'Proc. Civil'),
  Materia('penal', 'Direito Penal', 'Penal'),
  Materia('processopenal', 'Direito Processual Penal', 'Proc. Penal'),
  Materia('trabalho', 'Direito do Trabalho', 'Trabalho'),
  Materia('processotrabalho', 'Direito Processual do Trabalho', 'Proc. Trabalho'),
];

// ------------------------------------------------------------- entrada

/// Historico do candidato numa materia.
///
/// [recentes] guarda as ultimas respostas em ordem (a mais antiga primeiro,
/// a mais nova por ultimo), true = acerto. Basta manter as ultimas
/// [janelaMaxima] — e o que a maior meta de Catedra pode pedir.
class HistoricoMateria {
  final int respondidas;
  final int acertos;
  final List<bool> recentes;

  const HistoricoMateria({
    required this.respondidas,
    required this.acertos,
    this.recentes = const [],
  });

  /// Acertos entre as ultimas [n] respostas. Devolve null quando ainda nao ha
  /// [n] respostas registradas — nao da para julgar uma janela incompleta.
  int? acertosNaJanela(int n) {
    if (n <= 0 || recentes.length < n) return null;
    var certos = 0;
    for (var i = recentes.length - n; i < recentes.length; i++) {
      if (recentes[i]) certos++;
    }
    return certos;
  }
}

/// Quantas respostas por materia o app precisa guardar para o calculo de
/// dominio funcionar (a maior meta possivel e o teto da Catedra).
const janelaMaxima = 300;

class EstatisticasOab {
  /// Totais da vida no app.
  final int respondidas;
  final int acertos;

  /// Recorde de questoes seguidas numa mesma sessao (nao zera nunca).
  final int maiorMaratona;

  /// Recorde de acertos consecutivos, sem erro no meio (nao zera nunca).
  final int melhorPontaria;

  /// Historico por materia, indexado pelo id de [materiasOab].
  final Map<String, HistoricoMateria> porMateria;

  /// Ids das insignias secretas que o app ja disparou. Elas dependem de
  /// eventos (hora do dia, revisao de erro, simulado) que so o app observa.
  final Set<String> segredos;

  const EstatisticasOab({
    this.respondidas = 0,
    this.acertos = 0,
    this.maiorMaratona = 0,
    this.melhorPontaria = 0,
    this.porMateria = const {},
    this.segredos = const {},
  });

  double get taxa => respondidas == 0 ? 0 : acertos / respondidas;
}

// -------------------------------------------------------------- catalogo

enum CategoriaOab { carteira, volume, acertos, maratona, pontaria, dominio, secreta }

class InsigniaOab {
  final String id;
  final CategoriaOab categoria;
  final String titulo;
  final String criterio;

  /// Nome do glifo desenhado (ver preview.html). O app resolve para o asset.
  final String glifo;

  /// 1 bronze · 2 prata · 3 ouro · 4 esmalte · 5 apice.
  final int tier;

  /// Posicao na escada, quando ela existe (1 = primeiro degrau).
  final int? degrau;

  final num meta;
  final num valor;
  final bool conquistada;
  final int pontos;

  const InsigniaOab({
    required this.id,
    required this.categoria,
    required this.titulo,
    required this.criterio,
    required this.glifo,
    required this.tier,
    required this.meta,
    required this.valor,
    required this.conquistada,
    required this.pontos,
    this.degrau,
  });

  /// 0..1 — quanto falta para o proximo degrau.
  double get progresso => meta <= 0 ? 1 : (valor / meta).clamp(0, 1).toDouble();

  num get falta => conquistada ? 0 : (meta - valor);
}

class TierDominio {
  final String id;
  final String nome;
  final double fatiaDoBanco;
  final int minimo;
  final int maximo;
  final double acertoExigido;
  final int tier;
  final String glifo;
  const TierDominio(this.id, this.nome, this.fatiaDoBanco, this.minimo,
      this.maximo, this.acertoExigido, this.tier, this.glifo);
}

const tiersDominio = <TierDominio>[
  TierDominio('dominio', 'Domínio', .10, 20, 100, .80, 3, 'balanca'),
  TierDominio('excelencia', 'Excelência', .20, 40, 180, .85, 4, 'laurel'),
  TierDominio('catedra', 'Cátedra', .35, 70, 300, .90, 5, 'coluna'),
];

/// Quantas questoes daquela materia o candidato precisa fazer para valer o
/// tier — sai do tamanho do banco, com piso e teto para o calculo nao virar
/// piada em materia pequena nem penitencia em materia gigante.
int metaDominio(int questoesNoBanco, TierDominio t) {
  final bruto = (questoesNoBanco * t.fatiaDoBanco).round();
  return bruto.clamp(t.minimo, t.maximo);
}

/// Escadas: (meta, titulo).
const escadaVolume = <(int, String)>[
  (10, 'Primeira Audiência'), (25, 'Autuação'), (50, 'Distribuição'),
  (100, 'Petição Inicial'), (175, 'Citação'), (250, 'Contestação'),
  (350, 'Réplica'), (500, 'Saneamento'), (700, 'Instrução'),
  (900, 'Alegações Finais'), (1100, 'Sentença'), (1400, 'Apelação'),
  (1700, 'Contrarrazões'), (2000, 'Acórdão'), (2400, 'Embargos de Declaração'),
  (2800, 'Agravo Interno'), (3200, 'Recurso Especial'),
  (3700, 'Recurso Extraordinário'), (4200, 'Repercussão Geral'), (4800, 'Súmula'),
  (5500, 'Trânsito em Julgado'), (6500, 'Cumprimento de Sentença'),
  (7500, 'Precatório'), (8500, 'Jurisprudência Firmada'), (10000, 'Tribuna'),
  (12000, 'Sustentação Oral'), (14000, 'Banca Examinadora'), (17000, 'Cátedra Livre'),
  (20000, 'Doutrina'), (25000, 'Vade Mecum Vivo'),
];

const escadaAcertos = <(int, String)>[
  (5, 'Primeira Vitória'), (25, 'Liminar Deferida'), (50, 'Tutela de Urgência'),
  (100, 'Sentença Procedente'), (200, 'Provimento'), (350, 'Precedente'),
  (500, 'Segunda Instância'), (700, 'Decisão Unânime'), (1000, 'Milhar Limpo'),
  (1300, 'Tese Vencedora'), (1600, 'Jurisprudência Reiterada'),
  (2000, 'Súmula Pessoal'), (2500, 'Repetitivo'), (3000, 'Vinculante'),
  (3600, 'Tribuna de Ouro'), (4200, 'Placar Aberto'), (5000, 'Cinco Mil Razões'),
  (6000, 'Banca Vencida'), (7000, 'Excelência Reconhecida'), (8500, 'Ordem Honorífica'),
  (10000, 'Mestre do Exame'), (12000, 'Referência'), (14000, 'Grande Precedente'),
  (17000, 'Legado'), (20000, 'Imortal do Exame'),
];

const escadaMaratona = <(int, String)>[
  (5, 'Pauta Aberta'), (10, 'Sessão Instalada'), (15, 'Pauta do Dia'),
  (20, 'Sustentação em Curso'), (30, 'Vista Concedida'), (40, 'Sessão Prorrogada'),
  (50, 'Meia Centena de Fôlego'), (75, 'Plenário Cheio'),
  (100, 'Sessão Extraordinária'), (150, 'Vigília Processual'),
  (200, 'Resistência de Banca'), (300, 'Maratona da Ordem'),
];

const escadaPontaria = <(int, String)>[
  (3, 'Fundamento Sólido'), (5, 'Tese Coerente'), (8, 'Sem Reparos'),
  (10, 'Sem Divergência'), (15, 'Sem Contrarrazões'), (20, 'Placar 20 a 0'),
  (25, 'Voto Condutor'), (30, 'Precedente Firme'), (40, 'Súmula Impecável'),
  (50, 'Cinquenta sem Erro'), (75, 'Infalível'), (100, 'Centena Perfeita'),
];

/// Secretas: (id, titulo, descricao, glifo, tier). Quem dispara e o app —
/// aqui elas so viram insignia quando o id chega em [EstatisticasOab.segredos].
const secretasOab = <(String, String, String, String, int)>[
  ('primario', 'Réu Primário', 'Acertou as 10 primeiras questões da vida no app.', 'escudo', 2),
  ('vigilia', 'Vigília do Plantonista', '20 questões respondidas entre 0h e 5h.', 'ampulheta', 2),
  ('orvalho', 'Antes do Fórum Abrir', '20 questões respondidas antes das 7h.', 'tocha', 2),
  ('exofficio', 'Ex Officio', 'Ao menos uma questão de cada uma das 17 matérias no mesmo dia.', 'selo', 4),
  ('limpa', 'Prova Limpa', 'Simulado de 80 questões com 90% ou mais de acerto.', 'alvo', 4),
  ('recesso', 'Sem Recesso', '100 questões entre sábado e domingo do mesmo fim de semana.', 'livro', 3),
  ('virada', 'Reforma da Sentença', 'Errou e, na revisão, acertou a mesma questão — 50 vezes.', 'martelo', 3),
  ('venia', 'Data Venia', 'Errou 10 seguidas e, no mesmo dia, acertou 10 seguidas.', 'pena', 5),
];

/// As 8 pecas da carteira, em ordem. Uma peca so entra depois da anterior.
class PecaCarteira {
  final int numero;
  final String titulo;
  final String peca;
  final String criterio;
  final bool aberta;
  const PecaCarteira(this.numero, this.titulo, this.peca, this.criterio, this.aberta);
}

const _pecas = <(String, String, String)>[
  ('Autos Abertos', 'O couro', 'A primeira questão respondida.'),
  ('Bacharel', 'A moldura em ouro', '250 questões respondidas.'),
  ('Retrato nos Autos', 'A fotografia', '1.000 questões com 60% de acerto ou mais.'),
  ('Nome na Ordem', 'O nome', '3 matérias dominadas.'),
  ('Número de Inscrição', 'O número', '2.500 questões com 65% de acerto ou mais.'),
  ('Seccional', 'A seccional', '8 matérias dominadas.'),
  ('Juramento', 'A assinatura', '5.000 questões, 70% de acerto e uma maratona de 100.'),
  ('Carteira Vermelha', 'O selo e o brasão',
      'As 17 matérias dominadas e 10.000 questões respondidas.'),
];

/// Pontos por raridade — index = tier.
const pontosPorTier = <int>[0, 60, 180, 500, 1400, 3500];

const _glifosEscada = <CategoriaOab, List<String>>{
  CategoriaOab.volume: ['pena', 'livro', 'balanca', 'coluna', 'coroa'],
  CategoriaOab.acertos: ['alvo', 'selo', 'laurel', 'escudo', 'coroa'],
  CategoriaOab.maratona: ['ampulheta', 'tocha', 'coluna', 'escudo', 'laurel'],
  CategoriaOab.pontaria: ['alvo', 'alvo', 'selo', 'laurel', 'coroa'],
};

int _tierDoDegrau(int i, int total) => ((i * 5) ~/ total + 1).clamp(1, 5);

// ------------------------------------------------------------- resultado

class ResultadoOab {
  final List<InsigniaOab> insignias;
  final List<PecaCarteira> carteira;
  final int pontos;

  /// Ids que passaram a valer nesta chamada e precisam ser gravados para nao
  /// caírem depois (so importa para as de dominio, que usam janela movel).
  final Set<String> paraGuardar;

  const ResultadoOab(this.insignias, this.carteira, this.pontos, this.paraGuardar);

  List<InsigniaOab> get conquistadas =>
      insignias.where((i) => i.conquistada).toList();

  List<InsigniaOab> daCategoria(CategoriaOab c) =>
      insignias.where((i) => i.categoria == c).toList();

  int get pecasAbertas => carteira.where((p) => p.aberta).length;

  PecaCarteira? get ultimaPeca {
    PecaCarteira? ultima;
    for (final p in carteira) {
      if (p.aberta) ultima = p;
    }
    return ultima;
  }

  /// Proxima insignia a cair numa categoria — o que a tela mostra como "faltam N".
  InsigniaOab? proxima(CategoriaOab c) {
    for (final i in insignias) {
      if (i.categoria == c && !i.conquistada) return i;
    }
    return null;
  }

  int get materiasDominadas => materiasOab
      .where((m) => insignias.any((i) =>
          i.categoria == CategoriaOab.dominio &&
          i.conquistada &&
          i.id == 'dominio-${m.id}'))
      .length;
}

// -------------------------------------------------------------- calculo

String _mil(num n) {
  final s = n.round().toString();
  final buf = StringBuffer();
  for (var i = 0; i < s.length; i++) {
    if (i > 0 && (s.length - i) % 3 == 0) buf.write('.');
    buf.write(s[i]);
  }
  return buf.toString();
}

/// Recalcula tudo. [banco] = quantas questoes existem hoje em cada materia
/// (id de [materiasOab] -> total). [permanentes] = ids ja conquistados antes,
/// que nao podem cair.
ResultadoOab calcularOab(
  EstatisticasOab e,
  Map<String, int> banco, {
  Set<String> permanentes = const {},
}) {
  final insignias = <InsigniaOab>[];
  final guardar = <String>{};

  void escada(CategoriaOab cat, List<(int, String)> tabela, int valor,
      String Function(int) criterio) {
    for (var i = 0; i < tabela.length; i++) {
      final (meta, titulo) = tabela[i];
      final tier = _tierDoDegrau(i, tabela.length);
      insignias.add(InsigniaOab(
        id: '${cat.name}-$meta',
        categoria: cat,
        titulo: titulo,
        criterio: criterio(meta),
        glifo: _glifosEscada[cat]![tier - 1],
        tier: tier,
        degrau: i + 1,
        meta: meta,
        valor: valor,
        conquistada: valor >= meta,
        pontos: pontosPorTier[tier],
      ));
    }
  }

  escada(CategoriaOab.volume, escadaVolume, e.respondidas,
      (m) => '${_mil(m)} respondidas');
  escada(CategoriaOab.acertos, escadaAcertos, e.acertos,
      (m) => '${_mil(m)} acertos');
  escada(CategoriaOab.maratona, escadaMaratona, e.maiorMaratona,
      (m) => '${_mil(m)} numa sessão');
  escada(CategoriaOab.pontaria, escadaPontaria, e.melhorPontaria,
      (m) => '${_mil(m)} seguidas');

  // --- dominio por materia: janela movel + catraca
  var dominadas = 0;
  for (final m in materiasOab) {
    final h = e.porMateria[m.id] ?? const HistoricoMateria(respondidas: 0, acertos: 0);
    final total = banco[m.id] ?? 0;
    var dominou = false;
    for (final t in tiersDominio) {
      final meta = metaDominio(total, t);
      final id = '${t.id}-${m.id}';
      final naJanela = h.acertosNaJanela(meta);
      final agora = h.respondidas >= meta &&
          naJanela != null &&
          naJanela >= (meta * t.acertoExigido).ceil();
      final valeu = agora || permanentes.contains(id);
      if (agora) guardar.add(id);
      if (valeu && t.id == 'dominio') dominou = true;
      insignias.add(InsigniaOab(
        id: id,
        categoria: CategoriaOab.dominio,
        titulo: '${t.nome} · ${m.curto}',
        criterio:
            '${_mil(meta)} questões de ${m.nome} com ${(t.acertoExigido * 100).round()}% de acerto',
        glifo: t.glifo,
        tier: t.tier,
        meta: meta,
        valor: h.respondidas.clamp(0, meta),
        conquistada: valeu,
        pontos: pontosPorTier[t.tier],
      ));
    }
    if (dominou) dominadas++;
  }

  // --- secretas
  for (final (id, titulo, desc, glifo, tier) in secretasOab) {
    final valeu = e.segredos.contains(id);
    insignias.add(InsigniaOab(
      id: 'secreta-$id',
      categoria: CategoriaOab.secreta,
      titulo: titulo,
      criterio: desc,
      glifo: glifo,
      tier: tier,
      meta: 1,
      valor: valeu ? 1 : 0,
      conquistada: valeu,
      pontos: pontosPorTier[tier],
    ));
  }

  // --- carteira: sequencial, uma peca so entra depois da anterior
  final criterios = <bool>[
    e.respondidas >= 1,
    e.respondidas >= 250,
    e.respondidas >= 1000 && e.taxa >= .60,
    dominadas >= 3,
    e.respondidas >= 2500 && e.taxa >= .65,
    dominadas >= 8,
    e.respondidas >= 5000 && e.taxa >= .70 && e.maiorMaratona >= 100,
    dominadas >= materiasOab.length && e.respondidas >= 10000,
  ];
  var corte = criterios.indexOf(false);
  if (corte < 0) corte = criterios.length;

  final carteira = <PecaCarteira>[];
  for (var i = 0; i < _pecas.length; i++) {
    final (titulo, peca, criterio) = _pecas[i];
    final aberta = i < corte;
    carteira.add(PecaCarteira(i + 1, titulo, peca, criterio, aberta));
    final tier = i < 2 ? 2 : (i < 4 ? 3 : (i < 6 ? 4 : 5));
    insignias.add(InsigniaOab(
      id: 'carteira-${i + 1}',
      categoria: CategoriaOab.carteira,
      titulo: titulo,
      criterio: criterio,
      glifo: 'selo',
      tier: tier,
      degrau: i + 1,
      meta: 1,
      valor: aberta ? 1 : 0,
      conquistada: aberta,
      // a trilha principal vale dobrado
      pontos: pontosPorTier[tier] * 2,
    ));
  }

  final pontos = e.acertos * 10 +
      (e.respondidas - e.acertos) * 2 +
      insignias.where((i) => i.conquistada).fold(0, (s, i) => s + i.pontos);

  return ResultadoOab(insignias, carteira, pontos, guardar);
}
