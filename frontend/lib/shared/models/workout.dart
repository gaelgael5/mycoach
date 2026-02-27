import 'package:equatable/equatable.dart';

/// Type de séance de tracking.
enum WorkoutType {
  solo,     // Séance libre
  program;  // Séance de programme

  static WorkoutType fromString(String s) =>
      s == 'program' ? WorkoutType.program : WorkoutType.solo;

  String get value => name;
}

/// Ressenti post-séance (1 = épuisé → 5 = en feu).
enum WorkoutFeeling {
  exhausted(1, '😴'),
  okay(2, '😐'),
  good(3, '🙂'),
  strong(4, '💪'),
  fire(5, '🔥');

  const WorkoutFeeling(this.value, this.emoji);
  final int value;
  final String emoji;

  static WorkoutFeeling? fromInt(int? v) =>
      WorkoutFeeling.values.where((f) => f.value == v).firstOrNull;
}

/// Une série d'exercice.
class ExerciseSet extends Equatable {
  const ExerciseSet({
    required this.setNumber,
    required this.reps,
    required this.weightKg,
    this.isDone = false,
    this.isPr = false,
    this.notes,
  });

  final int setNumber;
  final int reps;
  final double weightKg; // stocké en kg, affiché selon préférence unité

  /// Série validée dans la session courante.
  final bool isDone;

  /// Personal Record détecté par le backend.
  final bool isPr;

  final String? notes;

  /// Volume de cette série en kg.
  double get volume => reps * weightKg;

  factory ExerciseSet.fromJson(Map<String, dynamic> json) => ExerciseSet(
    setNumber: json['set_number'] as int,
    reps:      json['reps'] as int,
    weightKg:  (json['weight_kg'] as num).toDouble(),
    isDone:    json['is_done'] as bool? ?? false,
    isPr:      json['is_pr'] as bool? ?? false,
    notes:     json['notes'] as String?,
  );

  Map<String, dynamic> toJson() => {
    'set_number': setNumber,
    'reps':       reps,
    'weight_kg':  weightKg,
    'is_done':    isDone,
    if (notes != null) 'notes': notes,
  };

  ExerciseSet copyWith({
    int? reps,
    double? weightKg,
    bool? isDone,
  }) => ExerciseSet(
    setNumber: setNumber,
    reps:      reps ?? this.reps,
    weightKg:  weightKg ?? this.weightKg,
    isDone:    isDone ?? this.isDone,
    isPr:      isPr,
    notes:     notes,
  );

  @override
  List<Object?> get props => [setNumber, reps, weightKg, isDone, isPr];
}

/// Un exercice dans une séance.
class WorkoutExercise extends Equatable {
  const WorkoutExercise({
    required this.id,
    required this.name,
    this.muscleGroups = const [],
    this.sets = const [],
    this.restTimerSeconds = 90,
    this.autoRest = true,
    this.notes,
    this.videoUrl,
  });

  final String id;
  final String name;
  final List<String> muscleGroups;
  final List<ExerciseSet> sets;

  /// Durée de repos configurée pour CET exercice (en secondes).
  final int restTimerSeconds;

  /// Timer de repos automatique activé pour cet exercice.
  final bool autoRest;

  final String? notes;
  final String? videoUrl;

  int get completedSets => sets.where((s) => s.isDone).length;

  /// Volume total de cet exercice (somme sets × reps × poids).
  double get totalVolume =>
      sets.fold(0.0, (sum, s) => sum + s.volume);

  /// Meilleure série (poids max).
  ExerciseSet? get bestSet => sets.isEmpty ? null
      : sets.reduce((a, b) => a.weightKg > b.weightKg ? a : b);

  factory WorkoutExercise.fromJson(Map<String, dynamic> json) => WorkoutExercise(
    id:               json['id'] as String,
    name:             json['name'] as String,
    muscleGroups:     (json['muscle_groups'] as List<dynamic>?)
        ?.map((e) => e as String).toList() ?? [],
    sets:             (json['sets'] as List<dynamic>?)
        ?.map((e) => ExerciseSet.fromJson(e as Map<String, dynamic>)).toList() ?? [],
    restTimerSeconds: json['rest_timer_seconds'] as int? ?? 90,
    autoRest:         json['auto_rest'] as bool? ?? true,
    notes:            json['notes'] as String?,
    videoUrl:         json['video_url'] as String?,
  );

  @override
  List<Object?> get props => [id, name, muscleGroups, sets, restTimerSeconds];
}

/// Résumé d'une séance terminée.
class WorkoutSummary extends Equatable {
  const WorkoutSummary({
    required this.sessionId,
    required this.durationSeconds,
    required this.exercises,
    required this.totalSets,
    required this.totalVolumeKg,
    this.feeling,
    this.hasNewPr = false,
    this.prExerciseName,
    this.prDescription,
  });

  final String sessionId;
  final int durationSeconds;
  final List<WorkoutExercise> exercises;
  final int totalSets;
  final double totalVolumeKg;
  final WorkoutFeeling? feeling;
  final bool hasNewPr;
  final String? prExerciseName;
  final String? prDescription;

  String get formattedDuration {
    final m = durationSeconds ~/ 60;
    final s = durationSeconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  @override
  List<Object?> get props => [sessionId, durationSeconds, totalVolumeKg, hasNewPr];
}
