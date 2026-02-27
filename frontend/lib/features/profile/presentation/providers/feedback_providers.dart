import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../shared/models/feedback_item.dart';
import '../../domain/profile_service.dart';
import 'profile_providers.dart';

/// Notifier pour les feedbacks utilisateur.
class FeedbackNotifier
    extends StateNotifier<AsyncValue<List<FeedbackItem>>> {
  FeedbackNotifier(this._service) : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;

  Future<void> load() async {
    try {
      final items = await _service.getMyFeedbacks();
      state = AsyncValue.data(items);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> send({
    required String type,
    required String title,
    required String description,
  }) async {
    try {
      final item = await _service.sendFeedback(
        type:        type,
        title:       title,
        description: description,
      );
      state = AsyncValue.data([item, ...state.valueOrNull ?? []]);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final feedbackNotifierProvider =
    StateNotifierProvider<FeedbackNotifier, AsyncValue<List<FeedbackItem>>>(
  (ref) => FeedbackNotifier(ref.watch(profileServiceProvider)),
);

/// Type sélectionné dans le formulaire feedback.
final feedbackTypeSelectedProvider = StateProvider<String>(
  (ref) => 'suggestion',
);
