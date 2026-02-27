import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';

/// Écran de démarrage — gère l'auto-login.
/// - Montre logo + tagline pendant la vérification de session.
/// - Redirige vers home (client/coach) ou login selon le résultat.
class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Réagit au changement d'état d'auth pour naviguer
    ref.listen<AsyncValue<dynamic>>(authStateProvider, (_, next) {
      next.whenOrNull(
        data: (user) {
          if (user != null) {
            final role = ref.read(userRoleProvider);
            if (role == 'coach') {
              context.go(AppRoutes.coachHome);
            } else {
              context.go(AppRoutes.clientHome);
            }
          } else {
            context.go(AppRoutes.login);
          }
        },
        error: (_, __) => context.go(AppRoutes.login),
      );
    });

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppGradients.splash,
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  gradient: AppGradients.accentButton,
                  borderRadius: BorderRadius.circular(AppRadius.card),
                  boxShadow: AppShadows.accent,
                ),
                child: const Icon(
                  Icons.fitness_center,
                  color: AppColors.white,
                  size: 44,
                ),
              ),
              const SizedBox(height: 24),
              // Nom app
              Text(
                context.l10n.appName,
                style: AppTextStyles.headline1(AppColors.white),
              ),
              const SizedBox(height: 8),
              Text(
                context.l10n.splashTagline,
                style: AppTextStyles.body1(AppColors.grey3),
              ),
              const SizedBox(height: 64),
              // Indicateur de chargement
              SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: AppColors.accent,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
