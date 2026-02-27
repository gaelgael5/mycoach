import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/performance_session.dart';
import '../../../../shared/models/program.dart';
import '../../data/performance_repository.dart';
import '../../data/program_repository.dart';

// ── Repositories ──────────────────────────────────────────────────────────────

final performanceRepositoryProvider =
    Provider<PerformanceRepository>((ref) {
  return PerformanceRepository(ref.watch(dioProvider));
});

final programRepositoryProvider = Provider<ProgramRepository>((ref) {
  return ProgramRepository(ref.watch(dioProvider));
});

// ── Selected Exercise Filter ──────────────────────────────────────────────────

final selectedExerciseSlugProvider =
    StateProvider.autoDispose<String?>((ref) => null);

// ── Data ──────────────────────────────────────────────────────────────────────

final performanceSessionsProvider =
    FutureProvider.autoDispose<List<PerformanceSession>>((ref) async {
  final slug = ref.watch(selectedExerciseSlugProvider);
  final repo = ref.watch(performanceRepositoryProvider);
  return repo.getPerformances(exerciseSlug: slug);
});

final personalRecordsProvider =
    FutureProvider.autoDispose<List<PersonalRecord>>((ref) async {
  final repo = ref.watch(performanceRepositoryProvider);
  return repo.getPersonalRecords();
});

final assignedProgramProvider =
    FutureProvider.autoDispose<Program?>((ref) async {
  final repo = ref.watch(programRepositoryProvider);
  return repo.getAssignedProgram();
});
