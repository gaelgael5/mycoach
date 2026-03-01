import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/features/auth/presentation/screens/login_screen.dart';

void main() {
  Widget buildApp() => const ProviderScope(
    child: MaterialApp(home: LoginScreen()),
  );

  group('LoginScreen', () {
    testWidgets('renders email and password fields', (tester) async {
      await tester.pumpWidget(buildApp());
      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Mot de passe'), findsOneWidget);
      expect(find.text('Se connecter'), findsOneWidget);
    });

    testWidgets('shows validation on empty submit', (tester) async {
      await tester.pumpWidget(buildApp());
      await tester.tap(find.text('Se connecter'));
      await tester.pump();
      expect(find.text('Email invalide'), findsOneWidget);
      expect(find.text('Min. 6 caractères'), findsOneWidget);
    });
  });
}
