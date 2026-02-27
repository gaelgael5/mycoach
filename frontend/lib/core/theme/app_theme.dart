import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Palette issue du design system JSX MyCoach v4.
/// Toutes les couleurs sont définies ici — zéro couleur codée en dur ailleurs.
class AppColors {
  AppColors._();

  // ── Accent (orange brand) ────────────────────────────────────────────────
  static const Color accent      = Color(0xFFFF4D00); // Couleur principale brand
  static const Color accentLight = Color(0xFFFF6B2E); // Gradient end / variante claire
  static const Color accentGlow  = Color(0x40FF4D00); // rgba(255,77,0,0.25)

  // ── Fond ────────────────────────────────────────────────────────────────
  static const Color bgDark      = Color(0xFF0A0A0F); // fond principal dark
  static const Color bgCard      = Color(0xFF14141F); // cartes
  static const Color bgInput     = Color(0xFF1A1A2A); // inputs
  static const Color bgElement   = Color(0xFF1E1E30); // bottom nav, éléments

  // ── Sémantiques ─────────────────────────────────────────────────────────
  static const Color green       = Color(0xFF00E676); // succès / disponible
  static const Color greenSurface= Color(0x2600E676); // rgba(0,230,118,0.15)
  static const Color yellow      = Color(0xFFFFD600); // record / alerte
  static const Color yellowSurface= Color(0x1FFFD600);// rgba(255,214,0,0.12)
  static const Color red         = Color(0xFFFF3D57); // erreur / complet
  static const Color blue        = Color(0xFF4D8DFF); // certifié / info
  static const Color blueSurface = Color(0x264D8DFF); // rgba(77,141,255,0.15)

  // ── Gris (échelle) ───────────────────────────────────────────────────────
  static const Color white       = Color(0xFFFAFAFA);
  static const Color grey1       = Color(0xFFE0E0E8);
  static const Color grey3       = Color(0xFF9898A8);
  static const Color grey5       = Color(0xFF5A5A6E);
  static const Color grey7       = Color(0xFF2A2A3A);

  // ── Couleur light (non utilisée pour l'instant, app dark-first) ─────────
  static const Color bgLight     = Color(0xFFF5F5F7);
  static const Color bgCardLight = Color(0xFFFFFFFF);
}

/// Styles de texte partagés (Outfit + JetBrains Mono pour les timers).
class AppTextStyles {
  AppTextStyles._();

  static TextStyle outfit(double size, FontWeight weight, Color color) =>
      GoogleFonts.outfit(fontSize: size, fontWeight: weight, color: color);

  static TextStyle mono(double size, FontWeight weight, Color color) =>
      GoogleFonts.jetBrainsMono(fontSize: size, fontWeight: weight, color: color);

  // ── Titres ───────────────────────────────────────────────────────────────
  static TextStyle headline1(Color c) => outfit(28, FontWeight.w800, c);
  static TextStyle headline2(Color c) => outfit(24, FontWeight.w800, c);
  static TextStyle headline3(Color c) => outfit(22, FontWeight.w800, c);
  static TextStyle headline4(Color c) => outfit(18, FontWeight.w700, c);

  // ── Corps ────────────────────────────────────────────────────────────────
  static TextStyle body1(Color c) => outfit(15, FontWeight.w400, c);
  static TextStyle body2(Color c) => outfit(14, FontWeight.w400, c);
  static TextStyle caption(Color c) => outfit(12, FontWeight.w400, c);

  // ── Labels (uppercase) ───────────────────────────────────────────────────
  static TextStyle label(Color c) => outfit(13, FontWeight.w600, c).copyWith(
    letterSpacing: 0.5,
    decoration: TextDecoration.none,
  );

  // ── Boutons ──────────────────────────────────────────────────────────────
  static TextStyle buttonPrimary()  => outfit(16, FontWeight.w700, AppColors.white);
  static TextStyle buttonSecondary()=> outfit(15, FontWeight.w600, AppColors.grey1);
  static TextStyle buttonGhost()    => outfit(14, FontWeight.w600, AppColors.accent);

  // ── Monospace (chrono, timer) ─────────────────────────────────────────────
  static TextStyle timer(Color c) => mono(48, FontWeight.w900, c);
  static TextStyle timerSmall(Color c) => mono(24, FontWeight.w900, c);
}

