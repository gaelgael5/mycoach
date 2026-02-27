import 'package:dio/dio.dart';
import '../../../shared/models/health_log.dart';
import '../../../shared/models/health_parameter.dart';

/// Repository pour les paramètres et logs de santé.
class HealthRepository {
  const HealthRepository(this._dio);

  final Dio _dio;

  /// Récupère la liste des paramètres de santé disponibles.
  Future<List<HealthParameter>> getParameters() async {
    final response = await _dio.get<List<dynamic>>('/health/parameters');
    return (response.data ?? [])
        .map((e) => HealthParameter.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Récupère les logs de santé pour un paramètre donné.
  Future<List<HealthLog>> getLogs({
    String? parameterSlug,
    int limit = 50,
  }) async {
    final queryParams = <String, dynamic>{
      'limit': limit,
      if (parameterSlug != null) 'parameter_slug': parameterSlug,
    };
    final response = await _dio.get<List<dynamic>>(
      '/health/logs',
      queryParameters: queryParams,
    );
    return (response.data ?? [])
        .map((e) => HealthLog.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Enregistre un nouveau log de santé.
  Future<HealthLog> addLog({
    required String parameterId,
    required double value,
    DateTime? measuredAt,
  }) async {
    final body = <String, dynamic>{
      'parameter_id': parameterId,
      'value':        value,
      if (measuredAt != null) 'measured_at': measuredAt.toIso8601String(),
    };
    final response = await _dio.post<Map<String, dynamic>>(
      '/health/logs',
      data: body,
    );
    return HealthLog.fromJson(response.data!);
  }

  /// Supprime un log de santé.
  Future<void> deleteLog(String id) async {
    await _dio.delete('/health/logs/$id');
  }

  /// Récupère les préférences de partage avec un coach.
  Future<Map<String, dynamic>> getSharing(String coachId) async {
    final response = await _dio.get<Map<String, dynamic>>(
      '/health/sharing/$coachId',
    );
    return response.data!;
  }

  /// Met à jour le partage d'un paramètre avec un coach.
  Future<Map<String, dynamic>> updateSharing({
    required String coachId,
    required String parameterSlug,
    required bool shared,
  }) async {
    final body = <String, dynamic>{
      'parameter_slug': parameterSlug,
      'shared':         shared,
    };
    final response = await _dio.patch<Map<String, dynamic>>(
      '/health/sharing/$coachId',
      data: body,
    );
    return response.data!;
  }
}
