import 'package:flutter/material.dart';

import 'telas/home.dart';
import 'tema.dart';

void main() {
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
