import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';

/// Écran de choix du rôle lors de l'inscription.
/// Coach → RegisterCoachScreen | Client → RegisterClientScreen
class RegisterRoleScreen extends ConsumerWidget {
  const RegisterRoleScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.grey1),
          onPressed: () => context.go(AppRoutes.login),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 16),
              Text(
                context.l10n.registerTitle,
                style: AppTextStyles.headline1(AppColors.white),
              ),
              const SizedBox(height: 8),
              Text(
                context.l10n.registerRoleQuestion,
                style: AppTextStyles.body1(AppColors.grey3),
              ),
              const SizedBox(height: 48),

              // Card Coach
              _RoleCard(
                emoji: '🏋️',
                title: context.l10n.registerRoleCoach,
                description: context.l10n.registerRoleCoachDesc,
                color: AppColors.accent,
                onTap: () => context.go(AppRoutes.registerCoach),
              ),
              const SizedBox(height: 16),

              // Card Client
              _RoleCard(
                emoji: '🎯',
                title: context.l10n.registerRoleClient,
                description: context.l10n.registerRoleClientDesc,
                color: AppColors.blue,
                onTap: () => context.go(AppRoutes.registerClient),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  const _RoleCard({
    required this.emoji,
    required this.title,
    required this.description,
    required this.color,
    required this.onTap,
  });

  final String emoji;
  final String title;
  final String description;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.card),
          border: Border.all(color: AppColors.grey7, width: 1.5),
        ),
        child: Row(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.12),
                borderRadius: BorderRadius.circular(AppRadius.input),
              ),
              child: Center(
                child: Text(emoji, style: const TextStyle(fontSize: 28)),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.headline4(AppColors.white),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    description,
                    style: AppTextStyles.body2(AppColors.grey3),
                  ),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: AppColors.grey5),
          ],
        ),
      ),
    );
  }
}
