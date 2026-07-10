/// Identidade visual do produto (mesma do prototipo e do painel).
library;

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

const verde = Color(0xFF17553F);
const dourado = Color(0xFFB8862F);
const papel = Color(0xFFFBFAF6);

ThemeData tema() {
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: verde,
      primary: verde,
      secondary: dourado,
      surface: papel,
    ),
    scaffoldBackgroundColor: papel,
  );
  return base.copyWith(
    textTheme: GoogleFonts.interTextTheme(base.textTheme).copyWith(
      headlineSmall: GoogleFonts.fraunces(
          fontWeight: FontWeight.w700, color: verde, fontSize: 24),
      titleLarge: GoogleFonts.fraunces(
          fontWeight: FontWeight.w600, color: verde, fontSize: 20),
      titleMedium: GoogleFonts.fraunces(
          fontWeight: FontWeight.w600, color: verde, fontSize: 17),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: verde,
      foregroundColor: Colors.white,
      titleTextStyle: GoogleFonts.fraunces(
          fontSize: 20, fontWeight: FontWeight.w600, color: Colors.white),
    ),
    cardTheme: const CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(12)),
        side: BorderSide(color: Color(0xFFE5E1D5)),
      ),
    ),
  );
}
