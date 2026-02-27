import 'package:dio/dio.dart';
import '../../../shared/models/user.dart';

/// Accès direct à l'API backend pour toutes les opérations d'authentification.
/// Toutes les méthodes lancent un [AppDioException] en cas d'erreur HTTP.
class AuthRepository {
  AuthRepository(this._dio);

  final Dio _dio;

  // ── Login ────────────────────────────────────────────────────────────────

  Future<({String apiKey, User user})> login({
    required String email,
    required String password,
  }) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: {'email': email, 'password': password},
    );
    final data = resp.data!;
    final userMap = data['user'] as Map<String, dynamic>;
    return (
      apiKey: data['api_key'] as String,
      user: User.fromJson(userMap),
    );
  }

  // ── Register ─────────────────────────────────────────────────────────────

  Future<({String apiKey, User user})> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
    String? phone,
    String? gender,
    int? birthYear,
  }) async {
    final body = <String, dynamic>{
      'email': email,
      'password': password,
      'first_name': firstName,
      'last_name': lastName,
      'role': role,
      if (phone != null) 'phone': phone,
      if (gender != null) 'gender': gender,
      if (birthYear != null) 'birth_year': birthYear,
    };
    final resp = await _dio.post<Map<String, dynamic>>(
      '/auth/register',
      data: body,
    );
    final data = resp.data!;
    final userMap = data['user'] as Map<String, dynamic>;
    return (
      apiKey: data['api_key'] as String,
      user: User.fromJson(userMap),
    );
  }

  // ── Logout ───────────────────────────────────────────────────────────────

  Future<void> logout() async {
    await _dio.post<void>('/auth/logout');
  }

  // ── Email Verification ───────────────────────────────────────────────────

  Future<void> requestEmailVerification() async {
    await _dio.post<void>('/auth/verify-email/request');
  }

  Future<bool> confirmEmailVerification(String token) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/auth/verify-email/confirm',
      data: {'token': token},
    );
    return (resp.data?['verified'] as bool?) ?? false;
  }

  // ── Phone Verification ───────────────────────────────────────────────────

  Future<void> requestPhoneVerification() async {
    await _dio.post<void>('/auth/verify-phone/request');
  }

  Future<bool> confirmPhoneVerification(String code) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/auth/verify-phone/confirm',
      data: {'code': code},
    );
    return (resp.data?['verified'] as bool?) ?? false;
  }

  // ── Password ─────────────────────────────────────────────────────────────

  Future<void> forgotPassword(String email) async {
    await _dio.post<void>('/auth/forgot-password', data: {'email': email});
  }

  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    await _dio.post<void>(
      '/auth/reset-password',
      data: {'token': token, 'new_password': newPassword},
    );
  }

  // ── Me ───────────────────────────────────────────────────────────────────

  Future<User> getMe() async {
    final resp = await _dio.get<Map<String, dynamic>>('/users/me');
    return User.fromJson(resp.data!);
  }
}
