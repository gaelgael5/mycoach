import 'package:dio/dio.dart';
import '../../../shared/models/performance_session.dart';

class PerformanceRepository {
  const PerformanceRepository(this._dio);

  final Dio _dio;

  Future<List<PerformanceSession>> getPerformances({
    String? exerciseSlug,
    int limit = 50,
  }) async {
    final params = <String, dynamic>{'limit': limit};
    if (exerciseSlug != null && exerciseSlug.isNotEmpty) {
      params['exercise_slug'] = exerciseSlug;
    }
    final resp = await _dio.get<Map<String, dynamic>>(
      '/performances/me',
      queryParameters: params,
    );
    final data = resp.data!;
    return (data['sessions'] as List<dynamic>)
        .map((e) => PerformanceSession.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<PersonalRecord>> getPersonalRecords() async {
    final resp =
        await _dio.get<Map<String, dynamic>>('/performances/me/prs');
    final data = resp.data!;
    return (data['prs'] as List<dynamic>)
        .map((e) => PersonalRecord.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
