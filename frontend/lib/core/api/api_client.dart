/// Client Dio — toutes les requêtes API passent ici.
/// L'API Key est injectée automatiquement via l'intercepteur.
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const String _apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://localhost:8000',
);

const String _apiKeyStorageKey = 'mycoach_api_key';

class ApiKeyInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;
  ApiKeyInterceptor(this._storage);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final apiKey = await _storage.read(key: _apiKeyStorageKey);
    if (apiKey != null) {
      options.headers['X-API-Key'] = apiKey;
    }
    super.onRequest(options, handler);
  }
}

Dio createApiClient(FlutterSecureStorage storage) {
  final dio = Dio(BaseOptions(
    baseUrl: _apiBaseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));
  dio.interceptors.add(ApiKeyInterceptor(storage));
  return dio;
}
