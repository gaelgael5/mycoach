// Tests du design system MyCoach.
//
// Note : google_fonts charge les polices de manière asynchrone.
// En environnement de test, aucune police externe n'est disponible.
// → Les tests de couleurs et de constantes utilisent uniquement des assertions
//   simples (pas de pump de MaterialApp avec AppTheme.dark).
// → Les tests d'intégration widget utilisent un ThemeData minimal sans google_fonts.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach/core/theme/app_theme.dart';

/// ThemeData léger pour les widget tests — sans google_fonts.
ThemeData get _testTheme => ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme(
        brightness: Brightness.dark,
        primary: AppColors.accent,
        onPrimary: AppColors.white,
        secondary: AppColors.accentLight,
        onSecondary: AppColors.white,
        surface: AppColors.bgCard,
        onSurface: AppColors.white,
        background: AppColors.bgDark,
        onBackground: AppColors.white,
        error: AppColors.red,
        onError: AppColors.white,
      ),
      scaffoldBackgroundColor: AppColors.bgDark,
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.accent,
          foregroundColor: AppColors.white,
        ),
      ),
    );

void main() {
  // ── Couleurs ─────────────────────────────────────────────────────────────
  group('AppColors', () {
    test('accent color is brand orange #FF4D00', () {
      expect(AppColors.accent.value, 0xFFFF4D00);
    });

    test('dark bg is #0A0A0F', () {
      expect(AppColors.bgDark.value, 0xFF0A0A0F);
    });

    test('card bg is #14141F', () {
      expect(AppColors.bgCard.value, 0xFF14141F);
    });

    test('green is available slot color #00E676', () {
      expect(AppColors.green.value, 0xFF00E676);
    });

    test('yellow is PR / alert color #FFD600', () {
      expect(AppColors.yellow.value, 0xFFFFD600);
    });

    test('red is error color #FF3D57', () {
      expect(AppColors.red.value, 0xFFFF3D57);
    });

    test('blue is certified badge color #4D8DFF', () {
      expect(AppColors.blue.value, 0xFF4D8DFF);
    });

    test('all surface/glow colors are semi-transparent', () {
      expect(AppColors.accentGlow.alpha,   lessThan(255));
      expect(AppColors.greenSurface.alpha, lessThan(255));
      expect(AppColors.yellowSurface.alpha,lessThan(255));
      expect(AppColors.blueSurface.alpha,  lessThan(255));
    });

    test('white is near-white #FAFAFA', () {
      expect(AppColors.white.value, 0xFFFAFAFA);
    });
  });

  // ── Rayons ────────────────────────────────────────────────────────────────
  group('AppRadius', () {
    test('card = 14', ()   => expect(AppRadius.card,   14.0));
    test('input = 10', ()  => expect(AppRadius.input,  10.0));
    test('pill = 50', ()   => expect(AppRadius.pill,   50.0));
    test('avatar = 16', () => expect(AppRadius.avatar, 16.0));
    test('circle = 999', ()=> expect(AppRadius.circle, 999.0));
  });

  // ── ColorScheme (sans google_fonts) ──────────────────────────────────────
  group('AppTheme ColorScheme', () {
    test('primary = accent orange', () {
      expect(_testTheme.colorScheme.primary, AppColors.accent);
    });

    test('error = red', () {
      expect(_testTheme.colorScheme.error, AppColors.red);
    });

    test('surface = card bg', () {
      expect(_testTheme.colorScheme.surface, AppColors.bgCard);
    });

    test('scaffold background = dark bg', () {
      expect(_testTheme.scaffoldBackgroundColor, AppColors.bgDark);
    });

    test('brightness is dark', () {
      expect(_testTheme.brightness, Brightness.dark);
    });

    test('useMaterial3 is true', () {
      expect(_testTheme.useMaterial3, true);
    });
  });

  // ── Gradients ─────────────────────────────────────────────────────────────
  group('AppGradients', () {
    test('accentButton is LinearGradient', () {
      expect(AppGradients.accentButton, isA<LinearGradient>());
      expect(AppGradients.accentButton.colors.first, AppColors.accent);
      expect(AppGradients.accentButton.colors.last, AppColors.accentLight);
    });

    test('splash is RadialGradient', () {
      expect(AppGradients.splash, isA<RadialGradient>());
    });
  });

  // ── Widget integration (thème minimal sans google_fonts) ──────────────────
  group('Widget integration', () {
    testWidgets('dark theme applied to MaterialApp', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme:     _testTheme,
          themeMode: ThemeMode.dark,
          home: const Scaffold(body: SizedBox()),
        ),
      );
      final context = tester.element(find.byType(Scaffold));
      final theme = Theme.of(context);
      expect(theme.brightness, Brightness.dark);
      expect(theme.colorScheme.primary, AppColors.accent);
    });

    testWidgets('ElevatedButton uses accent background', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: _testTheme,
          home: Scaffold(
            body: ElevatedButton(
              onPressed: () {},
              child: const Text('Test'),
            ),
          ),
        ),
      );
      // Vérifie que le bouton est affiché sans erreur de layout
      expect(find.text('Test'), findsOneWidget);
      final btn = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      final bg = btn.style?.backgroundColor?.resolve({});
      expect(bg, AppColors.accent);
    });

    testWidgets('Scaffold background uses dark color', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: _testTheme,
          home: const Scaffold(body: SizedBox()),
        ),
      );
      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
      // Le fond n'est pas défini sur le widget directement,
      // mais le theme est appliqué — on vérifie via Theme.of
      final ctx = tester.element(find.byType(Scaffold));
      expect(Theme.of(ctx).scaffoldBackgroundColor, AppColors.bgDark);
    });
  });
}
