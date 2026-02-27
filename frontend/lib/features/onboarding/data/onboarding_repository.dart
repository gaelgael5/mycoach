import 'package:dio/dio.dart';
import '../../../shared/models/gym.dart';

/// Repository Onboarding — appels API profil utilisateur + coachs + gyms.
class OnboardingRepository {
  const OnboardingRepository(this._dio);

  final Dio _dio;

  // ── Profil utilisateur ──────────────────────────────────────────────────

  Future<Map<String, dynamic>> patchUserProfile(
    Map<String, dynamic> body,
  ) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/users/me/profile',
      data: body,
    );
    return response.data ?? {};
  }

  // ── Profil coach ────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getCoachProfile() async {
    final response = await _dio.get<Map<String, dynamic>>('/coaches/me/profile');
    return response.data ?? {};
  }

  Future<Map<String, dynamic>> patchCoachProfile(
    Map<String, dynamic> body,
  ) async {
    final response = await _dio.patch<Map<String, dynamic>>(
      '/coaches/me/profile',
      data: body,
    );
    return response.data ?? {};
  }

  // ── Gyms utilisateur ────────────────────────────────────────────────────

  Future<List<Gym>> getUserGyms() async {
    final response = await _dio.get<List<dynamic>>('/users/me/gyms');
    final list = response.data ?? [];
    return list
        .map((e) => Gym.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> addUserGym(String gymId) async {
    await _dio.post<void>('/users/me/gyms', data: {'gym_id': gymId});
  }

  Future<void> removeUserGym(String gymId) async {
    await _dio.delete<void>('/users/me/gyms/$gymId');
  }

  // ── Recherche salles ────────────────────────────────────────────────────

  Future<List<Gym>> searchGyms({String q = '', String city = '', int limit = 20}) async {
    final response = await _dio.get<List<dynamic>>(
      '/gyms/search',
      queryParameters: {
        if (q.isNotEmpty) 'q': q,
        if (city.isNotEmpty) 'city': city,
        'limit': limit,
      },
    );
    final list = response.data ?? [];
    return list
        .map((e) => _gymFromSearchJson(e as Map<String, dynamic>))
        .toList();
  }

  Gym _gymFromSearchJson(Map<String, dynamic> json) => Gym(
    id:         json['id'] as String? ?? '',
    name:       json['name'] as String? ?? '',
    brand:      json['brand'] as String? ?? '',
    address:    json['address'] as String? ?? '',
    city:       json['city'] as String? ?? '',
    postalCode: json['postal_code'] as String? ?? '',
    country:    json['country'] as String? ?? '',
    coachesCount: json['coaches_count'] as int? ?? 0,
    latitude:   (json['latitude'] as num?)?.toDouble(),
    longitude:  (json['longitude'] as num?)?.toDouble(),
  );

  // ── Enrollment link ─────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getEnrollmentInfo(String token) async {
    final response = await _dio.get<Map<String, dynamic>>('/enroll/$token');
    return response.data ?? {};
  }

  Future<void> enrollWithToken(String token) async {
    await _dio.post<void>('/users/me/enroll/$token');
  }
}
