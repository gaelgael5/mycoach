import 'dart:io';
import '../../../shared/models/user.dart';
import '../../../shared/models/social_link.dart';
import '../../../shared/models/health_log.dart';
import '../../../shared/models/health_parameter.dart';
import '../../../shared/models/feedback_item.dart';
import '../data/profile_repository.dart';
import '../data/social_links_repository.dart';
import '../data/health_repository.dart';
import '../data/feedback_repository.dart';

/// Service de domaine pour le profil utilisateur.
/// Orchestre les repositories et applique les règles métier.
class ProfileService {
  const ProfileService({
    required this.profileRepo,
    required this.socialLinksRepo,
    required this.healthRepo,
    required this.feedbackRepo,
  });

  final ProfileRepository profileRepo;
  final SocialLinksRepository socialLinksRepo;
  final HealthRepository healthRepo;
  final FeedbackRepository feedbackRepo;

  // ── Profil ────────────────────────────────────────────────────────────────

  Future<User> getMe() => profileRepo.getMe();

  Future<User> updateProfile({
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
    String? phone,
    String? timezone,
  }) => profileRepo.updateProfile(
    firstName: firstName,
    lastName:  lastName,
    gender:    gender,
    birthYear: birthYear,
    phone:     phone,
    timezone:  timezone,
  );

  Future<String> uploadAvatar(File file) => profileRepo.uploadAvatar(file);

  Future<Map<String, dynamic>> getPrivacy() => profileRepo.getPrivacy();

  Future<Map<String, dynamic>> updatePrivacy({
    bool? consentAnalytics,
    bool? consentMarketing,
  }) => profileRepo.updatePrivacy(
    consentAnalytics: consentAnalytics,
    consentMarketing: consentMarketing,
  );

  // ── Liens sociaux ─────────────────────────────────────────────────────────

  Future<List<SocialLink>> getMyLinks() => socialLinksRepo.getMyLinks();

  Future<SocialLink> addLink({
    String? platform,
    String? label,
    required String url,
    required String visibility,
  }) => socialLinksRepo.addLink(
    platform:   platform,
    label:      label,
    url:        url,
    visibility: visibility,
  );

  Future<void> deleteLink(String id) => socialLinksRepo.deleteLink(id);

  // ── Santé ─────────────────────────────────────────────────────────────────

  Future<List<HealthParameter>> getHealthParameters() =>
      healthRepo.getParameters();

  Future<List<HealthLog>> getHealthLogs({
    String? parameterSlug,
    int limit = 50,
  }) => healthRepo.getLogs(parameterSlug: parameterSlug, limit: limit);

  Future<HealthLog> addHealthLog({
    required String parameterId,
    required double value,
    DateTime? measuredAt,
  }) => healthRepo.addLog(
    parameterId: parameterId,
    value:       value,
    measuredAt:  measuredAt,
  );

  Future<void> deleteHealthLog(String id) => healthRepo.deleteLog(id);

  Future<Map<String, dynamic>> getHealthSharing(String coachId) =>
      healthRepo.getSharing(coachId);

  Future<Map<String, dynamic>> updateHealthSharing({
    required String coachId,
    required String parameterSlug,
    required bool shared,
  }) => healthRepo.updateSharing(
    coachId:       coachId,
    parameterSlug: parameterSlug,
    shared:        shared,
  );

  // ── Feedback ──────────────────────────────────────────────────────────────

  Future<FeedbackItem> sendFeedback({
    required String type,
    required String title,
    required String description,
  }) => feedbackRepo.sendFeedback(
    type:        type,
    title:       title,
    description: description,
  );

  Future<List<FeedbackItem>> getMyFeedbacks() => feedbackRepo.getMyFeedbacks();
}
