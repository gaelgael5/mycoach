import 'package:dio/dio.dart';
import '../../../shared/models/social_link.dart';

/// Repository pour la gestion des liens sociaux.
class SocialLinksRepository {
  const SocialLinksRepository(this._dio);

  final Dio _dio;

  /// Récupère les liens sociaux de l'utilisateur connecté.
  Future<List<SocialLink>> getMyLinks() async {
    final response = await _dio.get<List<dynamic>>('/users/me/social-links');
    return (response.data ?? [])
        .map((e) => SocialLink.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Ajoute un nouveau lien social.
  Future<SocialLink> addLink({
    String? platform,
    String? label,
    required String url,
    required String visibility,
  }) async {
    final body = <String, dynamic>{
      if (platform != null) 'platform':   platform,
      if (label != null)    'label':      label,
      'url':                 url,
      'visibility':          visibility,
    };
    final response = await _dio.post<Map<String, dynamic>>(
      '/users/me/social-links',
      data: body,
    );
    return SocialLink.fromJson(response.data!);
  }

  /// Met à jour un lien social existant.
  Future<SocialLink> updateLink({
    required String id,
    String? label,
    String? url,
    String? visibility,
  }) async {
    final body = <String, dynamic>{
      if (label != null)      'label':      label,
      if (url != null)        'url':        url,
      if (visibility != null) 'visibility': visibility,
    };
    final response = await _dio.put<Map<String, dynamic>>(
      '/users/me/social-links/$id',
      data: body,
    );
    return SocialLink.fromJson(response.data!);
  }

  /// Supprime un lien social.
  Future<void> deleteLink(String id) async {
    await _dio.delete('/users/me/social-links/$id');
  }

  /// Récupère les liens publics d'un coach.
  Future<List<SocialLink>> getCoachLinks(String coachId) async {
    final response = await _dio.get<List<dynamic>>(
      '/coaches/$coachId/social-links',
    );
    return (response.data ?? [])
        .map((e) => SocialLink.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
