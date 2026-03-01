import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../data/profile_repository.dart';

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(ref.watch(apiClientProvider));
});

final profileProvider = AsyncNotifierProvider<ProfileNotifier, CoachProfile>(ProfileNotifier.new);

class ProfileNotifier extends AsyncNotifier<CoachProfile> {
  @override
  Future<CoachProfile> build() async {
    return ref.read(profileRepositoryProvider).getProfile();
  }

  Future<void> updateProfile(Map<String, dynamic> data) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
        () => ref.read(profileRepositoryProvider).updateProfile(data));
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
        () => ref.read(profileRepositoryProvider).getProfile());
  }
}
