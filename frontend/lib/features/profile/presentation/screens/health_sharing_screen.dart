import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/health_providers.dart';

/// Écran de partage des données de santé avec les coachs.
///
/// Pour la Phase A3, on affiche une interface qui liste les paramètres
/// partageables. Les relations coach seront chargées en A4/A5.
/// On utilise un coachId de démonstration.
class HealthSharingScreen extends ConsumerWidget {
  const HealthSharingScreen({
    super.key,
    this.coachId = 'demo_coach_id',
  });

  final String coachId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l          = context.l10n;
    final paramsAsync = ref.watch(healthParametersProvider);
    final sharingNotifier = ref.watch(
      healthSharingNotifierProvider(coachId).notifier,
    );
    final sharingAsync = ref.watch(
      healthSharingNotifierProvider(coachId),
    );

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.healthSharingTitle),
      ),
      body: paramsAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) => Center(
          child: Text(l.errorGeneric,
              style: AppTextStyles.body1(AppColors.grey3)),
        ),
        data: (params) {
          final sharing = sharingAsync.valueOrNull;
          final sharedList = (sharing?['shared_params'] as List<dynamic>?)
                  ?.cast<String>() ??
              [];
          final blockedList = (sharing?['blocked_params'] as List<dynamic>?)
                  ?.cast<String>() ??
              [];

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Info bulle
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: AppColors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(AppRadius.card),
                  border: Border.all(
                      color: AppColors.blue.withOpacity(0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.info_outline,
                        color: AppColors.blue, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        l.healthSharingWith(coachId),
                        style: AppTextStyles.caption(AppColors.grey3),
                      ),
                    ),
                  ],
                ),
              ),
              ...params.map((param) {
                final locale = Localizations.localeOf(context).languageCode;
                final label  = param.labelFor(locale);
                final isBlocked = blockedList.contains(param.slug);
                final isShared  = sharedList.contains(param.slug) ||
                    (!isBlocked && sharedList.isEmpty);
                return Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  decoration: BoxDecoration(
                    color: AppColors.bgCard,
                    borderRadius: BorderRadius.circular(AppRadius.card),
                    border: Border.all(color: AppColors.grey7),
                  ),
                  child: SwitchListTile(
                    value: isShared,
                    onChanged: (val) => sharingNotifier.toggleSharing(
                      param.slug,
                      val,
                    ),
                    activeColor: AppColors.accent,
                    title: Text(
                      label,
                      style: AppTextStyles.body1(AppColors.white),
                    ),
                    subtitle: Text(
                      '${param.unit}',
                      style: AppTextStyles.caption(AppColors.grey3),
                    ),
                  ),
                );
              }),
            ],
          );
        },
      ),
    );
  }
}
