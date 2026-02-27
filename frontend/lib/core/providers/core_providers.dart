import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../storage/secure_storage.dart';

/// Provider Flutter Secure Storage (singleton).
final flutterSecureStorageProvider = Provider<FlutterSecureStorage>(
  (_) => const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  ),
);

/// Provider AppSecureStorage — wrapper typé.
final secureStorageProvider = Provider<AppSecureStorage>((ref) {
  final raw = ref.watch(flutterSecureStorageProvider);
  return AppSecureStorage(raw);
});

/// Provider Dio — client HTTP principal.
/// Injecte automatiquement le header X-API-Key sur chaque requête.
final dioProvider = Provider<Dio>((ref) {
  final storage = ref.watch(flutterSecureStorageProvider);
  return createApiClient(storage);
});

/// Provider rôle de l'utilisateur connecté.
/// Alimenté après login/auto-login depuis [AuthNotifier].
/// 'client' | 'coach' | 'admin' | null (non connecté)
final userRoleProvider = StateProvider<String?>((ref) => null);

/// Provider ID de l'utilisateur connecté.
final userIdProvider = StateProvider<String?>((ref) => null);

/// Provider locale active (BCP 47).
/// Utilisé par MaterialApp.router → localeResolutionCallback.
final localProvider = StateProvider<String>((ref) => 'fr');
