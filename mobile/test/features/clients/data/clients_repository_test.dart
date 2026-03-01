import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:mycoach_mobile/core/api/api_client.dart';
import 'package:mycoach_mobile/features/clients/data/clients_repository.dart';

@GenerateNiceMocks([MockSpec<ApiClient>(), MockSpec<Dio>()])
import 'clients_repository_test.mocks.dart';

void main() {
  late MockDio mockDio;
  late MockApiClient mockApi;
  late ClientsRepository repo;

  setUp(() {
    mockDio = MockDio();
    mockApi = MockApiClient();
    when(mockApi.dio).thenReturn(mockDio);
    repo = ClientsRepository(mockApi);
  });

  test('getClients returns list', () async {
    when(mockDio.get('/clients')).thenAnswer((_) async => Response(
      data: [
        {'id': 'c1', 'first_name': 'A', 'last_name': 'B', 'email': 'a@b.com', 'created_at': '2025-01-01T00:00:00Z'},
      ],
      statusCode: 200, requestOptions: RequestOptions()));
    final clients = await repo.getClients();
    expect(clients.length, 1);
    expect(clients.first.id, 'c1');
  });

  test('getClient returns single client', () async {
    when(mockDio.get('/clients/c1')).thenAnswer((_) async => Response(
      data: {'id': 'c1', 'first_name': 'A', 'last_name': 'B', 'email': 'a@b.com', 'created_at': '2025-01-01T00:00:00Z'},
      statusCode: 200, requestOptions: RequestOptions()));
    final client = await repo.getClient('c1');
    expect(client.firstName, 'A');
  });
}
