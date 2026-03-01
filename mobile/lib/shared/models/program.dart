import 'package:equatable/equatable.dart';

class Program extends Equatable {
  final String id;
  final String name;
  final String? description;
  final int durationWeeks;
  final List<Session> sessions;
  final List<String> assignedClientIds;
  final DateTime createdAt;

  const Program({
    required this.id,
    required this.name,
    this.description,
    required this.durationWeeks,
    this.sessions = const [],
    this.assignedClientIds = const [],
    required this.createdAt,
  });

  factory Program.fromJson(Map<String, dynamic> json) => Program(
        id: json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String?,
        durationWeeks: json['duration_weeks'] as int? ?? 4,
        sessions: (json['sessions'] as List<dynamic>?)
                ?.map((s) => Session.fromJson(s as Map<String, dynamic>))
                .toList() ??
            [],
        assignedClientIds: (json['assigned_client_ids'] as List<dynamic>?)
                ?.map((e) => e as String)
                .toList() ??
            [],
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  Map<String, dynamic> toJson() => {
        'name': name,
        'description': description,
        'duration_weeks': durationWeeks,
      };

  @override
  List<Object?> get props => [id, name, description, durationWeeks, sessions, assignedClientIds];
}

class Session extends Equatable {
  final String id;
  final String title;
  final int dayOfWeek; // 1=Monday .. 7=Sunday
  final List<Exercise> exercises;

  const Session({
    required this.id,
    required this.title,
    required this.dayOfWeek,
    this.exercises = const [],
  });

  static const dayNames = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
  String get dayName => dayNames[dayOfWeek - 1];

  factory Session.fromJson(Map<String, dynamic> json) => Session(
        id: json['id'] as String,
        title: json['title'] as String,
        dayOfWeek: json['day_of_week'] as int,
        exercises: (json['exercises'] as List<dynamic>?)
                ?.map((e) => Exercise.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  Map<String, dynamic> toJson() => {
        'title': title,
        'day_of_week': dayOfWeek,
      };

  @override
  List<Object?> get props => [id, title, dayOfWeek, exercises];
}

class Exercise extends Equatable {
  final String id;
  final String name;
  final int sets;
  final int reps;
  final double weightKg;
  final int restSeconds;
  final String? videoUrl;

  const Exercise({
    required this.id,
    required this.name,
    required this.sets,
    required this.reps,
    required this.weightKg,
    required this.restSeconds,
    this.videoUrl,
  });

  String get summary => '${sets}×$reps — ${weightKg}kg';

  bool get hasVideo => videoUrl != null && videoUrl!.isNotEmpty;

  factory Exercise.fromJson(Map<String, dynamic> json) => Exercise(
        id: json['id'] as String,
        name: json['name'] as String,
        sets: json['sets'] as int,
        reps: json['reps'] as int,
        weightKg: (json['weight_kg'] as num).toDouble(),
        restSeconds: json['rest_seconds'] as int? ?? 60,
        videoUrl: json['video_url'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'name': name,
        'sets': sets,
        'reps': reps,
        'weight_kg': weightKg,
        'rest_seconds': restSeconds,
        if (videoUrl != null) 'video_url': videoUrl,
      };

  @override
  List<Object?> get props => [id, name, sets, reps, weightKg, restSeconds, videoUrl];
}
