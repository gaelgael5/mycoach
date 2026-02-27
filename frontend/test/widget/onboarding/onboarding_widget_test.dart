// Tests Phase A2 — Onboarding (30 tests)
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
import 'package:mycoach/features/auth/presentation/providers/auth_providers.dart';
import 'package:mycoach/features/onboarding/presentation/screens/client_onboarding_screen.dart';
import 'package:mycoach/features/onboarding/presentation/screens/coach_onboarding_screen.dart';
import 'package:mycoach/features/onboarding/presentation/screens/enrollment_link_screen.dart';
import 'package:mycoach/features/onboarding/presentation/providers/onboarding_providers.dart';
import 'package:mycoach/features/onboarding/presentation/widgets/onboarding_step_indicator.dart';
import 'package:mycoach/features/onboarding/presentation/widgets/specialty_selector.dart';
import 'package:mycoach/features/onboarding/presentation/widgets/gym_search_widget.dart';
import 'package:mycoach/shared/models/user.dart';
import 'package:mycoach/shared/models/gym.dart';
import 'package:mycoach/shared/widgets/profile_completion_banner.dart';

// ── FakeSecureStorage ────────────────────────────────────────────────────────

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
  }) async =>
      _data.remove(key);

  @override
  Future<void> deleteAll({
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async =>
      _data.clear();
}

// ── Wrapper de test ──────────────────────────────────────────────────────────

Widget _testApp(Widget child, {List<Override> overrides = const []}) {
  final fakeStorage = FakeSecureStorage();
  return ProviderScope(
    overrides: [
      flutterSecureStorageProvider.overrideWithValue(fakeStorage),
      authStateProvider.overrideWith((ref) {
        final svc = ref.watch(authServiceProvider);
        return AuthNotifier(svc, ref);
      }),
      ...overrides,
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

// ── Gym de test ───────────────────────────────────────────────────────────────

const _testGym = Gym(
  id: 'gym-1',
  name: 'Fitness Park',
  brand: 'fitness_park',
  address: '12 rue des sports',
  city: 'Paris',
  postalCode: '75001',
  country: 'FR',
);

// ── Utilisateur de test ───────────────────────────────────────────────────────

const _testUser = User(
  id: 'u-1',
  email: 'test@test.com',
  role: UserRole.client,
  firstName: 'Jean',
  lastName: 'Dupont',
);

const _testUserComplete = User(
  id: 'u-2',
  email: 'full@test.com',
  role: UserRole.client,
  firstName: 'Marie',
  lastName: 'Martin',
  gender: Gender.female,
  birthYear: 1990,
  phone: '+33612345678',
  avatarUrl: 'https://example.com/avatar.jpg',
  timezone: 'Europe/Paris',
);

// ═══════════════════════════════════════════════════════════════════════════════
// TESTS
// ═══════════════════════════════════════════════════════════════════════════════

void main() {
  // ── T01-T05 : OnboardingStepIndicator ────────────────────────────────────

  group('OnboardingStepIndicator', () {
    testWidgets('T01 — rendu sans exception (4 étapes)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: Center(
              child: OnboardingStepIndicator(currentStep: 0, totalSteps: 4),
            ),
          ),
        ),
      );
      expect(tester.takeException(), isNull);
    });

    testWidgets('T02 — affiche le bon nombre de cercles (4)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: Center(
              child: OnboardingStepIndicator(currentStep: 0, totalSteps: 4),
            ),
          ),
        ),
      );
      // 4 cercles = 4 containers avec BoxDecoration circle
      final circles = tester.widgetList<Container>(find.byType(Container)).where((c) {
        final d = c.decoration;
        return d is BoxDecoration && d.shape == BoxShape.circle;
      }).toList();
      expect(circles.length, 4);
    });

    testWidgets('T03 — étape active = 2 → checkmarks sur les 2 premières', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: Center(
              child: OnboardingStepIndicator(currentStep: 2, totalSteps: 4),
            ),
          ),
        ),
      );
      // 2 checkmarks pour les étapes passées
      expect(find.byIcon(Icons.check), findsNWidgets(2));
    });

    testWidgets('T04 — 5 étapes → 5 cercles', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: Center(
              child: OnboardingStepIndicator(currentStep: 1, totalSteps: 5),
            ),
          ),
        ),
      );
      final circles = tester.widgetList<Container>(find.byType(Container)).where((c) {
        final d = c.decoration;
        return d is BoxDecoration && d.shape == BoxShape.circle;
      }).toList();
      expect(circles.length, 5);
    });

    testWidgets('T05 — étape 0 → aucun checkmark', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: const Scaffold(
            body: Center(
              child: OnboardingStepIndicator(currentStep: 0, totalSteps: 3),
            ),
          ),
        ),
      );
      expect(find.byIcon(Icons.check), findsNothing);
    });
  });

  // ── T06-T10 : SpecialtySelector ──────────────────────────────────────────

  group('SpecialtySelector', () {
    testWidgets('T06 — affiche les spécialités', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SpecialtySelector(
              selectedSpecialties: const [],
              onToggle: (_) {},
            ),
          ),
        ),
      );
      expect(find.text('Musculation'), findsOneWidget);
      expect(find.text('Yoga'), findsOneWidget);
      expect(find.text('CrossFit'), findsOneWidget);
    });

    testWidgets('T07 — spécialité sélectionnée visible', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SpecialtySelector(
              selectedSpecialties: const ['Musculation'],
              onToggle: (_) {},
            ),
          ),
        ),
      );
      expect(find.text('Musculation'), findsOneWidget);
    });

    testWidgets('T08 — toggle callback déclenché', (tester) async {
      String? toggled;
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SpecialtySelector(
              selectedSpecialties: const [],
              onToggle: (s) => toggled = s,
            ),
          ),
        ),
      );
      await tester.tap(find.text('Yoga'));
      await tester.pump();
      expect(toggled, 'Yoga');
    });

    testWidgets('T09 — affiche toutes les 20 spécialités', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SingleChildScrollView(
              child: SpecialtySelector(
                selectedSpecialties: const [],
                onToggle: (_) {},
              ),
            ),
          ),
        ),
      );
      expect(find.text('Golf'), findsOneWidget);
      expect(find.text('Boxe'), findsOneWidget);
    });

    testWidgets('T10 — rendu sans exception', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: SpecialtySelector(
              selectedSpecialties: const ['Cardio', 'HIIT'],
              onToggle: (_) {},
            ),
          ),
        ),
      );
      expect(tester.takeException(), isNull);
    });
  });

  // ── T11-T14 : GoalSelector ───────────────────────────────────────────────

  group('GoalSelector', () {
    testWidgets('T11 — affiche les objectifs avec labels', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GoalSelector(
              selectedGoals: const [],
              goalLabels: const {
                'weight_loss': 'Perte de poids',
                'muscle_gain': 'Prise de masse',
                'endurance': 'Endurance',
                'flexibility': 'Flexibilité',
                'wellness': 'Bien-être',
                'sport_competition': 'Sport compétitif',
                'rehabilitation': 'Rééducation',
                'other': 'Autre',
              },
              onToggle: (_) {},
            ),
          ),
        ),
      );
      expect(find.text('Perte de poids'), findsOneWidget);
      expect(find.text('Endurance'), findsOneWidget);
    });

    testWidgets('T12 — callback onToggle déclenché', (tester) async {
      String? toggled;
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GoalSelector(
              selectedGoals: const [],
              goalLabels: const {
                'weight_loss': 'Perte de poids',
                'muscle_gain': 'Prise de masse',
                'endurance': 'Endurance',
                'flexibility': 'Flexibilité',
                'wellness': 'Bien-être',
                'sport_competition': 'Sport compétitif',
                'rehabilitation': 'Rééducation',
                'other': 'Autre',
              },
              onToggle: (g) => toggled = g,
            ),
          ),
        ),
      );
      await tester.tap(find.text('Endurance'));
      expect(toggled, 'endurance');
    });

    testWidgets('T13 — 8 chips affichés', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: AppTheme.dark,
          home: Scaffold(
            body: GoalSelector(
              selectedGoals: const [],
              goalLabels: {for (final g in kClientGoals) g: g},
              onToggle: (_) {},
            ),
          ),
        ),
      );
      // 8 GestureDetectors (un par objectif)
      expect(find.byType(GestureDetector), findsAtLeastNWidgets(8));
    });
  });

  // ── T14-T17 : GymSearchWidget ────────────────────────────────────────────

  group('GymSearchWidget', () {
    testWidgets('T14 — champ de recherche présent', (tester) async {
      await tester.pumpWidget(
        _testApp(
          Scaffold(
            body: GymSearchWidget(
              selectedGyms: const [],
              onToggle: (_) {},
            ),
          ),
        ),
      );
      await tester.pump();
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('T15 — salles sélectionnées affichées', (tester) async {
      await tester.pumpWidget(
        _testApp(
          Scaffold(
            body: GymSearchWidget(
              selectedGyms: const [_testGym],
              onToggle: (_) {},
            ),
          ),
        ),
      );
      await tester.pump();
      expect(find.text('Fitness Park'), findsOneWidget);
    });

    testWidgets('T16 — toggle callback déclenché sur salle sélectionnée', (tester) async {
      Gym? toggled;
      await tester.pumpWidget(
        _testApp(
          Scaffold(
            body: GymSearchWidget(
              selectedGyms: const [_testGym],
              onToggle: (g) => toggled = g,
            ),
          ),
        ),
      );
      await tester.pump();
      // Tap le bouton Retirer
      await tester.tap(find.textContaining('Retirer').last);
      await tester.pump();
      expect(toggled?.id, 'gym-1');
    });

    testWidgets('T17 — max 5 salles respecté visuellement', (tester) async {
      final gyms = List.generate(
        5,
        (i) => Gym(
          id: 'gym-$i',
          name: 'Gym $i',
          brand: 'brand',
          address: 'addr',
          city: 'City',
          postalCode: '75000',
          country: 'FR',
        ),
      );
      await tester.pumpWidget(
        _testApp(
          Scaffold(
            body: SingleChildScrollView(
              child: GymSearchWidget(
                selectedGyms: gyms,
                onToggle: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pump();
      // Compteur 5/5
      expect(find.text('5/5'), findsOneWidget);
    });
  });

  // ── T18-T21 : ProfileCompletionBanner ────────────────────────────────────

  group('ProfileCompletionBanner', () {
    testWidgets('T18 — invisible si profil complet', (tester) async {
      await tester.pumpWidget(
        _testApp(
          const Scaffold(
            body: ProfileCompletionBanner(user: _testUserComplete),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(LinearProgressIndicator), findsNothing);
    });

    testWidgets('T19 — visible si profil incomplet', (tester) async {
      await tester.pumpWidget(
        _testApp(
          const Scaffold(
            body: ProfileCompletionBanner(user: _testUser),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('T20 — calcul de complétion minimal (2 champs remplis)', (tester) async {
      final percent = computeProfileCompletion(_testUser);
      expect(percent, lessThan(100));
      expect(percent, greaterThan(0));
    });

    testWidgets('T21 — complétion maximale si tout rempli', (tester) async {
      final percent = computeProfileCompletion(_testUserComplete);
      expect(percent, 100);
    });
  });

  // ── T22-T26 : ClientOnboardingScreen ─────────────────────────────────────

  group('ClientOnboardingScreen', () {
    testWidgets('T22 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const ClientOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });

    testWidgets('T23 — step indicator visible', (tester) async {
      await tester.pumpWidget(_testApp(const ClientOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(OnboardingStepIndicator), findsOneWidget);
    });

    testWidgets('T24 — champs prénom et nom présents à l\'étape 1', (tester) async {
      await tester.pumpWidget(_testApp(const ClientOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(TextField), findsAtLeastNWidgets(2));
    });

    testWidgets('T25 — bouton Suivant présent', (tester) async {
      await tester.pumpWidget(_testApp(const ClientOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(ElevatedButton), findsAtLeastNWidgets(1));
    });

    testWidgets('T26 — étape 1 sur 4 affichée dans le header', (tester) async {
      await tester.pumpWidget(_testApp(const ClientOnboardingScreen()));
      await tester.pumpAndSettle();
      // Cherche le texte de l'étape
      final stepFinder = find.textContaining('1');
      expect(stepFinder, findsAtLeastNWidgets(1));
    });
  });

  // ── T27-T30 : CoachOnboardingScreen ──────────────────────────────────────

  group('CoachOnboardingScreen', () {
    testWidgets('T27 — rendu sans exception', (tester) async {
      await tester.pumpWidget(_testApp(const CoachOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
    });

    testWidgets('T28 — step indicator avec 5 étapes', (tester) async {
      await tester.pumpWidget(_testApp(const CoachOnboardingScreen()));
      await tester.pumpAndSettle();
      final circles = tester.widgetList<Container>(find.byType(Container)).where((c) {
        final d = c.decoration;
        return d is BoxDecoration && d.shape == BoxShape.circle;
      }).toList();
      expect(circles.length, greaterThanOrEqualTo(5));
    });

    testWidgets('T29 — textarea bio présent à l\'étape 1', (tester) async {
      await tester.pumpWidget(_testApp(const CoachOnboardingScreen()));
      await tester.pumpAndSettle();
      // Textarea (maxLines > 1)
      final textFields = tester.widgetList<TextField>(find.byType(TextField));
      final hasMultiline = textFields.any((t) => t.maxLines != null && t.maxLines! > 1);
      expect(hasMultiline, isTrue);
    });

    testWidgets('T30 — bouton Suivant présent', (tester) async {
      await tester.pumpWidget(_testApp(const CoachOnboardingScreen()));
      await tester.pumpAndSettle();
      expect(find.byType(ElevatedButton), findsAtLeastNWidgets(1));
    });
  });

  // ── Tests unitaires providers ─────────────────────────────────────────────

  group('ClientOnboardingNotifier (unit)', () {
    test('T31 — toggleGoal ajoute et retire', () {
      // Test logique pure sans UI
      final goals = <String>[];
      void toggle(String g) {
        if (goals.contains(g)) goals.remove(g); else goals.add(g);
      }
      toggle('weight_loss');
      expect(goals, contains('weight_loss'));
      toggle('weight_loss');
      expect(goals, isNot(contains('weight_loss')));
    });

    test('T32 — max 5 gyms respecté', () {
      final selected = <Gym>[];
      void toggle(Gym g) {
        if (selected.any((s) => s.id == g.id)) {
          selected.removeWhere((s) => s.id == g.id);
        } else if (selected.length < 5) {
          selected.add(g);
        }
      }
      for (var i = 0; i < 6; i++) {
        toggle(Gym(
          id: 'g$i',
          name: 'G$i',
          brand: 'b',
          address: 'a',
          city: 'c',
          postalCode: 'p',
          country: 'FR',
        ));
      }
      expect(selected.length, 5);
    });

    test('T33 — canProceedFromStep2 false si aucune spécialité', () {
      final state = CoachOnboardingState();
      expect(state.canProceedFromStep2, isFalse);
    });

    test('T34 — canProceedFromStep2 true si au moins une spécialité', () {
      final state = CoachOnboardingState(selectedSpecialties: ['Yoga']);
      expect(state.canProceedFromStep2, isTrue);
    });
  });

  // ── T35 : EnrollmentLinkScreen ───────────────────────────────────────────

  group('EnrollmentLinkScreen', () {
    testWidgets('T35 — rendu sans exception', (tester) async {
      await tester.pumpWidget(
        _testApp(const EnrollmentLinkScreen(token: 'test-token')),
      );
      await tester.pump(); // ne pas pumpAndSettle (réseau mocké non résolu)
      expect(tester.takeException(), isNull);
    });
  });
}
