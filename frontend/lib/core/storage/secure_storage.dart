import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Clés de stockage sécurisé — jamais de string libre ailleurs dans le code.
abstract class StorageKeys {
  static const String apiKey   = 'mycoach_api_key';
  static const String userRole = 'mycoach_user_role';
  static const String userId   = 'mycoach_user_id';
  static const String locale   = 'mycoach_locale';
}

/// Wrapper typé sur [FlutterSecureStorage].
///
/// Centralise toutes les opérations de lecture/écriture sur le stockage
/// sécurisé (AES-256 Android Keystore / iOS Keychain).
class AppSecureStorage {
  AppSecureStorage(this._storage);

  final FlutterSecureStorage _storage;

  // ── API Key ──────────────────────────────────────────────────────────────

  /// Stocke la clé API reçue après login/register.
  Future<void> saveApiKey(String key) =>
      _storage.write(key: StorageKeys.apiKey, value: key);

  /// Lit la clé API. Retourne `null` si absente.
  Future<String?> getApiKey() => _storage.read(key: StorageKeys.apiKey);

  /// Supprime la clé API (logout).
  Future<void> deleteApiKey() => _storage.delete(key: StorageKeys.apiKey);

  /// Retourne `true` si une clé API est présente (= session potentiellement active).
  Future<bool> hasApiKey() async => (await getApiKey()) != null;

  // ── Rôle utilisateur ─────────────────────────────────────────────────────

  /// Stocke le rôle ('client' | 'coach' | 'admin').
  Future<void> saveRole(String role) =>
      _storage.write(key: StorageKeys.userRole, value: role);

  /// Lit le rôle.
  Future<String?> getRole() => _storage.read(key: StorageKeys.userRole);

  // ── User ID ──────────────────────────────────────────────────────────────

  Future<void> saveUserId(String id) =>
      _storage.write(key: StorageKeys.userId, value: id);

  Future<String?> getUserId() => _storage.read(key: StorageKeys.userId);

  // ── Locale préférée ──────────────────────────────────────────────────────

  Future<void> saveLocale(String locale) =>
      _storage.write(key: StorageKeys.locale, value: locale);

  Future<String?> getLocale() => _storage.read(key: StorageKeys.locale);

  // ── Nettoyage complet (logout total) ─────────────────────────────────────

  /// Efface toutes les données stockées. Appelé à la déconnexion totale.
  Future<void> clearAll() => _storage.deleteAll();
}
