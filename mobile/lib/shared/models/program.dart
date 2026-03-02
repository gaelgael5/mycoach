import 'package:equatable/equatable.dart';

class Program extends Equatable {
  final String id;
  final String name;
  final String? description;
  final int durationWeeks;
  final String level;
  final String goal;
  final bool isAiGenerated;
  final bool archived;
  final List<PlannedSession> sessions;
  final DateTime createdAt;

  const Program({
    required this.id,
    required this.name,
    this.description,
    required this.durationWeeks,
    this.level = 'beginner',
    this.goal = 'general_fitness',
    this.isAiGenerated = false,
    this.archived = false,
    this.sessions = const [],
    required this.createdAt,
  });

  factory Program.fromJson(Map<String, dynamic> json) => Program(
        id: json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String?,
        durationWeeks: json['duration_weeks'] as int? ?? 4,
        level: json['level'] as String? ?? 'beginner',
        goal: json['goal'] as String? ?? 'general_fitness',
        isAiGenerated: json['is_ai_generated'] as bool? ?? false,
        archived: json['archived'] as bool? ?? false,
        sessions: (json['planned_sessions'] as List<dynamic>?)
                ?.map((s) => PlannedSession.fromJson(s as Map<String, dynamic>))
                .toList() ??
            [],
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  Map<String, dynamic> toCreateJson() => {
        'name': name,
        if (description != null) 'description': description,
        'duration_weeks': durationWeeks,
        'level': level,
        'goal': goal,
        'planned_sessions': sessions.map((s) => s.toCreateJson()).toList(),
      };

  @override
  List<Object?> get props => [id, name, durationWeeks, level, goal, archived, sessions];
}

class PlannedSession extends Equatable {
  final String? id;
  final String sessionName;
  final int dayOfWeek;
  final int? estimatedDurationMin;
  final int restSeconds;
  final List<PlannedExercise> exercises;

  const PlannedSession({
    this.id,
    required this.sessionName,
    required this.dayOfWeek,
    this.estimatedDurationMin,
    this.restSeconds = 60,
    this.exercises = const [],
  });

  static const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
  String get dayName => dayNames[dayOfWeek.clamp(1, 7) - 1];

  factory PlannedSession.fromJson(Map<String, dynamic> json) => PlannedSession(
        id: json['id'] as String?,
        sessionName: json['session_name'] as String? ?? json['title'] as String? ?? '',
        dayOfWeek: json['day_of_week'] as int? ?? 1,
        estimatedDurationMin: json['estimated_duration_min'] as int?,
        restSeconds: json['rest_seconds'] as int? ?? 60,
        exercises: (json['planned_exercises'] as List<dynamic>?)
                ?.map((e) => PlannedExercise.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  Map<String, dynamic> toCreateJson() => {
        'day_of_week': dayOfWeek,
        'session_name': sessionName,
        if (estimatedDurationMin != null) 'estimated_duration_min': estimatedDurationMin,
        'rest_seconds': restSeconds,
        'planned_exercises': exercises.map((e) => e.toCreateJson()).toList(),
      };

  @override
  List<Object?> get props => [id, sessionName, dayOfWeek, exercises];
}

class PlannedExercise extends Equatable {
  final String? id;
  final String exerciseTypeId;
  final String? exerciseName; // from join, display only
  final int targetSets;
  final int targetReps;
  final double? targetWeightKg;
  final int orderIndex;

  const PlannedExercise({
    this.id,
    required this.exerciseTypeId,
    this.exerciseName,
    this.targetSets = 3,
    this.targetReps = 10,
    this.targetWeightKg,
    this.orderIndex = 0,
  });

  String get summary => '${targetSets}×$targetReps${targetWeightKg != null ? ' — ${targetWeightKg}kg' : ''}';

  factory PlannedExercise.fromJson(Map<String, dynamic> json) => PlannedExercise(
        id: json['id'] as String?,
        exerciseTypeId: json['exercise_type_id'] as String,
        exerciseName: json['exercise_name'] as String?,
        targetSets: json['target_sets'] as int? ?? 3,
        targetReps: json['target_reps'] as int? ?? 10,
        targetWeightKg: (json['target_weight_kg'] as num?)?.toDouble(),
        orderIndex: json['order_index'] as int? ?? 0,
      );

  Map<String, dynamic> toCreateJson() => {
        'exercise_type_id': exerciseTypeId,
        'target_sets': targetSets,
        'target_reps': targetReps,
        if (targetWeightKg != null) 'target_weight_kg': targetWeightKg,
        'order_index': orderIndex,
      };

  @override
  List<Object?> get props => [id, exerciseTypeId, targetSets, targetReps, targetWeightKg];
}

// Exercise type from the library
class ExerciseType extends Equatable {
  final String id;
  final String nameKey;
  final String category;
  final String difficulty;
  final String? videoUrl;
  final String? thumbnailUrl;
  final String? instructions;
  final List<String> muscles;

  const ExerciseType({
    required this.id,
    required this.nameKey,
    required this.category,
    required this.difficulty,
    this.videoUrl,
    this.thumbnailUrl,
    this.instructions,
    this.muscles = const [],
  });

  factory ExerciseType.fromJson(Map<String, dynamic> json) => ExerciseType(
        id: json['id'] as String,
        nameKey: json['name_key'] as String,
        category: json['category'] as String,
        difficulty: json['difficulty'] as String,
        videoUrl: json['video_url'] as String?,
        thumbnailUrl: json['thumbnail_url'] as String?,
        instructions: json['instructions'] as String?,
        muscles: (json['muscles'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      );

  @override
  List<Object?> get props => [id, nameKey, category, difficulty];
}
