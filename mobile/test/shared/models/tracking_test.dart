import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/tracking.dart';

void main() {
  group('SessionCompletion', () {
    test('fromJson', () {
      final sc = SessionCompletion.fromJson({
        'id': 'sc1', 'session_id': 's1', 'completed_at': '2025-06-01T10:00:00Z',
        'exercise_logs': [
          {'exercise_id': 'e1', 'actual_weight_kg': 65, 'actual_reps': 10, 'actual_sets': 3}
        ],
      });
      expect(sc.sessionId, 's1');
      expect(sc.exerciseLogs.length, 1);
      expect(sc.exerciseLogs.first.actualWeightKg, 65.0);
    });
  });

  group('ExerciseLog', () {
    test('toJson roundtrip', () {
      final log = ExerciseLog.fromJson({
        'exercise_id': 'e1', 'actual_weight_kg': 80.5, 'actual_reps': 8, 'actual_sets': 4,
      });
      final json = log.toJson();
      expect(json['exercise_id'], 'e1');
      expect(json['actual_weight_kg'], 80.5);
    });
  });

  group('Metric', () {
    test('fromJson and toJson', () {
      final m = Metric.fromJson({
        'id': 'm1', 'weight_kg': 78.5, 'waist_cm': 82.0, 'date': '2025-06-01',
      });
      expect(m.weightKg, 78.5);
      expect(m.waistCm, 82.0);
      final json = m.toJson();
      expect(json['weight_kg'], 78.5);
      expect(json['date'], startsWith('2025-06-01'));
    });

    test('optional fields', () {
      final m = Metric.fromJson({'weight_kg': 70, 'date': '2025-01-01'});
      expect(m.id, isNull);
      expect(m.waistCm, isNull);
    });
  });
}
