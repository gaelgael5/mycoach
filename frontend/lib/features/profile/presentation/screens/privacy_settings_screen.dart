import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/profile_providers.dart';

/// Écran de confidentialité et RGPD.
class PrivacySettingsScreen extends ConsumerWidget {
  const PrivacySettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l           = context.l10n;
    final privacyAsync = ref.watch(privacyNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.privacyTitle),
      ),
      body: privacyAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) {
          // Si l'endpoint n'existe pas encore, on affiche quand même la page
          return _PrivacyBody(
            consentAnalytics: false,
            consentMarketing: false,
          );
        },
        data: (data) {
          final analytics = data['consent_analytics'] as bool? ?? false;
          final marketing = data['consent_marketing'] as bool? ?? false;
          return _PrivacyBody(
            consentAnalytics: analytics,
            consentMarketing: marketing,
          );
        },
      ),
    );
  }
}

class _PrivacyBody extends ConsumerWidget {
  const _PrivacyBody({
    required this.consentAnalytics,
    required this.consentMarketing,
  });

  final bool consentAnalytics;
  final bool consentMarketing;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ─ Toggles ──────────────────────────────────────────────────────
          Text(l.privacyTitle,
              style: AppTextStyles.label(AppColors.grey3)),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: AppColors.bgCard,
              borderRadius: BorderRadius.circular(AppRadius.card),
              border: Border.all(color: AppColors.grey7),
            ),
            child: Column(
              children: [
                SwitchListTile(
                  value: consentAnalytics,
                  onChanged: (val) {
                    ref
                        .read(privacyNotifierProvider.notifier)
                        .update(consentAnalytics: val);
                  },
                  activeColor: AppColors.accent,
                  title: Text(l.privacyAnalytics,
                      style: AppTextStyles.body1(AppColors.white)),
                  subtitle: Text(
                    'Amélioration de l\'application',
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                ),
                Divider(height: 1, color: AppColors.grey7),
                SwitchListTile(
                  value: consentMarketing,
                  onChanged: (val) {
                    ref
                        .read(privacyNotifierProvider.notifier)
                        .update(consentMarketing: val);
                  },
                  activeColor: AppColors.accent,
                  title: Text(l.privacyMarketing,
                      style: AppTextStyles.body1(AppColors.white)),
                  subtitle: Text(
                    'Offres personnalisées',
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // ─ Actions ──────────────────────────────────────────────────────
          Text('Actions', style: AppTextStyles.label(AppColors.grey3)),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _downloadData(context),
              icon: const Icon(Icons.download_outlined, size: 18),
              label: Text(l.privacyDownload),
            ),
          ),
          const SizedBox(height: 12),

          // ─ Liens légaux ─────────────────────────────────────────────────
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: () => _launchUrl('https://mycoach.app/cgu'),
              child: const Text('Conditions Générales d\'Utilisation'),
            ),
          ),
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: () =>
                  _launchUrl('https://mycoach.app/privacy-policy'),
              child: const Text('Politique de confidentialité'),
            ),
          ),
          const SizedBox(height: 24),

          // ─ Bouton suppression compte ─────────────────────────────────────
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () => _confirmDelete(context),
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.red,
                side: const BorderSide(color: AppColors.red),
              ),
              child: Text(l.privacyDelete),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _downloadData(BuildContext context) async {
    final l = context.l10n;
    // Afficher un message (endpoint à implémenter)
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(l.feedbackSent),
        backgroundColor: AppColors.green,
      ),
    );
  }

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  Future<void> _confirmDelete(BuildContext context) async {
    final l = context.l10n;
    await showDialog<void>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppColors.bgCard,
        title: Text(l.privacyDelete,
            style: AppTextStyles.headline4(AppColors.white)),
        content: Text(l.privacyDeleteConfirm,
            style: AppTextStyles.body1(AppColors.grey3)),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(l.btnCancel),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            style: TextButton.styleFrom(foregroundColor: AppColors.red),
            child: Text(l.privacyDelete),
          ),
        ],
      ),
    );
  }
}
