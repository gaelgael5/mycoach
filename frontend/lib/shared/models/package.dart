import 'package:equatable/equatable.dart';

/// Forfait de séances.
class Package extends Equatable {
  const Package({
    required this.id,
    required this.name,
    required this.sessionsCount,
    required this.priceCents,
    this.currency = 'EUR',
    required this.validityDays,
    this.isDiscovery = false,
  });

  final String id;
  final String name;
  final int sessionsCount;
  final int priceCents;
  final String currency;
  final int validityDays;
  final bool isDiscovery;

  /// Prix en euros (centimes ÷ 100).
  double get priceEur => priceCents / 100.0;

  factory Package.fromJson(Map<String, dynamic> json) => Package(
        id: json['id'] as String,
        name: json['name'] as String,
        sessionsCount: json['sessions_count'] as int,
        priceCents: json['price_cents'] as int,
        currency: json['currency'] as String? ?? 'EUR',
        validityDays: json['validity_days'] as int,
        isDiscovery: json['is_discovery'] as bool? ?? false,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'sessions_count': sessionsCount,
        'price_cents': priceCents,
        'currency': currency,
        'validity_days': validityDays,
        'is_discovery': isDiscovery,
      };

  @override
  List<Object?> get props =>
      [id, name, sessionsCount, priceCents, validityDays];
}

/// Solde forfait de l'utilisateur connecté.
class MyPackageBalance {
  const MyPackageBalance({
    this.activePackage,
    required this.sessionsRemaining,
    this.expiresAt,
  });

  final Package? activePackage;
  final int sessionsRemaining;
  final DateTime? expiresAt;

  factory MyPackageBalance.fromJson(Map<String, dynamic> json) =>
      MyPackageBalance(
        activePackage: json['active_package'] != null
            ? Package.fromJson(
                json['active_package'] as Map<String, dynamic>)
            : null,
        sessionsRemaining: json['sessions_remaining'] as int? ?? 0,
        expiresAt: json['expires_at'] != null
            ? DateTime.parse(json['expires_at'] as String)
            : null,
      );
}
