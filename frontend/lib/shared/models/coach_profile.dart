import 'package:equatable/equatable.dart';
import 'gym.dart';
import 'social_link.dart';

/// Profil public d'un coach — utilisé dans la recherche et sur la fiche coach.
class CoachProfile extends Equatable {
  const CoachProfile({
    required this.id,
    required this.userId,
    required this.firstName,
    required this.lastName,
    this.bio,
    this.resolvedAvatarUrl,
    this.isCertified = false,
    this.offersDiscovery = false,
    this.discoveryPrice = 0,
    this.discoveryDurationMin = 60,
    this.sessionPriceCents,
    this.currency = 'EUR',
    this.rating,
    this.reviewCount = 0,
    this.specialties = const [],
    this.certifications = const [],
    this.gyms = const [],
    this.socialLinks = const [],
    this.showsDiscoveryBadge = false,
  });

  final String id;
  final String userId;
  final String firstName;
  final String lastName;
  final String? bio;
  final String? resolvedAvatarUrl;
  final bool isCertified;

  /// Le coach propose une séance de première découverte.
  final bool offersDiscovery;

  /// Prix de la découverte en centimes (0 = gratuite).
  final int discoveryPrice;

  /// Durée de la découverte en minutes.
  final int discoveryDurationMin;

  /// Prix séance unitaire en centimes.
  final int? sessionPriceCents;

  final String currency;

  /// Note moyenne (null si pas encore d'avis).
  final double? rating;

  final int reviewCount;

  final List<String> specialties;
  final List<Certification> certifications;
  final List<Gym> gyms;
  final List<SocialLink> socialLinks;

  /// `true` si ce badge doit être affiché pour l'utilisateur courant
  /// (calculé côté backend : offersDiscovery=true ET pas de relation préalable).
  final bool showsDiscoveryBadge;

  String get fullName => '$firstName $lastName'.trim();

  /// Prix séance formaté (centimes → €).
  String get formattedPrice =>
      sessionPriceCents != null ? '${sessionPriceCents! ~/ 100}€' : '—';

  factory CoachProfile.fromJson(Map<String, dynamic> json) => CoachProfile(
    id:                  json['id'] as String,
    userId:              json['user_id'] as String,
    firstName:           json['first_name'] as String,
    lastName:            json['last_name'] as String,
    bio:                 json['bio'] as String?,
    resolvedAvatarUrl:   json['resolved_avatar_url'] as String?,
    isCertified:         json['is_certified'] as bool? ?? false,
    offersDiscovery:     json['offers_discovery'] as bool? ?? false,
    discoveryPrice:      json['discovery_price'] as int? ?? 0,
    discoveryDurationMin:json['discovery_duration_min'] as int? ?? 60,
    sessionPriceCents:   json['session_price_cents'] as int?,
    currency:            json['currency'] as String? ?? 'EUR',
    rating:              (json['rating'] as num?)?.toDouble(),
    reviewCount:         json['review_count'] as int? ?? 0,
    specialties:         (json['specialties'] as List<dynamic>?)
        ?.map((e) => e as String).toList() ?? [],
    certifications:      (json['certifications'] as List<dynamic>?)
        ?.map((e) => Certification.fromJson(e as Map<String, dynamic>)).toList() ?? [],
    gyms:                (json['gyms'] as List<dynamic>?)
        ?.map((e) => Gym.fromJson(e as Map<String, dynamic>)).toList() ?? [],
    socialLinks:         (json['social_links'] as List<dynamic>?)
        ?.map((e) => SocialLink.fromJson(e as Map<String, dynamic>)).toList() ?? [],
    showsDiscoveryBadge: json['shows_discovery_badge'] as bool? ?? false,
  );

  @override
  List<Object?> get props => [id, userId, firstName, lastName, isCertified,
    offersDiscovery, sessionPriceCents, rating];
}

/// Certification d'un coach.
class Certification extends Equatable {
  const Certification({
    required this.id,
    required this.name,
    required this.organization,
    this.year,
    this.isVerified = false,
  });

  final String id;
  final String name;
  final String organization;
  final int? year;
  final bool isVerified;

  factory Certification.fromJson(Map<String, dynamic> json) => Certification(
    id:           json['id'] as String,
    name:         json['name'] as String,
    organization: json['organization'] as String,
    year:         json['year'] as int?,
    isVerified:   json['is_verified'] as bool? ?? false,
  );

  @override
  List<Object?> get props => [id, name, organization, year, isVerified];
}
