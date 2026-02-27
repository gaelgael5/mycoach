import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/gym.dart';
import '../../data/onboarding_repository.dart';
import '../../domain/onboarding_service.dart';

// ── Repository & Service providers ──────────────────────────────────────────

final onboardingRepositoryProvider = Provider<OnboardingRepository>((ref) {
  return OnboardingRepository(ref.watch(dioProvider));
});

final onboardingServiceProvider = Provider<OnboardingService>((ref) {
  return OnboardingService(ref.watch(onboardingRepositoryProvider));
});

// ── Client Onboarding State ──────────────────────────────────────────────────

class ClientOnboardingState {
  ClientOnboardingState({
    this.step = 0,
    this.firstName = '',
    this.lastName = '',
    this.gender,
    this.birthYear,
    this.selectedGoals = const [],
    this.selectedGyms = const [],
    this.isLoading = false,
    this.error,
  });

  final int step;
  final String firstName;
  final String lastName;
  final String? gender;
  final int? birthYear;
  final List<String> selectedGoals;
  final List<Gym> selectedGyms;
  final bool isLoading;
  final String? error;

  ClientOnboardingState copyWith({
    int? step,
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
    List<String>? selectedGoals,
    List<Gym>? selectedGyms,
    bool? isLoading,
    String? error,
  }) =>
      ClientOnboardingState(
        step: step ?? this.step,
        firstName: firstName ?? this.firstName,
        lastName: lastName ?? this.lastName,
        gender: gender ?? this.gender,
        birthYear: birthYear ?? this.birthYear,
        selectedGoals: selectedGoals ?? this.selectedGoals,
        selectedGyms: selectedGyms ?? this.selectedGyms,
        isLoading: isLoading ?? this.isLoading,
        error: error,
      );
}

class ClientOnboardingNotifier extends StateNotifier<ClientOnboardingState> {
  ClientOnboardingNotifier(this._service) : super(ClientOnboardingState());

  final OnboardingService _service;

  static const int totalSteps = 4;

  void updateBasicInfo({
    String? firstName,
    String? lastName,
    String? gender,
    int? birthYear,
  }) {
    state = state.copyWith(
      firstName: firstName ?? state.firstName,
      lastName: lastName ?? state.lastName,
      gender: gender ?? state.gender,
      birthYear: birthYear ?? state.birthYear,
    );
  }

  void toggleGoal(String goal) {
    final goals = List<String>.from(state.selectedGoals);
    if (goals.contains(goal)) {
      goals.remove(goal);
    } else {
      goals.add(goal);
    }
    state = state.copyWith(selectedGoals: goals);
  }

  void toggleGym(Gym gym) {
    final gyms = List<Gym>.from(state.selectedGyms);
    final exists = gyms.any((g) => g.id == gym.id);
    if (exists) {
      gyms.removeWhere((g) => g.id == gym.id);
    } else if (gyms.length < 5) {
      gyms.add(gym);
    }
    state = state.copyWith(selectedGyms: gyms);
  }

  void nextStep() {
    if (state.step < totalSteps - 1) {
      state = state.copyWith(step: state.step + 1);
    }
  }

  void previousStep() {
    if (state.step > 0) {
      state = state.copyWith(step: state.step - 1);
    }
  }

