import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mycoach/core/theme/app_theme.dart';

void main() {
  // google_fonts essaie de télécharger les polices depuis fonts.gstatic.com.
  // TestWidgetsFlutterBinding bloque toutes les requêtes HTTP → erreur.
  // Solution : désactiver le runtime fetching pour tous les tests.
  setUpAll(() {
    GoogleFonts.config.allowRuntimeFetching = false;
  });

  group('AppColors', () {
    test('accent color is brand orange #FF4D00', () {
      expect(AppColors.accent.value, 0xFFFF4D00);
    });

    test('dark bg is #0A0A0F', () {
      expect(AppColors.bgDark.value, 0xFF0A0A0F);
    });

    test('green is available slot color', () {
      expect(AppColors.green.value, 0xFF00E676);
    });

    test('red is error color', () {
      expect(AppColors.red.value, 0xFFFF3D57);
    });

    test('all transparency variants are semi-transparent', () {
      expect(AppColors.accentGlow.alpha, lessThan(255));
      expect(AppColors.greenSurface.alpha, lessThan(255));
      expect(AppColors.yellowSurface.alpha, lessThan(255));
      expect(AppColors.blueSurface.alpha, lessThan(255));
    });
  });

  group('AppTheme.dark', () {
    test('useMaterial3 is true', () {
      expect(AppTheme.dark.useMaterial3, true);
    });

    test('brightness is dark', () {
      expect(AppTheme.dark.brightness, Brightness.dark);
    });

    test('primary color matches accent', () {
      expect(AppTheme.dark.colorScheme.primary, AppColors.accent);
    });

    test('scaffold background is dark', () {
      expect(AppTheme.dark.scaffoldBackgroundColor, AppColors.bgDark);
    });

    test('error color is red', () {
      expect(AppTheme.dark.colorScheme.error, AppColors.red);
    });
  });

  group('AppRadius', () {
    test('card radius is 14', () => expect(AppRadius.card, 14.0));
    test('input radius is 10', () => expect(AppRadius.input, 10.0));
    test('pill radius is 50', () => expect(AppRadius.pill, 50.0));
  });

  group('AppTheme widget integration', () {
    testWidgets('dark theme applied to MaterialApp', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme:     AppTheme.light,
          darkTheme: AppTheme.dark,
          themeMode: ThemeMode.dark,
          home: const Scaffold(body: SizedBox()),
        ),
      );
      final context = tester.element(find.byType(Scaffold));
      final theme = Theme.of(context);
      expect(theme.brightness, Brightness.dark);
      expect(theme.colorScheme.primary, AppColors.accent);
    });

    testWidgets('ElevatedButton has orange background', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          darkTheme: AppTheme.dark,
          themeMode: ThemeMode.dark,
          home: Scaffold(
            body: ElevatedButton(
              onPressed: () {},
              child: const Text('Test'),
            ),
          ),
        ),
      );
      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      final style = button.style;
      final bg = style?.backgroundColor?.resolve({});
      expect(bg, AppColors.accent);
    });
  });
}
