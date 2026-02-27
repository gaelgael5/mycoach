import 'package:equatable/equatable.dart';

/// Paiement effectué par le client.
class Payment extends Equatable {
  const Payment({
    required this.id,
    required this.amountCents,
    this.currency = 'EUR',
    required this.status,
    required this.method,
    required this.createdAt,
    this.description,
  });

  final String id;
  final int amountCents;
  final String currency;

  /// "pending" | "completed" | "failed" | "refunded"
  final String status;
  final String method;
  final DateTime createdAt;
  final String? description;

  double get amountEur => amountCents / 100.0;

  factory Payment.fromJson(Map<String, dynamic> json) => Payment(
        id: json['id'] as String,
        amountCents: json['amount_cents'] as int,
        currency: json['currency'] as String? ?? 'EUR',
        status: json['status'] as String,
        method: json['method'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        description: json['description'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'amount_cents': amountCents,
        'currency': currency,
        'status': status,
        'method': method,
        'created_at': createdAt.toUtc().toIso8601String(),
        if (description != null) 'description': description,
      };

  @override
  List<Object?> get props => [id, amountCents, status, createdAt];
}
