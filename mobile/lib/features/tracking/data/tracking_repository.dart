import '../../../core/api/api_client.dart';
import '../../../shared/models/tracking.dart';

class TrackingRepository {
  final ApiClient _api;
  TrackingRepository(this._api);

  Future<List<SessionCompletion>> getCompletions() async {
    final res = await _api.dio.get('/api/v1/tracking/completions');
    return (res.data as List).map((e) => SessionCompletion.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> completeSession(String sessionId, List<Map<String, dynamic>> exerciseLogs) async {
    await _api.dio.post('/api/v1/tracking/completions', data: {
      'session_id': sessionId,
      'exercise_logs': exerciseLogs,
    });
  }

  Future<List<Metric>> getMetrics({int days = 30}) async {
    final res = await _api.dio.get('/api/v1/tracking/metrics', queryParameters: {'days': days});
    return (res.data as List).map((e) => Metric.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<void> addMetric(Map<String, dynamic> data) async {
    await _api.dio.post('/api/v1/tracking/metrics', data: data);
  }
}
