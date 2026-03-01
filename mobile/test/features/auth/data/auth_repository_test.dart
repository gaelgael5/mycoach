import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:mycoach_mobile/core/api/api_client.dart';
import 'package:mycoach_mobile/core/storage/secure_storage.dart';
import 'package:mycoach_mobile/features/auth/data/auth_repository.dart';

@GenerateNiceMocks([MockSpec<ApiClient>(), MockSpec<Dio>(), MockSpec<SecureStorageService>()])
import 'auth_repository_test.mocks.dart';

void main() {
  late MockDio mockDio;
  late MockApiClient mockApi;
  late MockSecureStorageService mockStorage;
  late AuthRepository repo;

  final userJson = {
    'id': 'u1', 'email': 'a@b.com', 'first_name': 'A', 'last_name': 'B', 'role': 'coach',
  };

  setUp(() {
    mockDio = MockDio();
    mockApi = MockApiClient();
    mockStorage = MockSecureStorageService();
    when(mockApi.dio).thenReturn(mockDio);
    repo = AuthRepository(mockApi, mockStorage);
  });

  test('login stores token and returns user', () async {
    when(mockDio.post('/auth/login', data: anyNamed('data'))).thenAnswer((_) async =>
      Response(data: {'access_token': 'tok', 'refresh_token': 'ref', 'user': userJson},
        statusCode: 200, requestOptions: RequestOptions()));
    final user = await repo.login('a@b.com', 'pass');
    expect(user.email, 'a@b.com');
    verify(mockStorage.setToken('tok')).called(1);
    verify(mockStorage.setRefreshToken('ref')).called(1);
  });

  test('register stores token and returns user', () async {
    when(mockDio.post('/auth/register', data: anyNamed('data'))).thenAnswer((_) async =>
      Response(data: {'access_token': 'tok2', 'user': userJson},
        statusCode: 201, requestOptions: RequestOptions()));
    final user = await repo.register(email: 'a@b.com', password: 'p', firstName: 'A', lastName: 'B');
    expect(user.firstName, 'A');
    verify(mockStorage.setToken('tok2')).called(1);
  });

  test('logout clears storage', () async {
    await repo.logout();
    verify(mockStorage.clearAll()).called(1);
  });
}
