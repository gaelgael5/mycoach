import 'package:equatable/equatable.dart';

/// Rôle utilisateur — 3 valeurs possibles, hiérarchie inclusive.
enum UserRole {
  client,
  coach,
  admin;

  static UserRole fromString(String s) => switch (s) {
    'coach' => UserRole.coach,
    'admin' => UserRole.admin,
    _       => UserRole.client,
  };

  String get value => name; // 'client' | 'coach' | 'admin'

  bool get isCoach => this == UserRole.coach || this == UserRole.admin;
  bool get isAdmin => this == UserRole.admin;
}

/// Genre utilisateur.
enum Gender {
  male,
  female,
  other;

  static Gender? fromString(String? s) => switch (s) {
    'male'   => Gender.male,
    'female' => Gender.female,
    'other'  => Gender.other,
    _        => null,
  };

  String get value => name;
}

/// Modèle principal [User] — retourné par `GET /auth/me`.
///
/// Tous les champs PII sont déchiffrés côté backend avant d'être envoyés.
/// L'app Flutter ne stocke jamais les données sensibles en clair (sauf mémoire).
class User extends Equatable {
  const User({
    required this.id,
    required this.email,
    required this.role,
    required this.firstName,
    required this.lastName,
    this.phone,
    this.phoneVerifiedAt,
    this.gender,
    this.birthYear,
    this.avatarUrl,
    this.resolvedAvatarUrl,
    this.locale,
    this.timezone,
    this.country,
    this.isActive = true,
    this.createdAt,
  });

  final String id;
  final String email;
  final UserRole role;
  final String firstName;
  final String lastName;
  final String? phone;
  final DateTime? phoneVerifiedAt;
  final Gender? gender;
  final int? birthYear;
  final String? avatarUrl;

  /// URL d'avatar toujours valide (perso ou défaut selon genre).
  final String? resolvedAvatarUrl;

  final String? locale;      // BCP 47 ex: 'fr-FR'
  final String? timezone;    // IANA ex: 'Europe/Paris'
  final String? country;     // ISO 3166-1 alpha-2 ex: 'FR'
  final bool isActive;
  final DateTime? createdAt;

  String get fullName => '$firstName $lastName'.trim();

  bool get isPhoneVerified => phoneVerifiedAt != null;

  factory User.fromJson(Map<String, dynamic> json) => User(
    id:               json['id'] as String,
    email:            json['email'] as String,
    role:             UserRole.fromString(json['role'] as String? ?? 'client'),
    firstName:        json['first_name'] as String,
    lastName:         json['last_name'] as String,
    phone:            json['phone'] as String?,
    phoneVerifiedAt:  json['phone_verified_at'] != null
        ? DateTime.parse(json['phone_verified_at'] as String)
        : null,
    gender:           Gender.fromString(json['gender'] as String?),
    birthYear:        json['birth_year'] as int?,
    avatarUrl:        json['avatar_url'] as String?,
    resolvedAvatarUrl: json['resolved_avatar_url'] as String?,
    locale:           json['locale'] as String?,
    timezone:         json['timezone'] as String?,
    country:          json['country'] as String?,
    isActive:         json['is_active'] as bool? ?? true,
    createdAt:        json['created_at'] != null
        ? DateTime.parse(json['created_at'] as String)
        : null,
  );

  Map<String, dynamic> toJson() => {
    'id':                id,
    'email':             email,
    'role':              role.value,
    'first_name':        firstName,
    'last_name':         lastName,
    if (phone != null)              'phone':              phone,
    if (phoneVerifiedAt != null)    'phone_verified_at':  phoneVerifiedAt!.toIso8601String(),
    if (gender != null)             'gender':             gender!.value,
    if (birthYear != null)          'birth_year':         birthYear,
    if (avatarUrl != null)          'avatar_url':         avatarUrl,
    if (resolvedAvatarUrl != null)  'resolved_avatar_url': resolvedAvatarUrl,
    if (locale != null)             'locale':             locale,
    if (timezone != null)           'timezone':           timezone,
    if (country != null)            'country':            country,
    'is_active':  isActive,
    if (createdAt != null)          'created_at':         createdAt!.toIso8601String(),
  };

  User copyWith({
    String? firstName,
    String? lastName,
    String? phone,
    DateTime? phoneVerifiedAt,
    Gender? gender,
    int? birthYear,
    String? avatarUrl,
    String? resolvedAvatarUrl,
    String? locale,
    String? timezone,
    String? country,
  }) => User(
    id:               id,
    email:            email,
    role:             role,
    firstName:        firstName ?? this.firstName,
    lastName:         lastName ?? this.lastName,
    phone:            phone ?? this.phone,
    phoneVerifiedAt:  phoneVerifiedAt ?? this.phoneVerifiedAt,
    gender:           gender ?? this.gender,
    birthYear:        birthYear ?? this.birthYear,
    avatarUrl:        avatarUrl ?? this.avatarUrl,
    resolvedAvatarUrl:resolvedAvatarUrl ?? this.resolvedAvatarUrl,
    locale:           locale ?? this.locale,
    timezone:         timezone ?? this.timezone,
    country:          country ?? this.country,
    isActive:         isActive,
    createdAt:        createdAt,
  );

  @override
  List<Object?> get props => [id, email, role, firstName, lastName, phone,
    phoneVerifiedAt, gender, birthYear, locale, timezone, country, isActive];
}

/// Réponse de `POST /auth/login` et `POST /auth/register`.
class AuthResponse extends Equatable {
  const AuthResponse({
    required this.apiKey,
    required this.userId,
    required this.role,
    this.isNew = false,
  });

  final String apiKey;
  final String userId;
  final UserRole role;
  final bool isNew;   // true si nouvel utilisateur (Google OAuth)

  factory AuthResponse.fromJson(Map<String, dynamic> json) => AuthResponse(
    apiKey: json['api_key'] as String,
    userId: json['user_id'] as String,
    role:   UserRole.fromString(json['role'] as String? ?? 'client'),
    isNew:  json['is_new'] as bool? ?? false,
  );

  @override
  List<Object?> get props => [apiKey, userId, role, isNew];
}
