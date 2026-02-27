import 'package:dio/dio.dart';
import '../../../shared/models/feedback_item.dart';

/// Repository pour les feedbacks utilisateur.
class FeedbackRepository {
  const FeedbackRepository(this._dio);

  final Dio _dio;

  /// Envoie un feedback (suggestion ou bug report).
  Future<FeedbackItem> sendFeedback({
    required String type,
    required String title,
    required String description,
  }) async {
    final body = <String, dynamic>{
      'type':        type,
      'title':       title,
      'description': description,
    };
    final response = await _dio.post<Map<String, dynamic>>(
      '/feedback',
      data: body,
    );
    return FeedbackItem.fromJson(response.data!);
  }

  /// Récupère la liste des feedbacks de l'utilisateur connecté.
  Future<List<FeedbackItem>> getMyFeedbacks() async {
    final response = await _dio.get<List<dynamic>>('/feedback');
    return (response.data ?? [])
        .map((e) => FeedbackItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
