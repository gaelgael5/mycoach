import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/user.dart';
import '../../data/profile_repository.dart';
import '../../data/social_links_repository.dart';
import '../../data/health_repository.dart';
import '../../data/feedback_repository.dart';
import '../../domain/profile_service.dart';

// ── Repositories ─────────────────────────────────────────────────────────────

final profileRepositoryProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository(ref.watch(dioProvider));
});

final socialLinksRepositoryProvider = Provider<SocialLinksRepository>((ref) {
  return SocialLinksRepository(ref.watch(dioProvider));
});

final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  return HealthRepository(ref.watch(dioProvider));
});

final feedbackRepositoryProvider = Provider<FeedbackRepository>((ref) {
  return FeedbackRepository(ref.watch(dioProvider));
});

// ── Service ───────────────────────────────────────────────────────────────────

final profileServiceProvider = Provider<ProfileService>((ref) {
  return ProfileService(
    profileRepo:      ref.watch(profileRepositoryProvider),
    socialLinksRepo:  ref.watch(socialLinksRepositoryProvider),
    healthRepo:       ref.watch(healthRepositoryProvider),
    feedbackRepo:     ref.watch(feedbackRepositoryProvider),
  );
});

// ── Profil utilisateur ────────────────────────────────────────────────────────

/// Notifier pour le profil utilisateur.
class ProfileNotifier extends StateNotifier<AsyncValue<User?>> {
  ProfileNotifier(this._service) : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;

  Future<void> load() async {
    try {
      final user = await _service.getMe();
      state = AsyncValue.data(user);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> updateProfile({
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
    String? phone,
    String? timezone,
  }) async {
    try {
      final updated = await _service.updateProfile(
        firstName: firstName,
        lastName:  lastName,
        gender:    gender,
        birthYear: birthYear,
        phone:     phone,
        timezone:  timezone,
      );
      state = AsyncValue.data(updated);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> uploadAvatar(File file) async {
    try {
      await _service.uploadAvatar(file);
      await load();
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final profileNotifierProvider =
    StateNotifierProvider<ProfileNotifier, AsyncValue<User?>>((ref) {
  return ProfileNotifier(ref.watch(profileServiceProvider));
});

// ── Confidentialité ───────────────────────────────────────────────────────────

class PrivacyNotifier extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  PrivacyNotifier(this._service)
      : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;

  Future<void> load() async {
    try {
      final data = await _service.getPrivacy();
      state = AsyncValue.data(data);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> update({bool? consentAnalytics, bool? consentMarketing}) async {
    try {
      final data = await _service.updatePrivacy(
        consentAnalytics: consentAnalytics,
        consentMarketing: consentMarketing,
      );
      state = AsyncValue.data(data);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final privacyNotifierProvider =
    StateNotifierProvider<PrivacyNotifier, AsyncValue<Map<String, dynamic>>>(
      (ref) => PrivacyNotifier(ref.watch(profileServiceProvider)),
    );
