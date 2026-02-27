import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFF2563EB);    // Blue 600
  static const Color secondary = Color(0xFF7C3AED);  // Violet 600
  static const Color success = Color(0xFF16A34A);    // Green 600
  static const Color error = Color(0xFFDC2626);      // Red 600

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: primary),
    fontFamily: 'Inter',
  );

  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primary,
      brightness: Brightness.dark,
    ),
    fontFamily: 'Inter',
  );
}
