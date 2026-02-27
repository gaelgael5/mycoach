import 'package:dio/dio.dart';
import '../../../shared/models/coach_search_result.dart';
import '../../../shared/models/coach_profile.dart';
import '../../../shared/models/slot.dart';

class CoachSearchRepository {
  const CoachSearchRepository(this._dio);

  final Dio _dio;

  Future<({List<CoachSearchResult> coaches, int total, int page, int pages})>
      search({
    String? q,
    String? city,
    String? specialty,
    int page = 1,
    int limit = 20,
  }) async {
    final params = <String, dynamic>{
      'page': page,
      'limit': limit,
    };
    if (q != null && q.isNotEmpty) params['q'] = q;
    if (city != null && city.isNotEmpty) params['city'] = city;
    if (specialty != null && specialty.isNotEmpty) {
      params['specialty'] = specialty;
    }

    final resp = await _dio.get<Map<String, dynamic>>(
      '/coaches/search',
      queryParameters: params,
    );
    final data = resp.data!;
    final coaches = (data['coaches'] as List<dynamic>)
        .map((e) => CoachSearchResult.fromJson(e as Map<String, dynamic>))
        .toList();
    return (
      coaches: coaches,
      total: data['total'] as int? ?? coaches.length,
      page: data['page'] as int? ?? page,
      pages: data['pages'] as int? ?? 1,
    );
  }

  Future<CoachProfile> getProfile(String coachId) async {
    final resp = await _dio.get<Map<String, dynamic>>('/coaches/$coachId');
    return CoachProfile.fromJson(resp.data!);
  }

  Future<List<dynamic>> getSocialLinks(String coachId) async {
    final resp =
        await _dio.get<List<dynamic>>('/coaches/$coachId/social-links');
    return resp.data ?? [];
  }

  Future<List<Slot>> getAvailability(String coachId, DateTime date) async {
    final dateStr =
        '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    final resp = await _dio.get<Map<String, dynamic>>(
      '/coaches/$coachId/availability',
      queryParameters: {'date': dateStr},
    );
    final data = resp.data!;
    final slots = (data['slots'] as List<dynamic>)
        .map((e) => Slot.fromJson(e as Map<String, dynamic>))
        .toList();
    return slots;
  }
}
