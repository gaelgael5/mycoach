import 'package:equatable/equatable.dart';

class User extends Equatable {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String? phone;
  final String role;
  final String status;
  final String? avatarUrl;
  final String? resolvedAvatarUrl;
  final String? locale;
  final String? timezone;
  final String? country;
  final String? gender;
  final int? birthYear;
  final int profileCompletionPct;
  final bool emailVerified;
  final bool phoneVerified;

  const User({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phone,
    this.role = 'coach',
    this.status = 'unverified',
    this.avatarUrl,
    this.resolvedAvatarUrl,
    this.locale,
    this.timezone,
    this.country,
    this.gender,
    this.birthYear,
    this.profileCompletionPct = 0,
    this.emailVerified = false,
    this.phoneVerified = false,
  });

  String get fullName => '$firstName $lastName';

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        email: json['email'] as String? ?? '',
        firstName: json['first_name'] as String,
        lastName: json['last_name'] as String,
        phone: json['phone'] as String?,
        role: json['role'] as String? ?? 'coach',
        status: json['status'] as String? ?? 'unverified',
        avatarUrl: json['avatar_url'] as String?,
        resolvedAvatarUrl: json['resolved_avatar_url'] as String?,
        locale: json['locale'] as String?,
        timezone: json['timezone'] as String?,
        country: json['country'] as String?,
        gender: json['gender'] as String?,
        birthYear: (json['birth_year'] as num?)?.toInt(),
        profileCompletionPct: (json['profile_completion_pct'] as num?)?.toInt() ?? 0,
        emailVerified: json['email_verified'] as bool? ?? false,
        phoneVerified: json['phone_verified'] as bool? ?? false,
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'first_name': firstName,
        'last_name': lastName,
        'phone': phone,
        'role': role,
      };

  @override
  List<Object?> get props => [id, email, firstName, lastName, phone, role, status];
}
