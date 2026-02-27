import 'package:equatable/equatable.dart';

/// Type de feedback.
enum FeedbackType {
  suggestion,
  bugReport;

  static FeedbackType fromString(String s) =>
      s == 'bug_report' ? FeedbackType.bugReport : FeedbackType.suggestion;

  String get value => this == FeedbackType.bugReport ? 'bug_report' : 'suggestion';
}

/// Statut d'un feedback.
enum FeedbackStatus {
  pending,
  inReview,
  done;

  static FeedbackStatus fromString(String s) => switch (s) {
    'in_review' => FeedbackStatus.inReview,
    'done'      => FeedbackStatus.done,
    _           => FeedbackStatus.pending,
  };

  String get value => switch (this) {
    FeedbackStatus.pending  => 'pending',
    FeedbackStatus.inReview => 'in_review',
    FeedbackStatus.done     => 'done',
  };
}

/// Feedback utilisateur (suggestion ou signalement de bug).
class FeedbackItem extends Equatable {
  const FeedbackItem({
    required this.id,
    required this.type,
    required this.title,
    required this.description,
    required this.status,
    required this.createdAt,
  });

  final String id;
  final FeedbackType type;
  final String title;
  final String description;
  final FeedbackStatus status;
  final DateTime createdAt;

  factory FeedbackItem.fromJson(Map<String, dynamic> json) => FeedbackItem(
    id:          json['id'] as String,
    type:        FeedbackType.fromString(json['type'] as String? ?? 'suggestion'),
    title:       json['title'] as String,
    description: json['description'] as String,
    status:      FeedbackStatus.fromString(json['status'] as String? ?? 'pending'),
    createdAt:   DateTime.parse(json['created_at'] as String),
  );

  Map<String, dynamic> toJson() => {
    'id':          id,
    'type':        type.value,
    'title':       title,
    'description': description,
    'status':      status.value,
    'created_at':  createdAt.toIso8601String(),
  };

  @override
  List<Object?> get props => [id, type, title, status, createdAt];
}
