import 'package:equatable/equatable.dart';

/// Créneau retourné par GET /coaches/{id}/availability.
class Slot extends Equatable {
  const Slot({
    required this.id,
    required this.startAt,
    required this.endAt,
    required this.status,
    this.priceCents,
  });

  final String id;
  final DateTime startAt;
  final DateTime endAt;

  /// "available" | "booked" | "mine" | "blocked"
  final String status;
  final int? priceCents;

  bool get isAvailable => status == 'available';
  bool get isBooked => status == 'booked';
  bool get isMine => status == 'mine';
  bool get isBlocked => status == 'blocked';

  factory Slot.fromJson(Map<String, dynamic> json) => Slot(
        id: json['id'] as String,
        startAt: DateTime.parse(json['start_at'] as String),
        endAt: DateTime.parse(json['end_at'] as String),
        status: json['status'] as String? ?? 'available',
        priceCents: json['price_cents'] as int?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'start_at': startAt.toUtc().toIso8601String(),
        'end_at': endAt.toUtc().toIso8601String(),
        'status': status,
        if (priceCents != null) 'price_cents': priceCents,
      };

  @override
  List<Object?> get props => [id, startAt, endAt, status];
}