  Future<bool> saveStep1() async {
    state = state.copyWith(isLoading: true);
    try {
      await _service.saveClientBasicInfo(
        firstName: state.firstName,
        lastName: state.lastName,
        gender: state.gender,
        birthYear: state.birthYear,
      );
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  Future<bool> saveGyms() async {
    state = state.copyWith(isLoading: true);
    try {
      for (final gym in state.selectedGyms) {
        await _service.addGym(gym.id);
      }
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  void clearError() => state = state.copyWith(error: null);
}

final clientOnboardingProvider =
    StateNotifierProvider.autoDispose<ClientOnboardingNotifier, ClientOnboardingState>(
  (ref) => ClientOnboardingNotifier(ref.watch(onboardingServiceProvider)),
);

// ── Coach Onboarding State ───────────────────────────────────────────────────

class CoachOnboardingState {
  CoachOnboardingState({
    this.step = 0,
    this.bio = '',
    this.city = '',
    this.selectedSpecialties = const [],
    this.hourlyRateEuros = 0,
    this.currency = 'EUR',
    this.experienceYears = 0,
    this.offersDiscovery = false,
    this.maxClients,
    this.selectedGyms = const [],
    this.isLoading = false,
    this.error,
  });

  final int step;
  final String bio;
  final String city;
  final List<String> selectedSpecialties;
  final int hourlyRateEuros;
  final String currency;
  final int experienceYears;
  final bool offersDiscovery;
  final int? maxClients;
  final List<Gym> selectedGyms;
  final bool isLoading;
  final String? error;

  CoachOnboardingState copyWith({
    int? step,
    String? bio,
    String? city,
    List<String>? selectedSpecialties,
    int? hourlyRateEuros,
    String? currency,
    int? experienceYears,
    bool? offersDiscovery,
    int? maxClients,
    List<Gym>? selectedGyms,
    bool? isLoading,
    String? error,
  }) =>
      CoachOnboardingState(
        step: step ?? this.step,
        bio: bio ?? this.bio,
        city: city ?? this.city,
        selectedSpecialties: selectedSpecialties ?? this.selectedSpecialties,
        hourlyRateEuros: hourlyRateEuros ?? this.hourlyRateEuros,
        currency: currency ?? this.currency,
        experienceYears: experienceYears ?? this.experienceYears,
        offersDiscovery: offersDiscovery ?? this.offersDiscovery,
        maxClients: maxClients ?? this.maxClients,
        selectedGyms: selectedGyms ?? this.selectedGyms,
        isLoading: isLoading ?? this.isLoading,
        error: error,
      );

  bool get canProceedFromStep1 => true; // bio et city optionnels
  bool get canProceedFromStep2 => selectedSpecialties.isNotEmpty;
}

class CoachOnboardingNotifier extends StateNotifier<CoachOnboardingState> {
  CoachOnboardingNotifier(this._service) : super(CoachOnboardingState());

  final OnboardingService _service;

  static const int totalSteps = 5;

  void updateBioCity({String? bio, String? city}) {
    state = state.copyWith(bio: bio ?? state.bio, city: city ?? state.city);
  }

  void toggleSpecialty(String specialty) {
    final specs = List<String>.from(state.selectedSpecialties);
    if (specs.contains(specialty)) {
      specs.remove(specialty);
    } else {
      specs.add(specialty);
    }
    state = state.copyWith(selectedSpecialties: specs);
  }

  void updatePricing({
    int? hourlyRateEuros,
    String? currency,
    int? experienceYears,
    bool? offersDiscovery,
    int? maxClients,
  }) {
    state = state.copyWith(
      hourlyRateEuros: hourlyRateEuros ?? state.hourlyRateEuros,
      currency: currency ?? state.currency,
      experienceYears: experienceYears ?? state.experienceYears,
      offersDiscovery: offersDiscovery ?? state.offersDiscovery,
      maxClients: maxClients ?? state.maxClients,
    );
  }

  void toggleGym(Gym gym) {
    final gyms = List<Gym>.from(state.selectedGyms);
    final exists = gyms.any((g) => g.id == gym.id);
    if (exists) {
      gyms.removeWhere((g) => g.id == gym.id);
    } else if (gyms.length < 5) {
      gyms.add(gym);
    }
    state = state.copyWith(selectedGyms: gyms);
  }

  void nextStep() {
    if (state.step < totalSteps - 1) {
      state = state.copyWith(step: state.step + 1);
    }
  }

  void previousStep() {
    if (state.step > 0) {
      state = state.copyWith(step: state.step - 1);
    }
  }

  Future<bool> publishProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      await _service.saveCoachProfile(
        bio: state.bio.isNotEmpty ? state.bio : null,
        city: state.city.isNotEmpty ? state.city : null,
        specialties: state.selectedSpecialties,
        hourlyRateCents: state.hourlyRateEuros > 0 ? state.hourlyRateEuros * 100 : null,
        currency: state.currency,
        experienceYears: state.experienceYears,
        offersDiscovery: state.offersDiscovery,
        maxClients: state.maxClients,
      );
      for (final gym in state.selectedGyms) {
        await _service.addGym(gym.id);
      }
      state = state.copyWith(isLoading: false);
      return true;
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
      return false;
    }
  }

  void clearError() => state = state.copyWith(error: null);
}

final coachOnboardingProvider =
    StateNotifierProvider.autoDispose<CoachOnboardingNotifier, CoachOnboardingState>(
  (ref) => CoachOnboardingNotifier(ref.watch(onboardingServiceProvider)),
);

// ── Gym Search ───────────────────────────────────────────────────────────────

class GymSearchState {
  const GymSearchState({
    this.results = const [],
    this.isLoading = false,
    this.query = '',
    this.error,
  });

  final List<Gym> results;
  final bool isLoading;
  final String query;
  final String? error;

  GymSearchState copyWith({
    List<Gym>? results,
    bool? isLoading,
    String? query,
    String? error,
  }) =>
      GymSearchState(
        results: results ?? this.results,
        isLoading: isLoading ?? this.isLoading,
        query: query ?? this.query,
        error: error,
      );
}

class GymSearchNotifier extends StateNotifier<GymSearchState> {
  GymSearchNotifier(this._service) : super(const GymSearchState());

  final OnboardingService _service;

  Future<void> search(String query) async {
    state = state.copyWith(query: query, isLoading: true);
    try {
      final results = await _service.searchGyms(query);
      state = state.copyWith(results: results, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString(), results: []);
    }
  }

  void clear() => state = const GymSearchState();
}

final gymSearchProvider =
    StateNotifierProvider.autoDispose<GymSearchNotifier, GymSearchState>(
  (ref) => GymSearchNotifier(ref.watch(onboardingServiceProvider)),
);

// ── Enrollment ───────────────────────────────────────────────────────────────

class EnrollmentState {
  const EnrollmentState({
    this.coachData,
    this.isLoading = false,
    this.isEnrolling = false,
    this.error,
    this.enrolled = false,
  });

  final Map<String, dynamic>? coachData;
  final bool isLoading;
  final bool isEnrolling;
  final String? error;
  final bool enrolled;

  EnrollmentState copyWith({
    Map<String, dynamic>? coachData,
    bool? isLoading,
    bool? isEnrolling,
    String? error,
    bool? enrolled,
  }) =>
      EnrollmentState(
        coachData: coachData ?? this.coachData,
        isLoading: isLoading ?? this.isLoading,
        isEnrolling: isEnrolling ?? this.isEnrolling,
        error: error,
        enrolled: enrolled ?? this.enrolled,
      );
}

class EnrollmentNotifier extends StateNotifier<EnrollmentState> {
  EnrollmentNotifier(this._service) : super(const EnrollmentState());

  final OnboardingService _service;

  Future<void> loadToken(String token) async {
    state = state.copyWith(isLoading: true);
    try {
      final data = await _service.getEnrollmentInfo(token);
      state = state.copyWith(coachData: data, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> enroll(String token) async {
    state = state.copyWith(isEnrolling: true);
    try {
      await _service.enrollWithToken(token);
      state = state.copyWith(isEnrolling: false, enrolled: true);
      return true;
    } catch (e) {
      state = state.copyWith(isEnrolling: false, error: e.toString());
      return false;
    }
  }
}

final enrollmentProvider =
    StateNotifierProvider.autoDispose<EnrollmentNotifier, EnrollmentState>(
  (ref) => EnrollmentNotifier(ref.watch(onboardingServiceProvider)),
);
