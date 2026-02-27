import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_exception.dart';

/// URL de base de l'API.
/// Injectée via --dart-define=API_BASE_URL=http://...
/// Valeur par défaut : serveur de dev local (LXC 102).
const String apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://192.168.10.63:8200',
);

const String _apiKeyHeader = 'X-API-Key';
const String _apiKeyStorageKey = 'mycoach_api_key';

/// Intercepteur Dio — injecte le header [X-API-Key] sur chaque requête.
class ApiKeyInterceptor extends Interceptor {
  const ApiKeyInterceptor(this._storage);

  final FlutterSecureStorage _storage;

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final apiKey = await _storage.read(key: _apiKeyStorageKey);
    if (apiKey != null) {
      options.headers[_apiKeyHeader] = apiKey;
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Transforme les erreurs Dio en [ApiException] pour faciliter le traitement
    // dans les services/notifiers.
    handler.next(AppDioException.fromDio(err));
  }
}

/// Crée et configure le client Dio principal.
Dio createApiClient(FlutterSecureStorage storage) {
  final dio = Dio(
    BaseOptions(
      baseUrl: apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {'Content-Type': 'application/json'},
    ),
  );
  dio.interceptors.addAll([
    ApiKeyInterceptor(storage),
    LogInterceptor(
      requestBody: false,
      responseBody: false,
      logPrint: (o) {
        // ignore: avoid_print
        assert(() { print('[Dio] $o'); return true; }());
      },
    ),
  ]);
  return dio;
}
