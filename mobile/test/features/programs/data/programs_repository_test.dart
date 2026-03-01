import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:mycoach_mobile/core/api/api_client.dart';
import 'package:mycoach_mobile/features/programs/data/programs_repository.dart';

@GenerateNiceMocks([MockSpec<ApiClient>(), MockSpec<Dio>()])
import 'programs_repository_test.mocks.dart';

void main() {
  late MockDio mockDio;
  late MockApiClient mockApi;
  late ProgramsRepository repo;

  final programJson = {
    'id': 'p1', 'name': 'Strength', 'duration_weeks': 8,
    'created_at': '2025-01-01T00:00:00Z',
  };

  setUp(() {
    mockDio = MockDio();
    mockApi = MockApiClient();
    when(mockApi.dio).thenReturn(mockDio);
    repo = ProgramsRepository(mockApi);
  });

  test('getPrograms returns list', () async {
    when(mockDio.get('/api/v1/programs')).thenAnswer((_) async =>
      Response(data: [programJson], statusCode: 200, requestOptions: RequestOptions()));
    final programs = await repo.getPrograms();
    expect(programs.length, 1);
    expect(programs.first.name, 'Strength');
  });

  test('createProgram returns program', () async {
    when(mockDio.post('/api/v1/programs', data: anyNamed('data'))).thenAnswer((_) async =>
      Response(data: programJson, statusCode: 201, requestOptions: RequestOptions()));
    final p = await repo.createProgram({'name': 'Strength', 'duration_weeks': 8});
    expect(p.id, 'p1');
  });

  test('assignClients calls correct endpoint', () async {
    when(mockDio.post('/api/v1/programs/p1/assign', data: anyNamed('data'))).thenAnswer((_) async =>
      Response(data: null, statusCode: 200, requestOptions: RequestOptions()));
    await repo.assignClients('p1', ['c1', 'c2']);
    verify(mockDio.post('/api/v1/programs/p1/assign', data: {'client_ids': ['c1', 'c2']})).called(1);
  });
}
