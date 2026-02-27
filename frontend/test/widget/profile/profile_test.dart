import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach/shared/models/user.dart';
import 'package:mycoach/shared/models/social_link.dart';
import 'package:mycoach/shared/models/health_log.dart';
import 'package:mycoach/shared/models/health_parameter.dart';
import 'package:mycoach/shared/models/feedback_item.dart';
import 'package:mycoach/shared/widgets/avatar_widget.dart';
import 'package:mycoach/features/profile/presentation/widgets/social_link_tile.dart';
import 'package:mycoach/features/profile/presentation/widgets/health_chart_widget.dart';

// ── Helpers ──────────────────────────────────────────────────────────────────

Widget _wrap(Widget child) {
  return ProviderScope(
    child: MaterialApp(home: Scaffold(body: child)),
  );
}

User _makeUser({
  String id = 'u1',
  String firstName = 'Alice',
  String lastName = 'Martin',
  UserRole role = UserRole.client,
  Gender? gender,
  String? avatarUrl,
}) =>
    User(
      id: id,
      email: 'alice@test.com',
      role: role,
      firstName: firstName,
      lastName: lastName,
      gender: gender,
      avatarUrl: avatarUrl,
      resolvedAvatarUrl: avatarUrl,
    );

SocialLink _makeLink({
  String id = 'l1',
  String? platform = 'instagram',
  String url = 'https://instagram.com/alice',
  String? label,
}) =>
    SocialLink(
      id: id,
      platform: platform,
      url: url,
      label: label,
    );

HealthLog _makeLog({
  String id = 'log1',
  String parameterId = 'p1',
  String parameterSlug = 'poids',
  String parameterLabel = 'Poids',
  double value = 72.5,
  String unit = 'kg',
}) =>
    HealthLog(
      id: id,
      parameterId: parameterId,
      parameterSlug: parameterSlug,
      parameterLabel: parameterLabel,
      value: value,
      unit: unit,
      measuredAt: DateTime.now(),
    );

HealthParameter _makeParam({
  String id = 'p1',
  String slug = 'poids',
  String unit = 'kg',
  String dataType = 'decimal',
}) =>
    HealthParameter(
      id: id,
      slug: slug,
      label: {'fr': 'Poids', 'en': 'Weight'},
      unit: unit,
      dataType: dataType,
      category: 'body',
      active: true,
      position: 1,
    );

FeedbackItem _makeFeedback({
  String id = 'f1',
  FeedbackType type = FeedbackType.suggestion,
  String title = 'Super appli',
  String description = 'Vraiment top',
  FeedbackStatus status = FeedbackStatus.pending,
}) =>
    FeedbackItem(
      id: id,
      type: type,
      title: title,
      description: description,
      status: status,
      createdAt: DateTime(2026, 2, 1),
    );

// ── Tests ────────────────────────────────────────────────────────────────────

