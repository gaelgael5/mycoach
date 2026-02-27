import 'package:dio/dio.dart';
import '../../../shared/models/program.dart';

class ProgramRepository {
  const ProgramRepository(this._dio);

  final Dio _dio;

  Future<Program?> getAssignedProgram() async {
    try {
      final resp =
          await _dio.get<Map<String, dynamic>>('/programs/assigned');
      if (resp.data == null) return null;
      return Program.fromJson(resp.data!);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) return null;
      rethrow;
    }
  }
}
