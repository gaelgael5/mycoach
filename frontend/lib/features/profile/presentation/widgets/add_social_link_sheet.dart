import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/social_link.dart';
import '../providers/social_links_providers.dart';
import 'social_link_tile.dart';

/// Plateformes disponibles.
const _kPlatforms = [
  'instagram',
  'youtube',
  'tiktok',
  'linkedin',
  'x',
  'facebook',
  'twitch',
  'website',
  'custom',
];

/// Bottom sheet pour ajouter un lien social.
class AddSocialLinkSheet extends ConsumerStatefulWidget {
  const AddSocialLinkSheet({super.key});

  @override
  ConsumerState<AddSocialLinkSheet> createState() => _AddSocialLinkSheetState();
}

class _AddSocialLinkSheetState extends ConsumerState<AddSocialLinkSheet> {
  final _formKey = GlobalKey<FormState>();
  final _urlController = TextEditingController();
  final _labelController = TextEditingController();

  String? _selectedPlatform;
  String _visibility = LinkVisibility.public.value;
  bool _isLoading = false;

  @override
  void dispose() {
    _urlController.dispose();
    _labelController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l = context.l10n;
    final isCustom = _selectedPlatform == null || _selectedPlatform == 'custom';

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ─ Titre ────────────────────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(l.socialLinksAdd, style: AppTextStyles.headline4(AppColors.white)),
                IconButton(
                  icon: const Icon(Icons.close, color: AppColors.grey3),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // ─ Sélecteur plateforme ──────────────────────────────────────────
            Text(l.socialLinkPlatform, style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _kPlatforms.map((p) {
                final isSelected = _selectedPlatform == p ||
                    (p == 'custom' && (_selectedPlatform == null || _selectedPlatform == 'custom'));
                final platformName = p == 'custom' ? 'Custom' : p;
                return GestureDetector(
                  onTap: () => setState(() =>
                      _selectedPlatform = p == 'custom' ? null : p),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.accent.withOpacity(0.2)
                          : AppColors.bgCard,
                      borderRadius:
                          BorderRadius.circular(AppRadius.pill),
                      border: Border.all(
                        color: isSelected
                            ? AppColors.accent
                            : AppColors.grey7,
                      ),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          platformIcon(p == 'custom' ? null : p),
                          size: 14,
                          color: isSelected
                              ? AppColors.accent
                              : AppColors.grey3,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          platformName,
                          style: AppTextStyles.caption(
                            isSelected ? AppColors.accent : AppColors.grey3,
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),

            // ─ Champ URL ────────────────────────────────────────────────────
            Text(l.socialLinkUrl, style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            TextFormField(
              controller: _urlController,
              style: AppTextStyles.body1(AppColors.white),
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                prefixIcon:
                    Icon(Icons.link, color: AppColors.grey5, size: 18),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return l.validationRequired;
                return null;
              },
            ),
            const SizedBox(height: 12),

            // ─ Champ label (custom uniquement) ──────────────────────────────
            if (isCustom) ...[
              Text(l.socialLinkLabel, style: AppTextStyles.label(AppColors.grey3)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _labelController,
                style: AppTextStyles.body1(AppColors.white),
                decoration: InputDecoration(
                  hintText: '(${l.labelOptional})',
                  hintStyle: AppTextStyles.body1(AppColors.grey5),
                ),
              ),
              const SizedBox(height: 12),
            ],

            // ─ Visibilité ────────────────────────────────────────────────────
            Text(l.socialLinkVisibility, style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            Row(
              children: [
                _VisibilityChip(
                  label: l.socialLinkPublic,
                  selected: _visibility == LinkVisibility.public.value,
                  onTap: () => setState(
                    () => _visibility = LinkVisibility.public.value,
                  ),
                ),
                const SizedBox(width: 8),
                _VisibilityChip(
                  label: l.socialLinkCoachesOnly,
                  selected: _visibility == LinkVisibility.coachesOnly.value,
                  onTap: () => setState(
                    () => _visibility = LinkVisibility.coachesOnly.value,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // ─ Bouton ajouter ────────────────────────────────────────────────
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submit,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppColors.white,
                        ),
                      )
                    : Text(l.btnAdd),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      await ref.read(socialLinksNotifierProvider.notifier).addLink(
        platform:   _selectedPlatform,
        label:      _labelController.text.trim().isEmpty
            ? null
            : _labelController.text.trim(),
        url:        _urlController.text.trim(),
        visibility: _visibility,
      );
      if (mounted) Navigator.of(context).pop();
    } catch (_) {
      // Erreur gérée par le notifier
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

class _VisibilityChip extends StatelessWidget {
  const _VisibilityChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color:
              selected ? AppColors.accent.withOpacity(0.2) : AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          border: Border.all(
            color: selected ? AppColors.accent : AppColors.grey7,
          ),
        ),
        child: Text(
          label,
          style: AppTextStyles.caption(
            selected ? AppColors.accent : AppColors.grey3,
          ),
        ),
      ),
    );
  }
}
