import '../../../core/storage/secure_storage.dart';
import '../../../shared/models/user.dart';
import '../data/auth_repository.dart';

/// Couche domaine — orchestre le [AuthRepository] + [AppSecureStorage].
/// Persiste les informations de session après chaque opération réussie.
class AuthService {
  AuthService(this._repo, this._storage);

  final AuthRepository _repo;
  final AppSecureStorage _storage;

  // ── Auto-login ────────────────────────────────────────────────────────────

  /// Tente de restaurer la session depuis le stockage sécurisé.
  /// Retourne l'[User] si la clé API est valide, `null` sinon.
  Future<User?> tryAutoLogin() async {
    final hasKey = await _storage.hasApiKey();
    if (!hasKey) return null;
    try {
      final user = await _repo.getMe();
      await _persistSession(user.id, user.role.value);
      return user;
    } catch (_) {
      // Clé expirée ou invalide
      await _storage.clearAll();
      return null;
    }
  }

  // ── Login ─────────────────────────────────────────────────────────────────

  Future<User> login({
    required String email,
    required String password,
  }) async {
    final result = await _repo.login(email: email, password: password);
    await _storage.saveApiKey(result.apiKey);
    await _persistSession(result.user.id, result.user.role.value);
    return result.user;
  }

  // ── Register ──────────────────────────────────────────────────────────────

  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required String role,
    String? phone,
    String? gender,
    int? birthYear,
  }) async {
    final result = await _repo.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      role: role,
      phone: phone,
      gender: gender,
      birthYear: birthYear,
    );
    await _storage.saveApiKey(result.apiKey);
    await _persistSession(result.user.id, result.user.role.value);
    return result.user;
  }

  // ── Logout ────────────────────────────────────────────────────────────────

  Future<void> logout() async {
    try {
      await _repo.logout();
    } catch (_) {
      // Ignore — on supprime quand même la session locale
    }
    await _storage.clearAll();
  }

  // ── Email Verification ────────────────────────────────────────────────────

  Future<void> requestEmailVerification() => _repo.requestEmailVerification();

  Future<bool> confirmEmailVerification(String token) =>
      _repo.confirmEmailVerification(token);

  // ── Phone Verification ────────────────────────────────────────────────────

  Future<void> requestPhoneVerification() => _repo.requestPhoneVerification();

  Future<bool> confirmPhoneVerification(String code) =>
      _repo.confirmPhoneVerification(code);

  // ── Password ──────────────────────────────────────────────────────────────

  Future<void> forgotPassword(String email) => _repo.forgotPassword(email);

  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) =>
      _repo.resetPassword(token: token, newPassword: newPassword);

  // ── Private ───────────────────────────────────────────────────────────────

  Future<void> _persistSession(String userId, String role) async {
    await _storage.saveUserId(userId);
    await _storage.saveRole(role);
  }
}
