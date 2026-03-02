import '../../../core/api/api_client.dart';
import '../../../shared/models/program.dart';

class ProgramsRepository {
  final ApiClient _api;
  ProgramsRepository(this._api);

  Future<List<Program>> getPrograms() async {
    final res = await _api.dio.get('/coaches/programs');
    return (res.data as List).map((e) => Program.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Program> getProgram(String id) async {
    final res = await _api.dio.get('/coaches/programs/$id');
    return Program.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Program> createProgram(Program program) async {
    final res = await _api.dio.post('/coaches/programs', data: program.toCreateJson());
    return Program.fromJson(res.data as Map<String, dynamic>);
  }

  Future<void> archiveProgram(String id) async {
    await _api.dio.post('/coaches/programs/$id/archive');
  }

  Future<Program> duplicateProgram(String id) async {
    final res = await _api.dio.post('/coaches/programs/$id/duplicate');
    return Program.fromJson(res.data as Map<String, dynamic>);
  }

  Future<void> assignToClient(String planId, String clientId, String startDate, {String mode = 'strict'}) async {
    await _api.dio.post('/coaches/programs/$planId/assign', data: {
      'client_id': clientId,
      'start_date': startDate,
      'mode': mode,
    });
  }

  // Exercise library
  Future<List<ExerciseType>> getExercises() async {
    final res = await _api.dio.get('/exercises');
    return (res.data as List).map((e) => ExerciseType.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<ExerciseType> getExercise(String id) async {
    final res = await _api.dio.get('/exercises/$id');
    return ExerciseType.fromJson(res.data as Map<String, dynamic>);
  }
}