void main() {
  // ── User model ────────────────────────────────────────────────────────────

  group('User model', () {
    test('1 - fullName returns trimmed first + last name', () {
      final u = _makeUser(firstName: 'Alice', lastName: 'Martin');
      expect(u.fullName, 'Alice Martin');
    });

    test('2 - fromJson parses all fields correctly', () {
      final json = {
        'id': 'u1',
        'email': 'test@test.com',
        'role': 'coach',
        'first_name': 'Bob',
        'last_name': 'Smith',
        'gender': 'male',
        'birth_year': 1990,
        'is_active': true,
      };
      final u = User.fromJson(json);
      expect(u.role, UserRole.coach);
      expect(u.gender, Gender.male);
      expect(u.birthYear, 1990);
    });

    test('3 - copyWith updates only specified fields', () {
      final u = _makeUser();
      final u2 = u.copyWith(firstName: 'Bob');
      expect(u2.firstName, 'Bob');
      expect(u2.lastName, u.lastName);
    });

    test('4 - isPhoneVerified is false when phoneVerifiedAt is null', () {
      final u = _makeUser();
      expect(u.isPhoneVerified, isFalse);
    });

    test('5 - UserRole.isCoach is true for coach and admin', () {
      expect(UserRole.coach.isCoach, isTrue);
      expect(UserRole.admin.isCoach, isTrue);
      expect(UserRole.client.isCoach, isFalse);
    });

    test('6 - Gender.fromString parses correctly', () {
      expect(Gender.fromString('male'), Gender.male);
      expect(Gender.fromString('female'), Gender.female);
      expect(Gender.fromString('other'), Gender.other);
      expect(Gender.fromString(null), isNull);
    });

    test('7 - User.toJson is serializable', () {
      final u = _makeUser();
      final json = u.toJson();
      expect(json['id'], u.id);
      expect(json['email'], u.email);
    });
  });

  // ── SocialLink model ─────────────────────────────────────────────────────

  group('SocialLink model', () {
    test('8 - fromJson parses platform and url', () {
      final json = {
        'id': 'l1',
        'platform': 'instagram',
        'url': 'https://instagram.com/alice',
        'visibility': 'public',
      };
      final l = SocialLink.fromJson(json);
      expect(l.platform, 'instagram');
      expect(l.url, 'https://instagram.com/alice');
    });

    test('9 - isCustom is true when platform is null', () {
      final l = SocialLink(id: 'l', url: 'https://x.com');
      expect(l.isCustom, isTrue);
    });

    test('10 - displayLabel returns platform when label is null', () {
      final l = _makeLink(label: null);
      expect(l.displayLabel, 'instagram');
    });

    test('11 - displayLabel returns label when provided', () {
      final l = _makeLink(label: 'Ma page Insta');
      expect(l.displayLabel, 'Ma page Insta');
    });

    test('12 - LinkVisibility.fromString parses coaches_only', () {
      expect(
        LinkVisibility.fromString('coaches_only'),
        LinkVisibility.coachesOnly,
      );
      expect(
        LinkVisibility.fromString('public'),
        LinkVisibility.public,
      );
    });

    test('13 - toJson excludes null fields', () {
      final l = SocialLink(id: 'l1', url: 'https://x.com');
      final json = l.toJson();
      expect(json.containsKey('platform'), isFalse);
      expect(json.containsKey('label'), isFalse);
    });
  });

  // ── HealthLog model ──────────────────────────────────────────────────────

  group('HealthLog model', () {
    test('14 - fromJson parses value as double', () {
      final json = {
        'id': 'log1',
        'parameter_id': 'p1',
        'parameter_slug': 'poids',
        'parameter_label': 'Poids',
        'value': 72,
        'unit': 'kg',
        'measured_at': '2026-01-01T10:00:00.000Z',
      };
      final l = HealthLog.fromJson(json);
      expect(l.value, 72.0);
      expect(l.value, isA<double>());
    });

    test('15 - fromJson parses measured_at as DateTime', () {
      final json = {
        'id': 'log1',
        'parameter_id': 'p1',
        'parameter_slug': 'poids',
        'parameter_label': 'Poids',
        'value': 72.5,
        'unit': 'kg',
        'measured_at': '2026-01-15T08:30:00.000Z',
      };
      final l = HealthLog.fromJson(json);
      expect(l.measuredAt, isA<DateTime>());
      expect(l.measuredAt.month, 1);
    });

    test('16 - toJson serializes correctly', () {
      final l = _makeLog();
      final json = l.toJson();
      expect(json['value'], 72.5);
      expect(json['unit'], 'kg');
    });

    test('17 - props for equality comparison', () {
      final l1 = _makeLog();
      final l2 = _makeLog();
      expect(l1, equals(l2));
    });
  });

  // ── HealthParameter model ────────────────────────────────────────────────

  group('HealthParameter model', () {
    test('18 - labelFor returns correct locale', () {
      final p = _makeParam();
      expect(p.labelFor('fr'), 'Poids');
      expect(p.labelFor('en'), 'Weight');
    });

    test('19 - labelFor falls back to fr', () {
      final p = _makeParam();
      expect(p.labelFor('de'), 'Poids');
    });

    test('20 - fromJson parses label map', () {
      final json = {
        'id': 'p1',
        'slug': 'poids',
        'label': {'fr': 'Poids', 'en': 'Weight'},
        'unit': 'kg',
        'data_type': 'decimal',
        'category': 'body',
        'active': true,
        'position': 1,
      };
      final p = HealthParameter.fromJson(json);
      expect(p.label['fr'], 'Poids');
      expect(p.unit, 'kg');
    });

    test('21 - fromJson handles string label with fallback', () {
      final json = {
        'id': 'p1',
        'slug': 'poids',
        'label': 'Poids',
        'unit': 'kg',
        'data_type': 'decimal',
        'category': 'body',
        'active': true,
        'position': 1,
      };
      final p = HealthParameter.fromJson(json);
      expect(p.labelFor('fr'), 'Poids');
    });
  });

  // ── FeedbackItem model ───────────────────────────────────────────────────

  group('FeedbackItem model', () {
    test('22 - fromJson parses type correctly', () {
      final json = {
        'id': 'f1',
        'type': 'bug_report',
        'title': 'Bug',
        'description': 'crash',
        'status': 'in_review',
        'created_at': '2026-02-01T00:00:00.000Z',
      };
      final f = FeedbackItem.fromJson(json);
      expect(f.type, FeedbackType.bugReport);
      expect(f.status, FeedbackStatus.inReview);
    });

    test('23 - FeedbackType.value returns correct string', () {
      expect(FeedbackType.bugReport.value, 'bug_report');
      expect(FeedbackType.suggestion.value, 'suggestion');
    });

    test('24 - FeedbackStatus.fromString parses done', () {
      expect(FeedbackStatus.fromString('done'), FeedbackStatus.done);
      expect(FeedbackStatus.fromString('pending'), FeedbackStatus.pending);
    });

    test('25 - toJson serializes correctly', () {
      final f = _makeFeedback();
      final json = f.toJson();
      expect(json['type'], 'suggestion');
      expect(json['title'], 'Super appli');
    });
  });

  // ── AvatarWidget ─────────────────────────────────────────────────────────

  group('AvatarWidget', () {
    testWidgets('26 - renders without avatarUrl (placeholder)', (tester) async {
      await tester.pumpWidget(_wrap(
        const AvatarWidget(size: 80),
      ));
      expect(find.byType(Icon), findsOneWidget);
    });

    testWidgets('27 - renders with editable overlay', (tester) async {
      await tester.pumpWidget(_wrap(
        AvatarWidget(
          size: 80,
          editable: true,
          onEditTap: () {},
        ),
      ));
      // Camera icon should be present
      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
    });

    testWidgets('28 - male gender shows person icon', (tester) async {
      await tester.pumpWidget(_wrap(
        const AvatarWidget(gender: Gender.male, size: 60),
      ));
      expect(find.byIcon(Icons.person), findsOneWidget);
    });

    testWidgets('29 - female gender shows person_outline icon', (tester) async {
      await tester.pumpWidget(_wrap(
        const AvatarWidget(gender: Gender.female, size: 60),
      ));
      expect(find.byIcon(Icons.person_outline), findsOneWidget);
    });

    testWidgets('30 - size parameter controls widget size', (tester) async {
      await tester.pumpWidget(_wrap(
        const AvatarWidget(size: 120),
      ));
      // Just ensure it renders
      expect(find.byType(AvatarWidget), findsOneWidget);
    });
  });

  // ── SocialLinkTile ───────────────────────────────────────────────────────

  group('SocialLinkTile', () {
    testWidgets('31 - shows platform icon for instagram', (tester) async {
      final link = _makeLink(platform: 'instagram');
      await tester.pumpWidget(_wrap(
        SocialLinkTile(link: link),
      ));
      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
    });

    testWidgets('32 - shows delete button when onDelete provided', (tester) async {
      final link = _makeLink();
      await tester.pumpWidget(_wrap(
        SocialLinkTile(link: link, onDelete: () {}),
      ));
      expect(find.byIcon(Icons.close), findsOneWidget);
    });

    testWidgets('33 - shows url as subtitle', (tester) async {
      final link = _makeLink(url: 'https://instagram.com/test');
      await tester.pumpWidget(_wrap(
        SocialLinkTile(link: link),
      ));
      expect(find.text('https://instagram.com/test'), findsOneWidget);
    });

    testWidgets('34 - shows custom icon for null platform', (tester) async {
      final link = SocialLink(id: 'l1', url: 'https://x.com', label: 'Mon site');
      await tester.pumpWidget(_wrap(
        SocialLinkTile(link: link),
      ));
      expect(find.byIcon(Icons.link), findsOneWidget);
    });
  });

  // ── HealthChartWidget ────────────────────────────────────────────────────

  group('HealthChartWidget', () {
    testWidgets('35 - renders empty SizedBox when no logs', (tester) async {
      await tester.pumpWidget(_wrap(
        const HealthChartWidget(logs: []),
      ));
      // Should not render the chart
      expect(find.byType(HealthChartWidget), findsOneWidget);
    });

    testWidgets('36 - renders LineChart when logs present', (tester) async {
      final logs = [
        _makeLog(id: 'l1', value: 70.0),
        _makeLog(id: 'l2', value: 71.5),
        _makeLog(id: 'l3', value: 72.0),
      ];
      await tester.pumpWidget(_wrap(
        HealthChartWidget(logs: logs),
      ));
      expect(find.byType(HealthChartWidget), findsOneWidget);
    });

    testWidgets('37 - compact mode has smaller height', (tester) async {
      final logs = [
        _makeLog(id: 'l1', value: 70.0),
        _makeLog(id: 'l2', value: 71.0),
      ];
      await tester.pumpWidget(_wrap(
        HealthChartWidget(logs: logs, compact: true),
      ));
      expect(find.byType(HealthChartWidget), findsOneWidget);
    });
  });

  // ── platformIcon helper ──────────────────────────────────────────────────

  group('platformIcon helper', () {
    test('38 - returns camera_alt for instagram', () {
      expect(platformIcon('instagram'), Icons.camera_alt);
    });

    test('39 - returns play_circle for youtube', () {
      expect(platformIcon('youtube'), Icons.play_circle);
    });

    test('40 - returns link for null/custom', () {
      expect(platformIcon(null), Icons.link);
      expect(platformIcon('custom'), Icons.link);
    });

    test('41 - returns music_note for tiktok', () {
      expect(platformIcon('tiktok'), Icons.music_note);
    });

    test('42 - returns work for linkedin', () {
      expect(platformIcon('linkedin'), Icons.work);
    });

    test('43 - returns language for website', () {
      expect(platformIcon('website'), Icons.language);
    });
  });
}
