import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/api/api_exception.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/user.dart';
import '../../data/auth_repository.dart';
import '../../domain/auth_service.dart';

// ── Repository & Service providers ───────────────────────────────────────────

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(dioProvider));
});

final authServiceProvider = Provider<AuthService>((ref) {
  return AuthService(
    ref.watch(authRepositoryProvider),
    ref.watch(secureStorageProvider),
  );
});

// ── Auth State ────────────────────────────────────────────────────────────────

/// État global d'authentification.
/// - `loading` : auto-login en cours (affiché sur SplashScreen).
/// - `data(null)` : non connecté.
/// - `data(user)` : connecté.
/// - `error` : erreur d'auto-login (rare).
final authStateProvider =
    StateNotifierProvider<AuthNotifier, AsyncValue<User?>>((ref) {
  return AuthNotifier(
    ref.watch(authServiceProvider),
    ref,
  );
});

// ── Action States (pour les formulaires) ─────────────────────────────────────

/// État du formulaire de connexion.
final loginActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

/// État du formulaire d'inscription.
final registerActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

/// État des formulaires OTP / email verif / forgot / reset.
final otpActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

final emailVerifActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

final forgotPasswordActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

final resetPasswordActionProvider =
    StateNotifierProvider.autoDispose<AuthActionNotifier, AsyncValue<void>>(
  (_) => AuthActionNotifier(),
);

// ── Auth Notifier ─────────────────────────────────────────────────────────────

class AuthNotifier extends StateNotifier<AsyncValue<User?>> {
  AuthNotifier(this._service, this._ref)
      : super(const AsyncValue.loading()) {
    _autoLogin();
  }

  final AuthService _service;
  final Ref _ref;

  Future<void> _autoLogin() async {
    try {
      final user = await _service.tryAutoLogin();
      if (user != null) {
        _updateRoleProviders(user);
      }
      state = AsyncValue.data(user);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> login({
    required String email,
    required String password,
  }) async {
    state = const AsyncValue.loading();
    try {
      final user = await _service.login(email: email, password: password);
      _updateRoleProviders(user);
      state = AsyncValue.data(user);
    } catch (_) {
      state = AsyncValue.data(null);
      rethrow; // Les écrans gèrent l'affichage de l'erreur
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
    String? phone,
    String? gender,
    int? birthYear,
  }) async {
    state = const AsyncValue.loading();
    try {
      final user = await _service.register(
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
        role: role,
        phone: phone,
        gender: gender,
        birthYear: birthYear,
      );
      _updateRoleProviders(user);
      state = AsyncValue.data(user);
    } catch (_) {
      state = AsyncValue.data(null);
      rethrow;
    }
  }

  Future<void> logout() async {
    state = const AsyncValue.loading();
    try {
      await _service.logout();
    } finally {
      _ref.read(userRoleProvider.notifier).state = null;
      _ref.read(userIdProvider.notifier).state = null;
      state = AsyncValue.data(null);
    }
  }

  void _updateRoleProviders(User user) {
    _ref.read(userRoleProvider.notifier).state = user.role.value;
    _ref.read(userIdProvider.notifier).state = user.id;
  }

  // ── Current user shortcut ─────────────────────────────────────────────────

  User? get currentUser => state.valueOrNull;
}

// ── Generic Action Notifier ───────────────────────────────────────────────────

class AuthActionNotifier extends StateNotifier<AsyncValue<void>> {
  AuthActionNotifier() : super(const AsyncValue.data(null));

  Future<void> run(Future<void> Function() fn) async {
    state = const AsyncValue.loading();
    try {
      await fn();
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/// Traduit un [AppDioException] en code d'erreur lisible par les écrans.
ApiErrorCode extractApiErrorCode(Object error) {
  if (error is AppDioException) return error.code;
  return ApiErrorCode.unknown;
}

/// Extrait le nombre de minutes pour le rate-limit.
int extractRetryAfterMinutes(Object error) {
  if (error is AppDioException && error.retryAfterSeconds != null) {
    return (error.retryAfterSeconds! / 60).ceil();
  }
  return 5;
}
