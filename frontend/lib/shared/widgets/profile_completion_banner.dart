import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/extensions/context_ext.dart';
import '../../core/router/router.dart';
import '../../core/theme/app_theme.dart';
import '../models/user.dart';

/// Calcule le pourcentage de complétion d'un profil utilisateur.
int computeProfileCompletion(User user) {
  final fields = [
    user.firstName.isNotEmpty,
    user.lastName.isNotEmpty,
    user.gender != null,
    user.birthYear != null,
    user.phone != null && user.phone!.isNotEmpty,
    user.avatarUrl != null,
    user.timezone != null,
  ];
  final filled = fields.where((f) => f).length;
  return ((filled / fields.length) * 100).round();
}

/// Bandeau de progression du profil — affiché sur le dashboard.
///
/// Affiche le % de complétion et un bouton pour compléter le profil.
/// Se masque si le profil est complet à 100%.
class ProfileCompletionBanner extends StatelessWidget {
  const ProfileCompletionBanner({
    super.key,
    required this.user,
  });

  final User user;

  @override
  Widget build(BuildContext context) {
    final percent = computeProfileCompletion(user);

    if (percent >= 100) return const SizedBox.shrink();

    final isCoach = user.role.isCoach;
    final l10n = context.l10n;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  l10n.completionBannerTitle(percent),
                  style: AppTextStyles.body1(AppColors.white),
                ),
              ),
              TextButton(
                onPressed: () {
                  final route = isCoach
                      ? AppRoutes.onboardingCoach
                      : AppRoutes.onboardingClient;
                  context.go(route);
                },
                style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  minimumSize: Size.zero,
                ),
                child: Text(l10n.completionBannerAction),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percent / 100,
              backgroundColor: AppColors.grey7,
              valueColor: AlwaysStoppedAnimation<Color>(
                percent < 40
                    ? AppColors.red
                    : percent < 75
                        ? AppColors.yellow
                        : AppColors.accent,
              ),
              minHeight: 6,
            ),
          ),
        ],
      ),
    );
  }
}
