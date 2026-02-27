import 'package:equatable/equatable.dart';

/// Un set d'exercice dans une session de performance.
class ExerciseSet extends Equatable {
  const ExerciseSet({
    required this.exerciseSlug,
    required this.exerciseName,
    this.reps,
    this.weight,
    this.durationSeconds,
    this.isPr = false,
  });

  final String exerciseSlug;
  final String exerciseName;
  final int? reps;
  final double? weight;
  final int? durationSeconds;
  final bool isPr;

  factory ExerciseSet.fromJson(Map<String, dynamic> json) => ExerciseSet(
        exerciseSlug: json['exercise_slug'] as String,
        exerciseName: json['exercise_name'] as String,
        reps: json['reps'] as int?,
        weight: (json['weight'] as num?)?.toDouble(),
        durationSeconds: json['duration_seconds'] as int?,
        isPr: json['is_pr'] as bool? ?? false,
      );

  Map<String, dynamic> toJson() => {
        'exercise_slug': exerciseSlug,
        'exercise_name': exerciseName,
        if (reps != null) 'reps': reps,
        if (weight != null) 'weight': weight,
        if (durationSeconds != null) 'duration_seconds': durationSeconds,
        'is_pr': isPr,
      };

  @override
  List<Object?> get props => [exerciseSlug, reps, weight, durationSeconds];
}

/// Session de performance d'un client.
class PerformanceSession extends Equatable {
  const PerformanceSession({
    required this.id,
    required this.date,
    this.coachFirstName,
    this.coachLastName,
    this.sets = const [],
  });

  final String id;
  final DateTime date;
  final String? coachFirstName;
  final String? coachLastName;
  final List<ExerciseSet> sets;

  String get coachFullName =>
      [coachFirstName, coachLastName].where((s) => s != null).join(' ');

  factory PerformanceSession.fromJson(Map<String, dynamic> json) =>
      PerformanceSession(
        id: json['id'] as String,
        date: DateTime.parse(json['date'] as String),
        coachFirstName: json['coach_first_name'] as String?,
        coachLastName: json['coach_last_name'] as String?,
        sets: (json['sets'] as List<dynamic>?)
                ?.map((e) => ExerciseSet.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  @override
  List<Object?> get props => [id, date];
}

/// Record personnel sur un exercice.
class PersonalRecord extends Equatable {
  const PersonalRecord({
    required this.exerciseSlug,
    required this.exerciseName,
    this.weight,
    this.reps,
    this.durationSeconds,
    required this.achievedAt,
  });

  final String exerciseSlug;
  final String exerciseName;
  final double? weight;
  final int? reps;
  final int? durationSeconds;
  final DateTime achievedAt;

  factory PersonalRecord.fromJson(Map<String, dynamic> json) => PersonalRecord(
        exerciseSlug: json['exercise_slug'] as String,
        exerciseName: json['exercise_name'] as String,
        weight: (json['weight'] as num?)?.toDouble(),
        reps: json['reps'] as int?,
        durationSeconds: json['duration_seconds'] as int?,
        achievedAt: DateTime.parse(json['achieved_at'] as String),
      );

  @override
  List<Object?> get props => [exerciseSlug, weight, reps, achievedAt];
}
