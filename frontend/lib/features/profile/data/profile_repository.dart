import 'dart:io';
import 'package:dio/dio.dart';
import '../../../shared/models/user.dart';

/// Repository pour les opérations sur le profil utilisateur.
class ProfileRepository {
  const ProfileRepository(this._dio);

  final Dio _dio;

  /// Récupère le profil de l'utilisateur connecté.
  Future<User> getMe() async {
    final response = await _dio.get<Map<String, dynamic>>('/users/me');
    return User.fromJson(response.data!);
  }

  /// Met à jour le profil de l'utilisateur.
  Future<User> updateProfile({
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
    String? phone,
    String? timezone,
  }) async {
    final body = <String, dynamic>{
      if (firstName != null) 'first_name': firstName,
      if (lastName != null)  'last_name':  lastName,
      if (gender != null)    'gender':     gender,
      if (birthYear != null) 'birth_year': birthYear,
      if (phone != null)     'phone':      phone,
      if (timezone != null)  'timezone':   timezone,
    };
    final response = await _dio.patch<Map<String, dynamic>>(
      '/users/me/profile',
      data: body,
    );
    return User.fromJson(response.data!);
  }

  /// Télécharge un avatar.
  Future<String> uploadAvatar(File file) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(file.path),
    });
    final response = await _dio.post<Map<String, dynamic>>(
      '/users/me/avatar',
      data: formData,
    );
    return response.data!['avatar_url'] as String;
  }

  /// Récupère les paramètres de confidentialité.
  Future<Map<String, dynamic>> getPrivacy() async {
    final response = await _dio.get<Map<String, dynamic>>('/users/me/privacy');
    return response.data!;
  }

  /// Met à jour les paramètres de confidentialité.
  Future<Map<String, dynamic>> updatePrivacy({
    bool? consentAnalytics,
    bool? consentMarketing,
  }) async {
    final body = <String, dynamic>{
      if (consentAnalytics != null)  'consent_analytics':  consentAnalytics,
      if (consentMarketing != null)  'consent_marketing':  consentMarketing,
    };
    final response = await _dio.patch<Map<String, dynamic>>(
      '/users/me/privacy',
      data: body,
    );
    return response.data!;
  }
}
