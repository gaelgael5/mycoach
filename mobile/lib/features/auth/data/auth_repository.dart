import '../../../core/api/api_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../../../shared/models/user.dart';

class AuthRepository {
  final ApiClient _api;
  final SecureStorageService _storage;

  AuthRepository(this._api, this._storage);

  Future<User> login(String email, String password) async {
    final response = await _api.dio.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    final data = response.data as Map<String, dynamic>;
    final token = (data['api_key'] ?? data['access_token']) as String;
    await _storage.setToken(token);
    if (data['refresh_token'] != null) {
      await _storage.setRefreshToken(data['refresh_token'] as String);
    }
    return User.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String? phone,
  }) async {
    final body = <String, dynamic>{
      'email': email,
      'password': password,
      'confirm_password': password,
      'first_name': firstName,
      'last_name': lastName,
      'role': 'coach',
    };
    // phone is not in backend RegisterRequest schema, skip it

    final response = await _api.dio.post('/auth/register', data: body);
    final data = response.data as Map<String, dynamic>;
    final token = (data['api_key'] ?? data['access_token']) as String;
    await _storage.setToken(token);
    return User.fromJson(data['user'] as Map<String, dynamic>);
  }

  Future<void> logout() async {
    await _storage.clearAll();
  }

  Future<bool> isAuthenticated() async {
    final token = await _storage.getToken();
    return token != null;
  }
}
