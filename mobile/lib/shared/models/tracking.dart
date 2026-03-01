import 'package:equatable/equatable.dart';

class SessionCompletion extends Equatable {
  final String id;
  final String sessionId;
  final DateTime completedAt;
  final List<ExerciseLog> exerciseLogs;

  const SessionCompletion({
    required this.id,
    required this.sessionId,
    required this.completedAt,
    this.exerciseLogs = const [],
  });

  factory SessionCompletion.fromJson(Map<String, dynamic> json) => SessionCompletion(
        id: json['id'] as String,
        sessionId: json['session_id'] as String,
        completedAt: DateTime.parse(json['completed_at'] as String),
        exerciseLogs: (json['exercise_logs'] as List<dynamic>?)
                ?.map((e) => ExerciseLog.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  @override
  List<Object?> get props => [id, sessionId, completedAt];
}

class ExerciseLog extends Equatable {
  final String exerciseId;
  final double actualWeightKg;
  final int actualReps;
  final int actualSets;

  const ExerciseLog({
    required this.exerciseId,
    required this.actualWeightKg,
    required this.actualReps,
    required this.actualSets,
  });

  factory ExerciseLog.fromJson(Map<String, dynamic> json) => ExerciseLog(
        exerciseId: json['exercise_id'] as String,
        actualWeightKg: (json['actual_weight_kg'] as num).toDouble(),
        actualReps: json['actual_reps'] as int,
        actualSets: json['actual_sets'] as int,
      );

  Map<String, dynamic> toJson() => {
        'exercise_id': exerciseId,
        'actual_weight_kg': actualWeightKg,
        'actual_reps': actualReps,
        'actual_sets': actualSets,
      };

  @override
  List<Object?> get props => [exerciseId, actualWeightKg, actualReps, actualSets];
}

class Metric extends Equatable {
  final String? id;
  final double weightKg;
  final double? waistCm;
  final DateTime date;

  const Metric({
    this.id,
    required this.weightKg,
    this.waistCm,
    required this.date,
  });

  factory Metric.fromJson(Map<String, dynamic> json) => Metric(
        id: json['id'] as String?,
        weightKg: (json['weight_kg'] as num).toDouble(),
        waistCm: (json['waist_cm'] as num?)?.toDouble(),
        date: DateTime.parse(json['date'] as String),
      );

  Map<String, dynamic> toJson() => {
        'weight_kg': weightKg,
        'waist_cm': waistCm,
        'date': date.toIso8601String().substring(0, 10),
      };

  @override
  List<Object?> get props => [id, weightKg, waistCm, date];
}
