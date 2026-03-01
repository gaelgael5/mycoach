class AppConfig {
  static const String environment = String.fromEnvironment(
    'ENV',
    defaultValue: 'dev',
  );

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.158.10.63:8000/api/v1',
  );

  static const int maxFreeClients = 15;
  static const String appName = 'MyCoach';

  /// Helper to know current env
  static bool get isDev => environment == 'dev';
  static bool get isStaging => environment == 'staging';
  static bool get isProd => environment == 'prod';
}
