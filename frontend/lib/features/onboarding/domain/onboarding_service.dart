import '../../../shared/models/gym.dart';
import '../data/onboarding_repository.dart';

/// Service Onboarding — logique d'orchestration du wizard.
class OnboardingService {
  const OnboardingService(this._repo);

  final OnboardingRepository _repo;

  // ── Client ──────────────────────────────────────────────────────────────

  Future<void> saveClientBasicInfo({
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
    String? phone,
    String? timezone,
  }) async {
    final body = <String, dynamic>{};
    if (firstName != null && firstName.isNotEmpty) body['first_name'] = firstName;
    if (lastName != null && lastName.isNotEmpty) body['last_name'] = lastName;
    if (gender != null) body['gender'] = gender;
    if (birthYear != null) body['birth_year'] = birthYear;
    if (phone != null && phone.isNotEmpty) body['phone'] = phone;
    if (timezone != null && timezone.isNotEmpty) body['timezone'] = timezone;
    if (body.isNotEmpty) {
      await _repo.patchUserProfile(body);
    }
  }

  // ── Coach ──────────────────────────────────────────────────────────────

  Future<void> saveCoachProfile({
    String? bio,
    String? city,
    List<String>? specialties,
    int? hourlyRateCents,
    String? currency,
    int? experienceYears,
    bool? offersDiscovery,
    int? maxClients,
    List<String>? languages,
  }) async {
    final body = <String, dynamic>{};
    if (bio != null) body['bio'] = bio;
    if (city != null && city.isNotEmpty) body['city'] = city;
    if (specialties != null && specialties.isNotEmpty) body['specialties'] = specialties;
    if (hourlyRateCents != null) body['hourly_rate'] = hourlyRateCents;
    if (currency != null) body['currency'] = currency;
    if (experienceYears != null) body['experience_years'] = experienceYears;
    if (offersDiscovery != null) body['offers_discovery'] = offersDiscovery;
    if (maxClients != null) body['max_clients'] = maxClients;
    if (languages != null && languages.isNotEmpty) body['languages'] = languages;
    if (body.isNotEmpty) {
      await _repo.patchCoachProfile(body);
    }
  }

  // ── Gyms ────────────────────────────────────────────────────────────────

  Future<List<Gym>> searchGyms(String query, {String city = ''}) =>
      _repo.searchGyms(q: query, city: city);

  Future<List<Gym>> getUserGyms() => _repo.getUserGyms();

  Future<void> addGym(String gymId) => _repo.addUserGym(gymId);

  Future<void> removeGym(String gymId) => _repo.removeUserGym(gymId);

  // ── Enrollment ──────────────────────────────────────────────────────────

  Future<Map<String, dynamic>> getEnrollmentInfo(String token) =>
      _repo.getEnrollmentInfo(token);

  Future<void> enrollWithToken(String token) =>
      _repo.enrollWithToken(token);
}
