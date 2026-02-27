// Tests Phase A4 — Fonctionnalités Client
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
import 'package:mycoach/shared/models/coach_search_result.dart';
import 'package:mycoach/shared/models/slot.dart';
import 'package:mycoach/shared/models/package.dart';
import 'package:mycoach/shared/models/payment.dart';
import 'package:mycoach/shared/models/performance_session.dart';
import 'package:mycoach/shared/models/program.dart';
import 'package:mycoach/shared/models/booking.dart';
import 'package:mycoach/features/client/presentation/providers/coach_search_providers.dart';
import 'package:mycoach/features/client/presentation/providers/booking_providers.dart';
import 'package:mycoach/features/client/presentation/providers/package_providers.dart';
import 'package:mycoach/features/client/presentation/providers/performance_providers.dart';
import 'package:mycoach/features/client/presentation/screens/coach_search_screen.dart';
import 'package:mycoach/features/client/presentation/screens/my_bookings_screen.dart';
import 'package:mycoach/features/client/presentation/screens/waitlist_screen.dart';
import 'package:mycoach/features/client/presentation/screens/packages_screen.dart';
import 'package:mycoach/features/client/presentation/screens/payment_history_screen.dart';
import 'package:mycoach/features/client/presentation/screens/performance_history_screen.dart';
import 'package:mycoach/features/client/presentation/screens/my_program_screen.dart';
import 'package:mycoach/features/client/presentation/screens/client_agenda_screen.dart';
import 'package:mycoach/features/client/presentation/widgets/coach_card.dart';
import 'package:mycoach/features/client/presentation/widgets/booking_tile.dart';
import 'package:mycoach/features/client/presentation/widgets/slot_grid.dart';
import 'package:mycoach/features/client/presentation/widgets/package_card.dart';
import 'package:mycoach/features/client/presentation/widgets/pr_badge.dart';
import 'package:mycoach/features/client/presentation/widgets/performance_chart.dart';

