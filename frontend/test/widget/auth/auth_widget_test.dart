// Tests Phase A1 — Authentification (50 tests)
// ignore_for_file: avoid_print

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
// ignore: depend_on_referenced_packages
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'package:mycoach/core/theme/app_theme.dart';
import 'package:mycoach/core/providers/core_providers.dart';
import 'package:mycoach/features/auth/presentation/screens/login_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/register_role_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/register_client_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/register_coach_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/email_verification_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/otp_sms_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/forgot_password_screen.dart';
import 'package:mycoach/features/auth/presentation/screens/reset_password_screen.dart';
import 'package:mycoach/features/auth/presentation/widgets/auth_text_field.dart';
import 'package:mycoach/features/auth/presentation/widgets/gradient_button.dart';
import 'package:mycoach/features/auth/presentation/widgets/social_auth_button.dart';
import 'package:mycoach/features/auth/presentation/providers/auth_providers.dart';

// ── FakeSecureStorage (pas de keystore en environnement de test) ───────────

class FakeSecureStorage extends FlutterSecureStorage {
  final _data = <String, String>{};

  @override
  Future<void> write({
    required String key,
    required String? value,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    if (value != null) _data[key] = value;
  }

  @override
  Future<String?> read({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async =>
      _data[key];

  @override
  Future<void> delete({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _data.remove(key);
  }

  @override
  Future<void> deleteAll({
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async {
    _data.clear();
  }
}

// ── FakeAuthNotifier — retourne immédiatement data(null) ────────────────────

class FakeAuthNotifier extends AuthNotifier {
  FakeAuthNotifier(super.service, super.ref);

  @override
  Future<void> login({required String email, required String password}) async {
    throw UnimplementedError();
  }

  @override
  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
    String? phone,
    String? gender,
    int? birthYear,
  }) async {
    throw UnimplementedError();
  }
}

// ── Wrapper de test ───────────────────────────────────────────────────────────

Widget _testApp(Widget child) {
  final fakeStorage = FakeSecureStorage();
  return ProviderScope(
    overrides: [
      flutterSecureStorageProvider.overrideWithValue(fakeStorage),
      authStateProvider.overrideWith((ref) {
        final svc = ref.watch(authServiceProvider);
        return FakeAuthNotifier(svc, ref);
      }),
    ],
    child: MaterialApp(
      theme: AppTheme.dark,
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: AppLocalizations.supportedLocales,
      home: child,
    ),
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// TESTS
// ═════════════════════════════════════════════════════════════════════════════

void main() {
  // ── T01-T06 : AuthTextField ───────────────────────────────────────────────

  group('AuthTextField', () {
    testWidgets('T01 — affiche le label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(body: AuthTextField(label: 'Email')),
        ),
      );
      expect(find.text('Email'), findsOneWidget);
    });

    testWidgets('T02 — affiche le hint', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: AuthTextField(label: 'Email', hint: 'ex@test.com'),
          ),
        ),
      );
      expect(find.text('ex@test.com'), findsOneWidget);
    });

    testWidgets('T03 — password masqué par défaut', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(body: AuthTextField(label: 'Mdp', isPassword: true)),
        ),
      );
      final et = tester.widget<EditableText>(find.byType(EditableText).first);
      expect(et.obscureText, isTrue);
    });

    testWidgets('T04 — toggle visibilité mot de passe', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(body: AuthTextField(label: 'Mdp', isPassword: true)),
        ),
      );
      expect(
        tester.widget<EditableText>(find.byType(EditableText).first).obscureText,
        isTrue,
      );
      await tester.tap(find.byType(IconButton).first);
      await tester.pump();
      expect(
        tester.widget<EditableText>(find.byType(EditableText).first).obscureText,
        isFalse,
      );
    });

    testWidgets('T05 — validator affiche erreur', (tester) async {
      final key = GlobalKey<FormState>();
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: Form(
              key: key,
              child: AuthTextField(
                label: 'X',
                validator: (_) => 'Champ requis',
              ),
            ),
          ),
        ),
      );
      key.currentState?.validate();
      await tester.pump();
      expect(find.text('Champ requis'), findsOneWidget);
    });

    testWidgets('T06 — champ désactivé si enabled=false', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(body: AuthTextField(label: 'X', enabled: false)),
        ),
      );
      final tf = tester.widget<TextFormField>(find.byType(TextFormField));
      expect(tf.enabled, isFalse);
    });
  });

  // ── T07-T10 : GradientButton ──────────────────────────────────────────────

  group('GradientButton', () {
    testWidgets('T07 — affiche le label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GradientButton(label: 'Se connecter', onPressed: () {}),
          ),
        ),
      );
      expect(find.text('Se connecter'), findsOneWidget);
    });

    testWidgets('T08 — spinner quand isLoading=true', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GradientButton(label: 'Label', onPressed: () {}, isLoading: true),
          ),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Label'), findsNothing);
    });

    testWidgets('T09 — désactivé si onPressed=null', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(body: GradientButton(label: 'Btn', onPressed: null)),
        ),
      );
      final btn = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(btn.enabled, isFalse);
    });

    testWidgets('T10 — callback au tap', (tester) async {
      var hit = false;
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GradientButton(label: 'Tap', onPressed: () => hit = true),
          ),
        ),
      );
      await tester.tap(find.byType(ElevatedButton));
      expect(hit, isTrue);
    });
  });

  // ── T11-T13 : SocialAuthButton ────────────────────────────────────────────

  group('SocialAuthButton', () {
    testWidgets('T11 — affiche le label', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SocialAuthButton(
              label: 'Google',
              iconBuilder: () => const Icon(Icons.language),
              onPressed: () {},
            ),
          ),
        ),
      );
      expect(find.text('Google'), findsOneWidget);
    });

    testWidgets('T12 — désactivé si onPressed=null', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SocialAuthButton(
              label: 'G',
              iconBuilder: () => const SizedBox(),
              onPressed: null,
            ),
          ),
        ),
      );
      final btn = tester.widget<OutlinedButton>(find.byType(OutlinedButton));
      expect(btn.enabled, isFalse);
    });

    testWidgets('T13 — spinner si isLoading=true', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SocialAuthButton(
              label: 'G',
              iconBuilder: () => const SizedBox(),
              onPressed: () {},
              isLoading: true,
            ),
          ),
        ),
      );
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });

  // ── T14-T19 : LoginScreen ─────────────────────────────────────────────────

  group('LoginScreen', () {
    testWidgets('T14 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });

    testWidgets('T15 — deux champs (email + password)', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(AuthTextField), findsNWidgets(2));
    });

    testWidgets('T16 — bouton connexion présent', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T17 — bouton Google présent', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(SocialAuthButton), findsOneWidget);
    });

    testWidgets('T18 — formulaire présent', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(Form), findsOneWidget);
    });

    testWidgets('T19 — au moins 2 TextButton (forgot + signup)', (tester) async {
      await tester.pumpWidget(_testApp(const LoginScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(TextButton), findsAtLeastNWidgets(2));
    });
  });

  // ── T20-T21 : RegisterRoleScreen ──────────────────────────────────────────

  group('RegisterRoleScreen', () {
    testWidgets('T20 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterRoleScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });

    testWidgets('T21 — deux cards de rôle cliquables', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterRoleScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GestureDetector), findsAtLeastNWidgets(2));
    });
  });

  // ── T22-T26 : RegisterClientScreen ───────────────────────────────────────

  group('RegisterClientScreen', () {
    testWidgets('T22 — formulaire présent', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterClientScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(Form), findsOneWidget);
    });

    testWidgets('T23 — au moins 4 champs AuthTextField', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterClientScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(AuthTextField), findsAtLeastNWidgets(4));
    });

    testWidgets('T24 — bouton créer compte', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterClientScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T25 — dropdown genre', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterClientScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

    testWidgets('T26 — checkbox CGU', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterClientScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(Checkbox), findsOneWidget);
    });
  });

  // ── T27-T28 : RegisterCoachScreen ────────────────────────────────────────

  group('RegisterCoachScreen', () {
    testWidgets('T27 — au moins 5 champs (incl. phone)', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterCoachScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(AuthTextField), findsAtLeastNWidgets(5));
    });

    testWidgets('T28 — bouton créer compte présent', (tester) async {
      await tester.pumpWidget(_testApp(const RegisterCoachScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });
  });

  // ── T29-T31 : ForgotPasswordScreen ───────────────────────────────────────

  group('ForgotPasswordScreen', () {
    testWidgets('T29 — champ email présent', (tester) async {
      await tester.pumpWidget(_testApp(const ForgotPasswordScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(AuthTextField), findsOneWidget);
    });

    testWidgets('T30 — bouton envoyer présent', (tester) async {
      await tester.pumpWidget(_testApp(const ForgotPasswordScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T31 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const ForgotPasswordScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });
  });

  // ── T32-T34 : ResetPasswordScreen ────────────────────────────────────────

  group('ResetPasswordScreen', () {
    testWidgets('T32 — deux champs password', (tester) async {
      await tester.pumpWidget(
          _testApp(const ResetPasswordScreen(token: 'tok')));
      await tester.pumpAndSettle();
      expect(find.byType(AuthTextField), findsNWidgets(2));
    });

    testWidgets('T33 — bouton réinitialiser', (tester) async {
      await tester.pumpWidget(
          _testApp(const ResetPasswordScreen(token: 'tok')));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T34 — rendu sans token', (tester) async {
      await tester.pumpWidget(_testApp(const ResetPasswordScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });
  });

  // ── T35-T37 : OtpSmsScreen ───────────────────────────────────────────────

  group('OtpSmsScreen', () {
    testWidgets('T35 — 6 cases PIN (TextFormField)', (tester) async {
      await tester.pumpWidget(_testApp(const OtpSmsScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(TextFormField), findsNWidgets(6));
    });

    testWidgets('T36 — bouton Vérifier présent', (tester) async {
      await tester.pumpWidget(_testApp(const OtpSmsScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T37 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const OtpSmsScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });
  });

  // ── T38-T39 : EmailVerificationScreen ────────────────────────────────────

  group('EmailVerificationScreen', () {
    testWidgets('T38 — bouton Renvoyer présent', (tester) async {
      await tester.pumpWidget(_testApp(const EmailVerificationScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(GradientButton), findsOneWidget);
    });

    testWidgets('T39 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const EmailVerificationScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });
  });

  // ── T40-T44 : Validation email ────────────────────────────────────────────

  group('Validation email', () {
    bool valid(String v) =>
        RegExp(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$').hasMatch(v);

    test('T40 — valide basique', () => expect(valid('u@ex.com'), isTrue));
    test('T41 — sans @', () => expect(valid('noemail'), isFalse));
    test('T42 — sans domaine', () => expect(valid('u@'), isFalse));
    test('T43 — sous-domaine', () => expect(valid('a@b.c.co'), isTrue));
    test('T44 — TLD manquant', () => expect(valid('u@a.'), isFalse));
  });

  // ── T45-T48 : Validation password ────────────────────────────────────────

  group('Validation password', () {
    bool strong(String v) =>
        v.length >= 8 &&
        v.contains(RegExp(r'[A-Z]')) &&
        v.contains(RegExp(r'[0-9]'));

    test('T45 — fort', () => expect(strong('MyPass1!'), isTrue));
    test('T46 — trop court', () => expect(strong('Aa1'), isFalse));
    test('T47 — sans majuscule', () => expect(strong('mypass1!'), isFalse));
    test('T48 — sans chiffre', () => expect(strong('MyPassword!'), isFalse));
  });

  // ── T49-T50 : Validation phone ────────────────────────────────────────────

  group('Validation phone E.164', () {
    bool valid(String v) => RegExp(r'^\+[1-9]\d{6,14}$').hasMatch(v);

    test('T49 — français valide', () => expect(valid('+33612345678'), isTrue));
    test('T50 — sans + invalide', () => expect(valid('0612345678'), isFalse));
  });
}
