import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/core_providers.dart';
import '../../features/auth/presentation/screens/splash_screen.dart';
import '../../features/auth/presentation/screens/login_screen.dart';
import '../../features/auth/presentation/screens/register_role_screen.dart';
import '../../features/auth/presentation/screens/register_client_screen.dart';
import '../../features/auth/presentation/screens/register_coach_screen.dart';
import '../../features/auth/presentation/screens/otp_sms_screen.dart';
import '../../features/auth/presentation/screens/email_verification_screen.dart';
import '../../features/auth/presentation/screens/forgot_password_screen.dart';
import '../../features/auth/presentation/screens/reset_password_screen.dart';
import '../../features/onboarding/presentation/screens/client_onboarding_screen.dart';
import '../../features/onboarding/presentation/screens/coach_onboarding_screen.dart';
import '../../features/onboarding/presentation/screens/enrollment_link_screen.dart';
import '../../features/profile/presentation/screens/profile_screen.dart';
import '../../features/profile/presentation/screens/social_links_screen.dart';
import '../../features/profile/presentation/screens/health_params_screen.dart';
import '../../features/profile/presentation/screens/health_sharing_screen.dart';
import '../../features/profile/presentation/screens/privacy_settings_screen.dart';
import '../../features/profile/presentation/screens/notification_preferences_screen.dart';
import '../../features/profile/presentation/screens/feedback_screen.dart';

// ── Noms des routes (évite les strings libres) ───────────────────────────────

abstract class AppRoutes {
  // Auth
  static const splash          = '/';
  static const login           = '/login';
  static const registerRole    = '/register';
  static const registerClient  = '/register/client';
  static const registerCoach   = '/register/coach';
  static const verifyPhone     = '/verify/phone';
  static const verifyEmail     = '/verify/email';
  static const forgotPassword  = '/forgot-password';
  static const resetPassword   = '/reset-password';

  // Onboarding
  static const onboardingClient = '/onboarding/client';
  static const onboardingCoach  = '/onboarding/coach';
  static const enroll           = '/enroll/:token';       // deep link

  // Client — navigation principale
  static const clientHome     = '/home';
  static const coachSearch    = '/coaches';
  static const coachProfile   = '/coaches/:id';
  static const bookingCal     = '/coaches/:id/book';
  static const bookingConfirm = '/coaches/:id/book/confirm';
  static const waitlist       = '/waitlist/:bookingId';
  static const clientAgenda   = '/agenda';

  // Client — tracking
  static const workoutStart   = '/workout/start';
  static const workoutSession = '/workout/session';
  static const addExercise    = '/workout/add-exercise';
  static const exerciseDetail = '/workout/exercise/:exerciseId';
  static const restTimer      = '/workout/rest';
  static const workoutSummary = '/workout/summary';

  // Profil & Paramètres (Phase A3)
  static const profile              = '/profile';
  static const profileSocialLinks   = '/profile/social-links';
  static const profileHealthParams  = '/profile/health-params';
  static const profileHealthSharing = '/profile/health-sharing';
  static const profilePrivacy       = '/profile/privacy';
  static const profileNotifications = '/profile/notifications';
  static const profileFeedback      = '/profile/feedback';

  // Coach — navigation principale
  static const coachHome      = '/coach/home';
  static const coachClients   = '/coach/clients';
  static const coachAgenda    = '/coach/agenda';
  static const coachPerfs     = '/coach/perfs';
  static const coachProfile_  = '/coach/profile'; // profil coach (édition)
}

