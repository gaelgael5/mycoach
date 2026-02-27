import 'package:equatable/equatable.dart';

/// Exercice dans un programme.
class ProgramExercise extends Equatable {
  const ProgramExercise({
    required this.exerciseSlug,
    required this.exerciseName,
    this.sets,
    this.reps,
    this.weight,
    this.restSeconds,
  });

  final String exerciseSlug;
  final String exerciseName;
  final int? sets;
  final int? reps;
  final double? weight;
  final int? restSeconds;

  factory ProgramExercise.fromJson(Map<String, dynamic> json) =>
      ProgramExercise(
        exerciseSlug: json['exercise_slug'] as String,
        exerciseName: json['exercise_name'] as String,
        sets: json['sets'] as int?,
        reps: json['reps'] as int?,
        weight: (json['weight'] as num?)?.toDouble(),
        restSeconds: json['rest_seconds'] as int?,
      );

  @override
  List<Object?> get props => [exerciseSlug, sets, reps, weight];
}

/// Jour de programme.
class ProgramDay extends Equatable {
  const ProgramDay({
    required this.dayNumber,
    this.name,
    this.exercises = const [],
  });

  final int dayNumber;
  final String? name;
  final List<ProgramExercise> exercises;

  factory ProgramDay.fromJson(Map<String, dynamic> json) => ProgramDay(
        dayNumber: json['day_number'] as int,
        name: json['name'] as String?,
        exercises: (json['exercises'] as List<dynamic>?)
                ?.map((e) =>
                    ProgramExercise.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  @override
  List<Object?> get props => [dayNumber, name, exercises];
}

/// Programme assigné par un coach.
class Program extends Equatable {
  const Program({
    required this.id,
    required this.name,
    this.description,
    this.days = const [],
  });

  final String id;
  final String name;
  final String? description;
  final List<ProgramDay> days;

  factory Program.fromJson(Map<String, dynamic> json) => Program(
        id: json['id'] as String,
        name: json['name'] as String,
        description: json['description'] as String?,
        days: (json['days'] as List<dynamic>?)
                ?.map(
                    (e) => ProgramDay.fromJson(e as Map<String, dynamic>))
                .toList() ??
            [],
      );

  @override
  List<Object?> get props => [id, name];
}

/// Entrée de liste d'attente.
class WaitlistEntry extends Equatable {
  const WaitlistEntry({
    required this.id,
    required this.bookingId,
    required this.slotStartAt,
    required this.coachName,
    required this.position,
    required this.createdAt,
  });

  final String id;
  final String bookingId;
  final DateTime slotStartAt;
  final String coachName;
  final int position;
  final DateTime createdAt;

  factory WaitlistEntry.fromJson(Map<String, dynamic> json) => WaitlistEntry(
        id: json['id'] as String,
        bookingId: json['booking_id'] as String,
        slotStartAt: DateTime.parse(json['slot_start_at'] as String),
        coachName: json['coach_name'] as String? ?? '',
        position: json['position'] as int? ?? 0,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  @override
  List<Object?> get props => [id, bookingId, position];
}

/// Événement agenda.
class AgendaEvent extends Equatable {
  const AgendaEvent({
    required this.id,
    required this.title,
    required this.startAt,
    required this.endAt,
    required this.status,
    this.coachName,
  });

  final String id;
  final String title;
  final DateTime startAt;
  final DateTime endAt;
  final String status;
  final String? coachName;

  bool get isConfirmed => status == 'confirmed';
  bool get isPending => status == 'pending_coach_validation';

  factory AgendaEvent.fromJson(Map<String, dynamic> json) => AgendaEvent(
        id: json['id'] as String,
        title: json['title'] as String? ?? '',
        startAt: DateTime.parse(json['start_at'] as String),
        endAt: DateTime.parse(json['end_at'] as String),
        status: json['status'] as String? ?? 'confirmed',
        coachName: json['coach_name'] as String?,
      );

  @override
  List<Object?> get props => [id, startAt, endAt, status];
}
