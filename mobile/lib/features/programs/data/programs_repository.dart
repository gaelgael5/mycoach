import '../../../core/api/api_client.dart';
import '../../../shared/models/program.dart';

class ProgramsRepository {
  final ApiClient _api;
  ProgramsRepository(this._api);

  Future<List<Program>> getPrograms() async {
    final res = await _api.dio.get('/programs');
    return (res.data as List).map((e) => Program.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Program> getProgram(String id) async {
    final res = await _api.dio.get('/programs/$id');
    return Program.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Program> createProgram(Map<String, dynamic> data) async {
    final res = await _api.dio.post('/programs', data: data);
    return Program.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Session> addSession(String programId, Map<String, dynamic> data) async {
    final res = await _api.dio.post('/programs/$programId/sessions', data: data);
    return Session.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Exercise> addExercise(String sessionId, Map<String, dynamic> data) async {
    final res = await _api.dio.post('/sessions/$sessionId/exercises', data: data);
    return Exercise.fromJson(res.data as Map<String, dynamic>);
  }

  Future<void> assignClients(String programId, List<String> clientIds) async {
    await _api.dio.post('/programs/$programId/assign', data: {'client_ids': clientIds});
  }
}