/// Provider du routeur go_router.
///
/// Gestion de la redirection d'authentification :
/// - Pas d'API Key → /login
/// - API Key présente mais rôle inconnu → /login (auto-login en cours)
/// - Connecté client → /home
/// - Connecté coach → /coach/home
final routerProvider = Provider<GoRouter>((ref) {
  final role = ref.watch(userRoleProvider);

  return GoRouter(
    initialLocation: AppRoutes.splash,
    debugLogDiagnostics: false,
    redirect: (context, state) {
      final isOnAuth = _isAuthRoute(state.uri.path);
      // Pas encore d'état connu → on laisse passer (SplashScreen gère l'auto-login)
      if (role == null) return null;
      // Connecté sur route d'auth → redirect dashboard
      if (isOnAuth) {
        return role == 'coach' ? AppRoutes.coachHome : AppRoutes.clientHome;
      }
      return null;
    },
    routes: [
      // ── Splash ─────────────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.splash,
        name: 'splash',
        builder: (ctx, state) => const SplashScreen(),
      ),

      // ── Auth ────────────────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        builder: (ctx, state) => const LoginScreen(),
      ),
      GoRoute(
        path: AppRoutes.registerRole,
        name: 'register-role',
        builder: (ctx, state) => const RegisterRoleScreen(),
      ),
      GoRoute(
        path: AppRoutes.registerClient,
        name: 'register-client',
        builder: (ctx, state) => const RegisterClientScreen(),
      ),
      GoRoute(
        path: AppRoutes.registerCoach,
        name: 'register-coach',
        builder: (ctx, state) => const RegisterCoachScreen(),
      ),
      GoRoute(
        path: AppRoutes.verifyPhone,
        name: 'verify-phone',
        builder: (ctx, state) => const OtpSmsScreen(),
      ),
      GoRoute(
        path: AppRoutes.verifyEmail,
        name: 'verify-email',
        builder: (ctx, state) => const EmailVerificationScreen(),
      ),
      GoRoute(
        path: AppRoutes.forgotPassword,
        name: 'forgot-password',
        builder: (ctx, state) => const ForgotPasswordScreen(),
      ),
      GoRoute(
        path: AppRoutes.resetPassword,
        name: 'reset-password',
        builder: (ctx, state) => ResetPasswordScreen(
          token: state.uri.queryParameters['token'],
        ),
      ),

      // ── Onboarding ──────────────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.onboardingClient,
        name: 'onboarding-client',
        builder: (ctx, state) => const ClientOnboardingScreen(),
      ),
      GoRoute(
        path: AppRoutes.onboardingCoach,
        name: 'onboarding-coach',
        builder: (ctx, state) => const CoachOnboardingScreen(),
      ),

      // ── Deep link enrollment ─────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.enroll,
        name: 'enroll',
        builder: (ctx, state) {
          final token = state.pathParameters['token'] ?? '';
          return EnrollmentLinkScreen(token: token);
        },
      ),

      // ── Profil & Paramètres (Phase A3) ───────────────────────────────────
      GoRoute(
        path: AppRoutes.profile,
        name: 'profile',
        builder: (ctx, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: AppRoutes.profileSocialLinks,
        name: 'profile-social-links',
        builder: (ctx, state) => const SocialLinksScreen(),
      ),
      GoRoute(
        path: AppRoutes.profileHealthParams,
        name: 'profile-health-params',
        builder: (ctx, state) => const HealthParamsScreen(),
      ),
      GoRoute(
        path: AppRoutes.profileHealthSharing,
        name: 'profile-health-sharing',
        builder: (ctx, state) => const HealthSharingScreen(),
      ),
      GoRoute(
        path: AppRoutes.profilePrivacy,
        name: 'profile-privacy',
        builder: (ctx, state) => const PrivacySettingsScreen(),
      ),
      GoRoute(
        path: AppRoutes.profileNotifications,
        name: 'profile-notifications',
        builder: (ctx, state) => const NotificationPreferencesScreen(),
      ),
      GoRoute(
        path: AppRoutes.profileFeedback,
        name: 'profile-feedback',
        builder: (ctx, state) => const FeedbackScreen(),
      ),

      // ── Client — shell avec Bottom Nav ────────────────────────────────────
      ShellRoute(
        builder: (ctx, state, child) => _ClientShell(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.clientHome,
            name: 'client-home',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Dashboard Client'),
          ),
          GoRoute(
            path: AppRoutes.coachSearch,
            name: 'coach-search',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Recherche Coachs'),
            routes: [
              GoRoute(
                path: ':id',
                name: 'coach-profile',
                builder: (ctx, state) {
                  final id = state.pathParameters['id']!;
                  return _PlaceholderScreen(label: 'Profil Coach $id');
                },
                routes: [
                  GoRoute(
                    path: 'book',
                    name: 'booking-cal',
                    builder: (ctx, state) => const _PlaceholderScreen(label: 'Calendrier Réservation'),
                    routes: [
                      GoRoute(
                        path: 'confirm',
                        name: 'booking-confirm',
                        builder: (ctx, state) => const _PlaceholderScreen(label: 'Confirmation Réservation'),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          GoRoute(
            path: AppRoutes.clientAgenda,
            name: 'client-agenda',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Agenda Client'),
          ),
          GoRoute(
            path: AppRoutes.workoutStart,
            name: 'workout-start',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Démarrer Séance'),
          ),
        ],
      ),

      // ── Waitlist (hors shell) ─────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.waitlist,
        name: 'waitlist',
        builder: (ctx, state) {
          final id = state.pathParameters['bookingId']!;
          return _PlaceholderScreen(label: 'Liste attente ($id)');
        },
      ),

      // ── Workout (hors shell — plein écran) ───────────────────────────────
      GoRoute(
        path: AppRoutes.workoutSession,
        name: 'workout-session',
        builder: (ctx, state) => const _PlaceholderScreen(label: 'Séance en cours'),
      ),
      GoRoute(
        path: AppRoutes.addExercise,
        name: 'add-exercise',
        builder: (ctx, state) => const _PlaceholderScreen(label: 'Ajouter Exercice'),
      ),
      GoRoute(
        path: AppRoutes.exerciseDetail,
        name: 'exercise-detail',
        builder: (ctx, state) {
          final id = state.pathParameters['exerciseId']!;
          return _PlaceholderScreen(label: 'Exercice $id');
        },
      ),
      GoRoute(
        path: AppRoutes.restTimer,
        name: 'rest-timer',
        builder: (ctx, state) => const _PlaceholderScreen(label: 'Timer Repos'),
      ),
      GoRoute(
        path: AppRoutes.workoutSummary,
        name: 'workout-summary',
        builder: (ctx, state) => const _PlaceholderScreen(label: 'Résumé Séance'),
      ),

      // ── Coach — shell avec Bottom Nav ─────────────────────────────────────
      ShellRoute(
        builder: (ctx, state, child) => _CoachShell(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.coachHome,
            name: 'coach-home',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Dashboard Coach'),
          ),
          GoRoute(
            path: AppRoutes.coachClients,
            name: 'coach-clients',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Clients Coach'),
          ),
          GoRoute(
            path: AppRoutes.coachAgenda,
            name: 'coach-agenda',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Agenda Coach'),
          ),
          GoRoute(
            path: AppRoutes.coachPerfs,
            name: 'coach-perfs',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Perfs Coach'),
          ),
          GoRoute(
            path: AppRoutes.coachProfile_,
            name: 'coach-profile-edit',
            builder: (ctx, state) => const _PlaceholderScreen(label: 'Profil Coach'),
          ),
        ],
      ),
    ],
  );
});

// ── Helpers ──────────────────────────────────────────────────────────────────

bool _isAuthRoute(String path) => const {
  AppRoutes.login,
  AppRoutes.registerRole,
  AppRoutes.registerClient,
  AppRoutes.registerCoach,
  AppRoutes.verifyPhone,
  AppRoutes.verifyEmail,
  AppRoutes.forgotPassword,
  AppRoutes.resetPassword,
}.any(path.startsWith);

// ── Shells (bottom navigation) ───────────────────────────────────────────────

/// Shell Client — Bottom Nav 5 onglets.
class _ClientShell extends StatelessWidget {
  const _ClientShell({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: const _ClientBottomNav(),
    );
  }
}

class _ClientBottomNav extends StatelessWidget {
  const _ClientBottomNav();

  @override
  Widget build(BuildContext context) {
    // Placeholder — remplacé en Phase A4 par le vrai bottom nav avec go_router
    return const BottomAppBar(child: SizedBox(height: 56));
  }
}

/// Shell Coach — Bottom Nav 5 onglets.
class _CoachShell extends StatelessWidget {
  const _CoachShell({required this.child});
  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: const _CoachBottomNav(),
    );
  }
}

class _CoachBottomNav extends StatelessWidget {
  const _CoachBottomNav();

  @override
  Widget build(BuildContext context) {
    return const BottomAppBar(child: SizedBox(height: 56));
  }
}

// ── Placeholder (Phase A0 — remplacé par les vrais écrans en A1+) ─────────────

class _PlaceholderScreen extends StatelessWidget {
  const _PlaceholderScreen({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(label)),
      body: Center(
        child: Text(
          label,
          style: Theme.of(context).textTheme.bodyLarge,
        ),
      ),
    );
  }
}
