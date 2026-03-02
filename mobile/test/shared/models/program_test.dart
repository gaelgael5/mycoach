import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/program.dart';

void main() {
  group('Program', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': '123',
        'name': 'Full Body',
        'description': 'A full body program',
        'duration_weeks': 4,
        'level': 'beginner',
        'goal': 'general_fitness',
        'is_ai_generated': false,
        'archived': false,
        'created_at': '2026-01-01T00:00:00Z',
        'planned_sessions': [],
      };
      final p = Program.fromJson(json);
      expect(p.id, '123');
      expect(p.name, 'Full Body');
      expect(p.durationWeeks, 4);
      expect(p.level, 'beginner');
      expect(p.sessions, isEmpty);
    });

    test('toCreateJson produces correct output', () {
      final p = Program(
        id: '',
        name: 'Test',
        durationWeeks: 6,
        level: 'advanced',
        goal: 'strength',
        createdAt: DateTime.now(),
      );
      final json = p.toCreateJson();
      expect(json['name'], 'Test');
      expect(json['duration_weeks'], 6);
      expect(json['level'], 'advanced');
    });
  });

  group('PlannedSession', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 's1',
        'session_name': 'Jour jambes',
        'day_of_week': 1,
        'rest_seconds': 90,
        'planned_exercises': [],
      };
      final s = PlannedSession.fromJson(json);
      expect(s.sessionName, 'Jour jambes');
      expect(s.dayOfWeek, 1);
      expect(s.dayName, 'Lundi');
    });
  });

  group('PlannedExercise', () {
    test('summary format', () {
      const e = PlannedExercise(
        exerciseTypeId: 'ex1',
        targetSets: 4,
        targetReps: 12,
        targetWeightKg: 80,
      );
      expect(e.summary, '4×12 — 80.0kg');
    });

    test('summary without weight', () {
      const e = PlannedExercise(
        exerciseTypeId: 'ex1',
        targetSets: 3,
        targetReps: 10,
      );
      expect(e.summary, '3×10');
    });
  });

  group('ExerciseType', () {
    test('fromJson parses correctly', () {
      final json = {
        'id': 'et1',
        'name_key': 'squat',
        'category': 'legs',
        'difficulty': 'intermediate',
        'video_url': 'https://youtube.com/watch?v=123',
        'thumbnail_url': null,
        'instructions': 'Stand with feet shoulder-width apart',
        'muscles': ['quadriceps', 'glutes'],
      };
      final et = ExerciseType.fromJson(json);
      expect(et.nameKey, 'squat');
      expect(et.muscles, ['quadriceps', 'glutes']);
    });
  });
}
