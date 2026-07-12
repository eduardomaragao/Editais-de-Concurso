import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';

import 'telas/home.dart';
import 'tema.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('pt_BR'); // calendario em portugues
  runApp(const EditaisApp());
}

class EditaisApp extends StatelessWidget {
  const EditaisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Editais',
      theme: tema(),
      debugShowCheckedModeBanner: false,
      home: const HomePage(),
    );
  }
}
