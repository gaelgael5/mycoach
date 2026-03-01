import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/features/auth/presentation/screens/register_screen.dart';

void main() {
  Widget buildApp() => const ProviderScope(
        child: MaterialApp(home: RegisterScreen()),
      );

  // Field order in RegisterScreen:
  // 0: Prénom, 1: Nom, 2: Email, 3: Téléphone, 4: Mot de passe, 5: Confirmer
  final passwordField = find.byType(TextFormField).at(4);
  final confirmField = find.byType(TextFormField).at(5);

  group('RegisterScreen – password validation', () {
    testWidgets('shows error when passwords do not match', (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.enterText(passwordField, 'abc123');
      await tester.enterText(confirmField, 'xyz789');

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Les mots de passe ne correspondent pas'),
          findsOneWidget);
    });

    testWidgets('no mismatch error when passwords match', (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.enterText(passwordField, 'abc123');
      await tester.enterText(confirmField, 'abc123');

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Les mots de passe ne correspondent pas'),
          findsNothing);
    });

    testWidgets('shows error when password is too short', (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.enterText(passwordField, '123');
      await tester.enterText(confirmField, '123');

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Min. 6 caractères'), findsOneWidget);
    });

    testWidgets('shows error when confirm password is empty', (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.enterText(passwordField, 'abc123');

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Les mots de passe ne correspondent pas'),
          findsOneWidget);
    });

    testWidgets('shows required errors on empty submit', (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Requis'), findsNWidgets(2));
      expect(find.text('Email invalide'), findsOneWidget);
      expect(find.text('Min. 6 caractères'), findsOneWidget);
    });

    testWidgets('passwords match even with trailing spaces from paste',
        (tester) async {
      await tester.pumpWidget(buildApp());

      await tester.enterText(passwordField, 'abc123');
      await tester.enterText(confirmField, 'abc123 ');

      await tester.tap(find.text("S'inscrire"));
      await tester.pump();

      expect(find.text('Les mots de passe ne correspondent pas'),
          findsNothing);
    });
  });
}
