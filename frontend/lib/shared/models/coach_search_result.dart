import 'package:equatable/equatable.dart';

/// Résultat de recherche coach — retourné par GET /coaches/search.
class CoachSearchResult extends Equatable {
  const CoachSearchResult({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.resolvedAvatarUrl,
    this.bio,
    this.city,
    this.specialties = const [],
    this.hourlyRate,
    this.currency = 'EUR',
    this.offersDiscovery = false,
    this.isCertified = false,
    this.rating,
    this.reviewCount = 0,
  });

  final String id;
  final String firstName;
  final String lastName;
  final String? resolvedAvatarUrl;
  final String? bio;
  final String? city;
  final List<String> specialties;
  final int? hourlyRate;
  final String currency;
  final bool offersDiscovery;
  final bool isCertified;
  final double? rating;
  final int reviewCount;

  String get fullName => '$firstName $lastName'.trim();

  factory CoachSearchResult.fromJson(Map<String, dynamic> json) =>
      CoachSearchResult(
        id: json['id'] as String,
        firstName: json['first_name'] as String,
        lastName: json['last_name'] as String,
        resolvedAvatarUrl: json['resolved_avatar_url'] as String?,
        bio: json['bio'] as String?,
        city: json['city'] as String?,
        specialties: (json['specialties'] as List<dynamic>?)
                ?.map((e) => e as String)
                .toList() ??
            [],
        hourlyRate: json['hourly_rate'] as int?,
        currency: json['currency'] as String? ?? 'EUR',
        offersDiscovery: json['offers_discovery'] as bool? ?? false,
        isCertified: json['is_certified'] as bool? ?? false,
        rating: (json['rating'] as num?)?.toDouble(),
        reviewCount: json['review_count'] as int? ?? 0,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'first_name': firstName,
        'last_name': lastName,
        if (resolvedAvatarUrl != null)
          'resolved_avatar_url': resolvedAvatarUrl,
        if (bio != null) 'bio': bio,
        if (city != null) 'city': city,
        'specialties': specialties,
        if (hourlyRate != null) 'hourly_rate': hourlyRate,
        'currency': currency,
        'offers_discovery': offersDiscovery,
        'is_certified': isCertified,
        if (rating != null) 'rating': rating,
        'review_count': reviewCount,
      };

  @override
  List<Object?> get props =>
      [id, firstName, lastName, city, hourlyRate, rating];
}