// ── FakeSecureStorage ─────────────────────────────────────────────────────────

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
  Future<Map<String, String>> readAll({
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async =>
      Map.from(_data);

  @override
  Future<bool> containsKey({
    required String key,
    IOSOptions? iOptions,
    AndroidOptions? aOptions,
    LinuxOptions? lOptions,
    WebOptions? webOptions,
    MacOsOptions? mOptions,
    WindowsOptions? wOptions,
  }) async =>
      _data.containsKey(key);
}

// ── Test Helpers ──────────────────────────────────────────────────────────────

final _fakeStorage = FakeSecureStorage();

/// Wrap a widget with all required providers and localization.
Widget _wrap(Widget child, {List<Override>? overrides}) {
  return ProviderScope(
    overrides: [
      flutterSecureStorageProvider.overrideWithValue(_fakeStorage),
      ...?overrides,
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
      locale: const Locale('fr'),
      home: child,
    ),
  );
}

// ── Sample Data ───────────────────────────────────────────────────────────────

CoachSearchResult get _sampleCoach => const CoachSearchResult(
      id: 'coach1',
      firstName: 'Alice',
      lastName: 'Dupont',
      city: 'Paris',
      specialties: ['Yoga', 'Pilates'],
      hourlyRate: 60,
      offersDiscovery: true,
      isCertified: true,
      rating: 4.8,
      reviewCount: 42,
    );

Slot get _sampleSlot => Slot(
      id: 'slot1',
      startAt: DateTime.now().add(const Duration(hours: 2)),
      endAt: DateTime.now().add(const Duration(hours: 3)),
      status: 'available',
      priceCents: 6000,
    );

Package get _samplePackage => const Package(
      id: 'pkg1',
      name: '10 séances',
      sessionsCount: 10,
      priceCents: 50000,
      validityDays: 90,
    );

Payment get _samplePayment => Payment(
      id: 'pay1',
      amountCents: 5000,
      status: 'completed',
      method: 'stripe',
      createdAt: DateTime.now().subtract(const Duration(days: 3)),
    );

Booking get _sampleBooking => Booking(
      id: 'bk1',
      coachId: 'coach1',
      coachName: 'Alice Dupont',
      clientId: 'client1',
      startAt: DateTime.now().add(const Duration(days: 1)),
      durationMin: 60,
      status: BookingStatus.confirmed,
      type: BookingType.individual,
    );

PerformanceSession get _samplePerfSession => PerformanceSession(
      id: 'ps1',
      date: DateTime.now().subtract(const Duration(days: 7)),
      coachFirstName: 'Alice',
      coachLastName: 'Dupont',
      sets: const [
        ExerciseSet(
          exerciseSlug: 'squat',
          exerciseName: 'Squat',
          reps: 10,
          weight: 80.0,
          isPr: true,
        ),
      ],
    );

PersonalRecord get _samplePR => PersonalRecord(
      exerciseSlug: 'squat',
      exerciseName: 'Squat',
      weight: 80.0,
      reps: 10,
      achievedAt: DateTime.now().subtract(const Duration(days: 7)),
    );

Program get _sampleProgram => const Program(
      id: 'prog1',
      name: 'Programme Force',
      description: 'Développer la force musculaire',
      days: [
        ProgramDay(
          dayNumber: 1,
          name: 'Jour A',
          exercises: [
            ProgramExercise(
              exerciseSlug: 'squat',
              exerciseName: 'Squat',
              sets: 4,
              reps: 8,
              weight: 80,
              restSeconds: 90,
            ),
          ],
        ),
        ProgramDay(
          dayNumber: 2,
          name: 'Jour B',
          exercises: [
            ProgramExercise(
              exerciseSlug: 'bench',
              exerciseName: 'Développé couché',
              sets: 4,
              reps: 8,
              weight: 70,
              restSeconds: 90,
            ),
          ],
        ),
      ],
    );

AgendaEvent get _sampleEvent => AgendaEvent(
      id: 'ev1',
      title: 'Séance avec Alice',
      startAt: DateTime.now().add(const Duration(days: 1, hours: 10)),
      endAt: DateTime.now().add(const Duration(days: 1, hours: 11)),
      status: 'confirmed',
      coachName: 'Alice Dupont',
    );

// ════════════════════════════════════════════════════════════════════════════
// TESTS
// ════════════════════════════════════════════════════════════════════════════

void main() {
  // ── CoachSearchResult Model Tests ──────────────────────────────────────────
  group('CoachSearchResult model', () {
    test('1. fromJson parses correctly', () {
      final json = {
        'id': 'c1',
        'first_name': 'John',
        'last_name': 'Doe',
        'city': 'Lyon',
        'specialties': ['Musculation'],
        'hourly_rate': 50,
        'offers_discovery': true,
        'is_certified': false,
        'rating': 4.5,
        'review_count': 10,
        'currency': 'EUR',
      };
      final coach = CoachSearchResult.fromJson(json);
      expect(coach.id, 'c1');
      expect(coach.fullName, 'John Doe');
      expect(coach.offersDiscovery, true);
      expect(coach.specialties, ['Musculation']);
    });

    test('2. fullName concatenates correctly', () {
      final coach = const CoachSearchResult(
        id: 'c1',
        firstName: 'Marie',
        lastName: 'Curie',
      );
      expect(coach.fullName, 'Marie Curie');
    });

    test('3. defaults are correct', () {
      final coach = const CoachSearchResult(
        id: 'c1',
        firstName: 'A',
        lastName: 'B',
      );
      expect(coach.reviewCount, 0);
      expect(coach.offersDiscovery, false);
      expect(coach.isCertified, false);
      expect(coach.currency, 'EUR');
    });
  });

  // ── Slot Model Tests ───────────────────────────────────────────────────────
  group('Slot model', () {
    test('4. fromJson parses correctly', () {
      final json = {
        'id': 's1',
        'start_at': '2026-03-01T10:00:00Z',
        'end_at': '2026-03-01T11:00:00Z',
        'status': 'available',
        'price_cents': 5000,
      };
      final slot = Slot.fromJson(json);
      expect(slot.id, 's1');
      expect(slot.isAvailable, true);
      expect(slot.priceCents, 5000);
    });

    test('5. status helpers work correctly', () {
      final available = _sampleSlot;
      expect(available.isAvailable, true);
      expect(available.isBooked, false);

      final booked = Slot(
        id: 's2',
        startAt: DateTime.now(),
        endAt: DateTime.now().add(const Duration(hours: 1)),
        status: 'booked',
      );
      expect(booked.isBooked, true);
    });
  });

  // ── Package Model Tests ────────────────────────────────────────────────────
  group('Package model', () {
    test('6. priceEur is correct', () {
      final pkg = const Package(
        id: 'p1',
        name: 'Test',
        sessionsCount: 5,
        priceCents: 25000,
        validityDays: 60,
      );
      expect(pkg.priceEur, closeTo(250.0, 0.01));
    });

    test('7. fromJson parses correctly', () {
      final json = {
        'id': 'p1',
        'name': '5 séances',
        'sessions_count': 5,
        'price_cents': 25000,
        'validity_days': 60,
        'currency': 'EUR',
        'is_discovery': false,
      };
      final pkg = Package.fromJson(json);
      expect(pkg.sessionsCount, 5);
      expect(pkg.isDiscovery, false);
    });
  });

  // ── Payment Model Tests ────────────────────────────────────────────────────
  group('Payment model', () {
    test('8. amountEur converts correctly', () {
      final payment = _samplePayment;
      expect(payment.amountEur, closeTo(50.0, 0.01));
    });

    test('9. fromJson parses all statuses', () {
      for (final status in ['pending', 'completed', 'failed', 'refunded']) {
        final json = {
          'id': 'pay',
          'amount_cents': 1000,
          'currency': 'EUR',
          'status': status,
          'method': 'stripe',
          'created_at': '2026-01-01T10:00:00Z',
        };
        final payment = Payment.fromJson(json);
        expect(payment.status, status);
      }
    });
  });

  // ── PerformanceSession Model Tests ─────────────────────────────────────────
  group('PerformanceSession model', () {
    test('10. coachFullName is correct', () {
      final session = _samplePerfSession;
      expect(session.coachFullName, 'Alice Dupont');
    });

    test('11. ExerciseSet isPr flag', () {
      const s = ExerciseSet(
        exerciseSlug: 'squat',
        exerciseName: 'Squat',
        reps: 10,
        weight: 80.0,
        isPr: true,
      );
      expect(s.isPr, true);
    });
  });

  // ── Program Model Tests ────────────────────────────────────────────────────
  group('Program model', () {
    test('12. Program parses days correctly', () {
      final program = _sampleProgram;
      expect(program.days.length, 2);
      expect(program.days[0].exercises.length, 1);
    });

    test('13. WaitlistEntry parses correctly', () {
      final json = {
        'id': 'wl1',
        'booking_id': 'bk1',
        'slot_start_at': '2026-03-01T10:00:00Z',
        'coach_name': 'Alice',
        'position': 2,
        'created_at': '2026-02-28T10:00:00Z',
      };
      final entry = WaitlistEntry.fromJson(json);
      expect(entry.position, 2);
      expect(entry.coachName, 'Alice');
    });

    test('14. AgendaEvent status helpers', () {
      final event = _sampleEvent;
      expect(event.isConfirmed, true);
      expect(event.isPending, false);
    });
  });

  // ── Widget: PrBadge ────────────────────────────────────────────────────────
  group('PrBadge widget', () {
    testWidgets('15. PrBadge renders with label', (tester) async {
      await tester.pumpWidget(_wrap(const PrBadge()));
      await tester.pumpAndSettle();
      expect(find.byType(PrBadge), findsOneWidget);
    });

    testWidgets('16. PrBadge small variant renders', (tester) async {
      await tester.pumpWidget(_wrap(const PrBadge(small: true)));
      await tester.pumpAndSettle();
      expect(find.byType(PrBadge), findsOneWidget);
    });
  });

  // ── Widget: CoachCard ──────────────────────────────────────────────────────
  group('CoachCard widget', () {
    testWidgets('17. CoachCard renders coach name', (tester) async {
      await tester.pumpWidget(_wrap(CoachCard(
        coach: _sampleCoach,
        onTap: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('Alice Dupont'), findsOneWidget);
    });

    testWidgets('18. CoachCard shows city', (tester) async {
      await tester.pumpWidget(_wrap(CoachCard(
        coach: _sampleCoach,
        onTap: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('Paris'), findsOneWidget);
    });

    testWidgets('19. CoachCard shows specialties', (tester) async {
      await tester.pumpWidget(_wrap(CoachCard(
        coach: _sampleCoach,
        onTap: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('Yoga'), findsOneWidget);
    });

    testWidgets('20. CoachCard onTap fires', (tester) async {
      bool tapped = false;
      await tester.pumpWidget(_wrap(CoachCard(
        coach: _sampleCoach,
        onTap: () => tapped = true,
      )));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(GestureDetector).first);
      expect(tapped, true);
    });

    testWidgets('21. CoachCard without discovery badge', (tester) async {
      const noDiscovery = CoachSearchResult(
        id: 'c2',
        firstName: 'Bob',
        lastName: 'Martin',
        offersDiscovery: false,
      );
      await tester.pumpWidget(_wrap(CoachCard(
        coach: noDiscovery,
        onTap: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('Bob Martin'), findsOneWidget);
    });
  });

  // ── Widget: BookingTile ────────────────────────────────────────────────────
  group('BookingTile widget', () {
    testWidgets('22. BookingTile renders coach name', (tester) async {
      await tester.pumpWidget(_wrap(BookingTile(booking: _sampleBooking)));
      await tester.pumpAndSettle();
      expect(find.text('Alice Dupont'), findsOneWidget);
    });

    testWidgets('23. BookingTile shows cancel button for future booking',
        (tester) async {
      await tester.pumpWidget(_wrap(BookingTile(
        booking: _sampleBooking,
        onCancel: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.byType(TextButton), findsOneWidget);
    });

    testWidgets('24. BookingTile no cancel for past booking', (tester) async {
      final past = Booking(
        id: 'bk2',
        coachId: 'coach1',
        coachName: 'Alice Dupont',
        clientId: 'client1',
        startAt: DateTime.now().subtract(const Duration(days: 1)),
        durationMin: 60,
        status: BookingStatus.done,
        type: BookingType.individual,
      );
      await tester.pumpWidget(_wrap(BookingTile(booking: past)));
      await tester.pumpAndSettle();
      expect(find.byType(TextButton), findsNothing);
    });
  });

  // ── Widget: SlotGrid ──────────────────────────────────────────────────────
  group('SlotGrid widget', () {
    testWidgets('25. SlotGrid shows empty message when no slots',
        (tester) async {
      await tester.pumpWidget(_wrap(SlotGrid(
        slots: const [],
        onSlotTap: (_) {},
      )));
      await tester.pumpAndSettle();
      expect(find.byType(SlotGrid), findsOneWidget);
    });

    testWidgets('26. SlotGrid renders slot cells', (tester) async {
      await tester.pumpWidget(_wrap(
        SizedBox(
          height: 300,
          child: SlotGrid(
            slots: [_sampleSlot],
            onSlotTap: (_) {},
          ),
        ),
      ));
      await tester.pumpAndSettle();
      expect(find.byType(SlotGrid), findsOneWidget);
    });
  });

  // ── Widget: PackageCard ───────────────────────────────────────────────────
  group('PackageCard widget', () {
    testWidgets('27. PackageCard renders package name', (tester) async {
      await tester.pumpWidget(_wrap(PackageCard(
        package: _samplePackage,
        onBuy: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('10 séances'), findsOneWidget);
    });

    testWidgets('28. PackageCard shows price', (tester) async {
      await tester.pumpWidget(_wrap(PackageCard(
        package: _samplePackage,
        onBuy: () {},
      )));
      await tester.pumpAndSettle();
      expect(find.text('500.00€'), findsOneWidget);
    });

    testWidgets('29. PackageCard buy button triggers callback',
        (tester) async {
      bool bought = false;
      await tester.pumpWidget(_wrap(PackageCard(
        package: _samplePackage,
        onBuy: () => bought = true,
      )));
      await tester.pumpAndSettle();
      await tester.tap(find.byType(ElevatedButton));
      expect(bought, true);
    });
  });

  // ── Widget: PerformanceChart ──────────────────────────────────────────────
  group('PerformanceChart widget', () {
    testWidgets('30. PerformanceChart renders with empty sessions',
        (tester) async {
      await tester.pumpWidget(_wrap(const PerformanceChart(
        sessions: [],
        exerciseSlug: 'squat',
      )));
      await tester.pumpAndSettle();
      expect(find.byType(PerformanceChart), findsOneWidget);
    });

    testWidgets('31. PerformanceChart renders with data', (tester) async {
      await tester.pumpWidget(_wrap(PerformanceChart(
        sessions: [_samplePerfSession],
        exerciseSlug: 'squat',
      )));
      await tester.pumpAndSettle();
      expect(find.byType(PerformanceChart), findsOneWidget);
    });
  });

  // ── Screen: CoachSearchScreen ─────────────────────────────────────────────
  group('CoachSearchScreen', () {
    testWidgets('32. CoachSearchScreen shows loading state', (tester) async {
      final overrides = [
        coachSearchResultsProvider.overrideWith(
            (ref) async => <CoachSearchResult>[]),
      ];
      await tester.pumpWidget(_wrap(const CoachSearchScreen(),
          overrides: overrides));
      await tester.pump();
      // Should show screen
      expect(find.byType(CoachSearchScreen), findsOneWidget);
    });

    testWidgets('33. CoachSearchScreen has search field', (tester) async {
      final overrides = [
        coachSearchResultsProvider.overrideWith(
            (ref) async => <CoachSearchResult>[]),
      ];
      await tester.pumpWidget(_wrap(const CoachSearchScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(TextField), findsOneWidget);
    });
  });

  // ── Screen: MyBookingsScreen ──────────────────────────────────────────────
  group('MyBookingsScreen', () {
    testWidgets('34. MyBookingsScreen shows tabs', (tester) async {
      final overrides = [
        myBookingsProvider.overrideWith((ref) async => <Booking>[]),
      ];
      await tester.pumpWidget(
          _wrap(const MyBookingsScreen(), overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(MyBookingsScreen), findsOneWidget);
    });
  });

  // ── Screen: WaitlistScreen ────────────────────────────────────────────────
  group('WaitlistScreen', () {
    testWidgets('35. WaitlistScreen shows empty state', (tester) async {
      final overrides = [
        myWaitlistProvider.overrideWith(
            (ref) async => <WaitlistEntry>[]),
      ];
      await tester.pumpWidget(
          _wrap(const WaitlistScreen(), overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(WaitlistScreen), findsOneWidget);
    });
  });

  // ── Screen: PackagesScreen ────────────────────────────────────────────────
  group('PackagesScreen', () {
    testWidgets('36. PackagesScreen shows packages', (tester) async {
      final balance = MyPackageBalance(
        sessionsRemaining: 5,
        expiresAt: DateTime.now().add(const Duration(days: 30)),
      );
      final overrides = [
        myPackageBalanceProvider.overrideWith((ref) async => balance),
        availablePackagesProvider.overrideWith(
            (ref) async => [_samplePackage]),
      ];
      await tester.pumpWidget(
          _wrap(const PackagesScreen(), overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(PackagesScreen), findsOneWidget);
    });
  });

  // ── Screen: PaymentHistoryScreen ──────────────────────────────────────────
  group('PaymentHistoryScreen', () {
    testWidgets('37. PaymentHistoryScreen shows payments', (tester) async {
      final overrides = [
        paymentHistoryProvider.overrideWith(
            (ref) async => [_samplePayment]),
      ];
      await tester.pumpWidget(_wrap(const PaymentHistoryScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(PaymentHistoryScreen), findsOneWidget);
    });

    testWidgets('38. PaymentHistoryScreen empty state', (tester) async {
      final overrides = [
        paymentHistoryProvider.overrideWith(
            (ref) async => <Payment>[]),
      ];
      await tester.pumpWidget(_wrap(const PaymentHistoryScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(PaymentHistoryScreen), findsOneWidget);
    });
  });

  // ── Screen: PerformanceHistoryScreen ─────────────────────────────────────
  group('PerformanceHistoryScreen', () {
    testWidgets('39. PerformanceHistoryScreen renders', (tester) async {
      final overrides = [
        personalRecordsProvider.overrideWith(
            (ref) async => [_samplePR]),
        performanceSessionsProvider.overrideWith(
            (ref) async => [_samplePerfSession]),
      ];
      await tester.pumpWidget(_wrap(const PerformanceHistoryScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(PerformanceHistoryScreen), findsOneWidget);
    });

    testWidgets('40. PerformanceHistoryScreen empty state', (tester) async {
      final overrides = [
        personalRecordsProvider.overrideWith(
            (ref) async => <PersonalRecord>[]),
        performanceSessionsProvider.overrideWith(
            (ref) async => <PerformanceSession>[]),
      ];
      await tester.pumpWidget(_wrap(const PerformanceHistoryScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(PerformanceHistoryScreen), findsOneWidget);
    });
  });

  // ── Screen: MyProgramScreen ───────────────────────────────────────────────
  group('MyProgramScreen', () {
    testWidgets('41. MyProgramScreen shows empty state when no program',
        (tester) async {
      final overrides = [
        assignedProgramProvider.overrideWith((ref) async => null),
      ];
      await tester.pumpWidget(
          _wrap(const MyProgramScreen(), overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(MyProgramScreen), findsOneWidget);
    });

    testWidgets('42. MyProgramScreen shows program name', (tester) async {
      final overrides = [
        assignedProgramProvider.overrideWith(
            (ref) async => _sampleProgram),
      ];
      await tester.pumpWidget(
          _wrap(const MyProgramScreen(), overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.text('Programme Force'), findsOneWidget);
    });
  });

  // ── Screen: ClientAgendaScreen ────────────────────────────────────────────
  group('ClientAgendaScreen', () {
    testWidgets('43. ClientAgendaScreen renders week view', (tester) async {
      final overrides = [
        agendaEventsProvider.overrideWith(
            (ref) async => [_sampleEvent]),
      ];
      await tester.pumpWidget(_wrap(const ClientAgendaScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(ClientAgendaScreen), findsOneWidget);
    });

    testWidgets('44. ClientAgendaScreen empty state', (tester) async {
      final overrides = [
        agendaEventsProvider.overrideWith(
            (ref) async => <AgendaEvent>[]),
      ];
      await tester.pumpWidget(_wrap(const ClientAgendaScreen(),
          overrides: overrides));
      await tester.pumpAndSettle();
      expect(find.byType(ClientAgendaScreen), findsOneWidget);
    });
  });

  // ── Additional Model Tests ────────────────────────────────────────────────
  group('Additional model tests', () {
    test('45. PersonalRecord fromJson parses correctly', () {
      final json = {
        'exercise_slug': 'deadlift',
        'exercise_name': 'Deadlift',
        'weight': 120.0,
        'reps': 5,
        'achieved_at': '2026-01-15T10:00:00Z',
      };
      final pr = PersonalRecord.fromJson(json);
      expect(pr.exerciseSlug, 'deadlift');
      expect(pr.weight, 120.0);
    });

    test('46. ProgramExercise fromJson parses correctly', () {
      final json = {
        'exercise_slug': 'bench',
        'exercise_name': 'Bench Press',
        'sets': 4,
        'reps': 8,
        'weight': 70.0,
        'rest_seconds': 90,
      };
      final ex = ProgramExercise.fromJson(json);
      expect(ex.sets, 4);
      expect(ex.restSeconds, 90);
    });

    test('47. MyPackageBalance parses correctly', () {
      final json = {
        'active_package': null,
        'sessions_remaining': 3,
        'expires_at': null,
      };
      final balance = MyPackageBalance.fromJson(json);
      expect(balance.sessionsRemaining, 3);
      expect(balance.activePackage, isNull);
    });

    test('48. PerformanceSession sets list', () {
      final session = _samplePerfSession;
      expect(session.sets.length, 1);
      expect(session.sets[0].isPr, true);
    });

    test('49. Slot toJson round-trip', () {
      final slot = _sampleSlot;
      final json = slot.toJson();
      expect(json['id'], 'slot1');
      expect(json['status'], 'available');
      expect(json['price_cents'], 6000);
    });

    test('50. CoachSearchResult toJson has all fields', () {
      final coach = _sampleCoach;
      final json = coach.toJson();
      expect(json['id'], 'coach1');
      expect(json['city'], 'Paris');
      expect(json['offers_discovery'], true);
    });
  });
}
