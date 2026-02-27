import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../shared/models/social_link.dart';
import '../../domain/profile_service.dart';
import 'profile_providers.dart';

/// Notifier pour les liens sociaux de l'utilisateur.
class SocialLinksNotifier extends StateNotifier<AsyncValue<List<SocialLink>>> {
  SocialLinksNotifier(this._service) : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;

  Future<void> load() async {
    try {
      final links = await _service.getMyLinks();
      state = AsyncValue.data(links);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addLink({
    String? platform,
    String? label,
    required String url,
    required String visibility,
  }) async {
    try {
      final link = await _service.addLink(
        platform:   platform,
        label:      label,
        url:        url,
        visibility: visibility,
      );
      state = AsyncValue.data([...state.valueOrNull ?? [], link]);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> deleteLink(String id) async {
    try {
      await _service.deleteLink(id);
      state = AsyncValue.data(
        (state.valueOrNull ?? []).where((l) => l.id != id).toList(),
      );
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final socialLinksNotifierProvider =
    StateNotifierProvider<SocialLinksNotifier, AsyncValue<List<SocialLink>>>(
  (ref) => SocialLinksNotifier(ref.watch(profileServiceProvider)),
);
