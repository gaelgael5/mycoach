import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/program.dart';
import '../../data/programs_repository.dart';

final programsRepositoryProvider = Provider<ProgramsRepository>((ref) {
  return ProgramsRepository(ref.watch(apiClientProvider));
});

final programsProvider = FutureProvider<List<Program>>((ref) async {
  return ref.watch(programsRepositoryProvider).getPrograms();
});

final programDetailProvider = FutureProvider.family<Program, String>((ref, id) async {
  return ref.watch(programsRepositoryProvider).getProgram(id);
});
