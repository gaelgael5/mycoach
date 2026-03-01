import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/program.dart';

void main() {
  group('Program', () {
    test('fromJson with full data', () {
      final json = {
        'id': 'p1', 'name': 'Fat Loss', 'description': 'Desc',
        'duration_weeks': 8, 'created_at': '2025-01-01T00:00:00Z',
        'sessions': [
          {'id': 's1', 'title': 'Upper', 'day_of_week': 1, 'exercises': [
            {'id': 'e1', 'name': 'Bench', 'sets': 3, 'reps': 10, 'weight_kg': 60, 'rest_seconds': 90}
          ]}
        ],
        'assigned_client_ids': ['c1', 'c2'],
      };
      final p = Program.fromJson(json);
      expect(p.name, 'Fat Loss');
      expect(p.durationWeeks, 8);
      expect(p.sessions.length, 1);
      expect(p.sessions.first.exercises.length, 1);
      expect(p.assignedClientIds, ['c1', 'c2']);
    });

    test('fromJson defaults', () {
      final json = {'id': 'p2', 'name': 'X', 'created_at': '2025-01-01T00:00:00Z'};
      final p = Program.fromJson(json);
      expect(p.durationWeeks, 4);
      expect(p.sessions, isEmpty);
      expect(p.assignedClientIds, isEmpty);
    });

    test('toJson', () {
      final json = {'id': 'p1', 'name': 'Y', 'duration_weeks': 6, 'created_at': '2025-01-01T00:00:00Z'};
      final out = Program.fromJson(json).toJson();
      expect(out['name'], 'Y');
      expect(out['duration_weeks'], 6);
    });
  });

  group('Session', () {
    test('dayName', () {
      final s = Session.fromJson({'id': 's1', 'title': 'Leg', 'day_of_week': 3});
      expect(s.dayName, 'Mercredi');
    });
  });

  group('Exercise', () {
    test('summary', () {
      final e = Exercise.fromJson({'id': 'e1', 'name': 'Squat', 'sets': 4, 'reps': 8, 'weight_kg': 100, 'rest_seconds': 120});
      expect(e.summary, '4×8 — 100.0kg');
    });
  });
}
