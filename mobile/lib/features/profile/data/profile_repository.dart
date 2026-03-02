import '../../../core/api/api_client.dart';

class CoachProfile {
  final String id;
  final String email;
  final String firstName;
  final String lastName;
  final String? phone;
  final String? bio;
  final List<String> specialties;
  final String? avatarUrl;
  final int clientCount;
  final int maxClients;
  final String plan;

  CoachProfile({
    required this.id,
    required this.email,
    required this.firstName,
    required this.lastName,
    this.phone,
    this.bio,
    this.specialties = const [],
    this.avatarUrl,
    this.clientCount = 0,
    this.maxClients = 15,
    this.plan = 'Free',
  });

  String get fullName => '$firstName $lastName';

  factory CoachProfile.fromJson(Map<String, dynamic> json) => CoachProfile(
        id: json['id'] as String,
        email: json['email'] as String,
        firstName: json['first_name'] as String,
        lastName: json['last_name'] as String,
        phone: json['phone'] as String?,
        bio: json['bio'] as String?,
        specialties: (json['specialties'] as List?)?.cast<String>() ?? [],
        avatarUrl: json['avatar_url'] as String?,
        clientCount: (json['client_count'] as num?)?.toInt() ?? 0,
        maxClients: (json['max_clients'] as num?)?.toInt() ?? 15,
        plan: json['plan'] as String? ?? 'Free',
      );
}

class ProfileRepository {
  final ApiClient _api;
  ProfileRepository(this._api);

  Future<CoachProfile> getProfile() async {
    final response = await _api.dio.get('/coaches/profile');
    return CoachProfile.fromJson(response.data as Map<String, dynamic>);
  }

  Future<CoachProfile> updateProfile(Map<String, dynamic> data) async {
    final response = await _api.dio.patch('/coaches/profile', data: data);
    return CoachProfile.fromJson(response.data as Map<String, dynamic>);
  }
}
