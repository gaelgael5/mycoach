import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/coach_search_result.dart';
import '../../../../shared/models/coach_profile.dart';
import '../../../../shared/models/slot.dart';
import '../../data/coach_search_repository.dart';

// ── Repository ────────────────────────────────────────────────────────────────

final coachSearchRepositoryProvider =
    Provider<CoachSearchRepository>((ref) {
  return CoachSearchRepository(ref.watch(dioProvider));
});

// ── Search State ──────────────────────────────────────────────────────────────

class CoachSearchParams {
  const CoachSearchParams({
    this.query = '',
    this.city = '',
    this.specialty = '',
    this.discoveryOnly = false,
  });

  final String query;
  final String city;
  final String specialty;
  final bool discoveryOnly;

  CoachSearchParams copyWith({
    String? query,
    String? city,
    String? specialty,
    bool? discoveryOnly,
  }) =>
      CoachSearchParams(
        query: query ?? this.query,
        city: city ?? this.city,
        specialty: specialty ?? this.specialty,
        discoveryOnly: discoveryOnly ?? this.discoveryOnly,
      );
}

final coachSearchParamsProvider =
    StateProvider<CoachSearchParams>((ref) => const CoachSearchParams());

final coachSearchResultsProvider = FutureProvider.autoDispose<
    List<CoachSearchResult>>((ref) async {
  final params = ref.watch(coachSearchParamsProvider);
  final repo = ref.watch(coachSearchRepositoryProvider);
  final result = await repo.search(
    q: params.query,
    city: params.city,
    specialty: params.specialty,
  );
  var coaches = result.coaches;
  if (params.discoveryOnly) {
    coaches = coaches.where((c) => c.offersDiscovery).toList();
  }
  return coaches;
});

// ── Coach Profile ─────────────────────────────────────────────────────────────

final coachProfileProvider =
    FutureProvider.autoDispose.family<CoachProfile, String>((ref, id) async {
  final repo = ref.watch(coachSearchRepositoryProvider);
  return repo.getProfile(id);
});

final coachSocialLinksProvider =
    FutureProvider.autoDispose.family<List<dynamic>, String>((ref, id) async {
  final repo = ref.watch(coachSearchRepositoryProvider);
  return repo.getSocialLinks(id);
});

// ── Availability ──────────────────────────────────────────────────────────────

class CoachDateKey {
  const CoachDateKey(this.coachId, this.date);
  final String coachId;
  final DateTime date;

  @override
  bool operator ==(Object other) =>
      other is CoachDateKey &&
      other.coachId == coachId &&
      other.date.year == date.year &&
      other.date.month == date.month &&
      other.date.day == date.day;

  @override
  int get hashCode => Object.hash(coachId, date.year, date.month, date.day);
}

final slotAvailabilityProvider = FutureProvider.autoDispose
    .family<List<Slot>, CoachDateKey>((ref, key) async {
  final repo = ref.watch(coachSearchRepositoryProvider);
  return repo.getAvailability(key.coachId, key.date);
});

final selectedDateProvider =
    StateProvider.autoDispose<DateTime>((ref) => DateTime.now());