/// Rayons des bordures — alignés sur le JSX.
class AppRadius {
  AppRadius._();
  static const double card    = 14.0; // T.r
  static const double input   = 10.0; // T.rs
  static const double pill    = 50.0; // chips / badges
  static const double avatar  = 16.0; // avatars carrés
  static const double circle  = 999.0;
}

/// Ombres portées.
class AppShadows {
  AppShadows._();

  static List<BoxShadow> accent = [
    BoxShadow(
      color: AppColors.accentGlow,
      blurRadius: 20,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> card = [
    BoxShadow(
      color: Colors.black.withOpacity(0.3),
      blurRadius: 12,
      offset: const Offset(0, 4),
    ),
  ];
}

/// Gradients réutilisables.
class AppGradients {
  AppGradients._();

  static const LinearGradient accentButton = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [AppColors.accent, AppColors.accentLight],
  );

  static const LinearGradient splash = RadialGradient(
    center: Alignment(0, -0.4),
    radius: 1.2,
    colors: [Color(0x1FFF4D00), AppColors.bgDark],
  );
}

/// ThemeData principal (dark — app dark-first).
class AppTheme {
  AppTheme._();

  // ── DARK (thème principal) ───────────────────────────────────────────────
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bgDark,
    colorScheme: ColorScheme(
      brightness: Brightness.dark,
      primary:          AppColors.accent,
      onPrimary:        AppColors.white,
      secondary:        AppColors.accentLight,
      onSecondary:      AppColors.white,
      surface:          AppColors.bgCard,
      onSurface:        AppColors.white,
      error:            AppColors.red,
      onError:          AppColors.white,
    ),
    textTheme: GoogleFonts.outfitTextTheme(ThemeData.dark().textTheme).copyWith(
      displayLarge:  AppTextStyles.headline1(AppColors.white),
      displayMedium: AppTextStyles.headline2(AppColors.white),
      displaySmall:  AppTextStyles.headline3(AppColors.white),
      headlineMedium:AppTextStyles.headline4(AppColors.white),
      bodyLarge:     AppTextStyles.body1(AppColors.grey1),
      bodyMedium:    AppTextStyles.body2(AppColors.grey3),
      labelSmall:    AppTextStyles.label(AppColors.grey3),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.bgInput,
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.accent, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.input),
        borderSide: BorderSide(color: AppColors.red, width: 1.5),
      ),
      hintStyle: AppTextStyles.body1(AppColors.grey5),
      labelStyle: AppTextStyles.label(AppColors.grey3),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: AppColors.accent,
        foregroundColor: AppColors.white,
        minimumSize: const Size(double.infinity, 54),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
        ),
        elevation: 0,
        textStyle: AppTextStyles.buttonPrimary(),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.grey1,
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
        ),
        side: BorderSide(color: AppColors.grey5, width: 1.5),
        textStyle: AppTextStyles.buttonSecondary(),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: AppColors.accent,
        textStyle: AppTextStyles.buttonGhost(),
        padding: const EdgeInsets.symmetric(vertical: 8),
      ),
    ),
    cardTheme: CardTheme(
      color: AppColors.bgCard,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.card),
        side: BorderSide(color: AppColors.grey7, width: 1),
      ),
      margin: EdgeInsets.zero,
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: AppColors.bgDark,
      elevation: 0,
      centerTitle: true,
      iconTheme: const IconThemeData(color: AppColors.grey1),
      titleTextStyle: AppTextStyles.headline4(AppColors.white),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: AppColors.bgElement,
      selectedItemColor: AppColors.accent,
      unselectedItemColor: AppColors.grey5,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
    ),
    dividerTheme: DividerThemeData(
      color: AppColors.grey7,
      thickness: 1,
      space: 0,
    ),
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.bgInput,
      labelStyle: AppTextStyles.caption(AppColors.grey3),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppRadius.pill),
        side: BorderSide(color: AppColors.grey7),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    ),
  );

  // ── LIGHT (future, prévu mais non prioritaire) ────────────────────────────
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: AppColors.bgLight,
    colorScheme: ColorScheme.fromSeed(
      seedColor: AppColors.accent,
      brightness: Brightness.light,
    ),
    textTheme: GoogleFonts.outfitTextTheme(ThemeData.light().textTheme),
  );
}
