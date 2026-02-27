import 'package:flutter/material.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';

/// Dropdown de sélection du genre — réutilisé sur les formulaires d'inscription.
class GenderDropdown extends StatelessWidget {
  const GenderDropdown({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final String? value;
  final ValueChanged<String?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${context.l10n.labelGender} (${context.l10n.labelOptional})',
          style: AppTextStyles.label(AppColors.grey3),
        ),
        const SizedBox(height: 6),
        DropdownButtonFormField<String>(
          value: value,
          dropdownColor: AppColors.bgCard,
          style: AppTextStyles.body1(AppColors.white),
          decoration: InputDecoration(
            filled: true,
            fillColor: AppColors.bgInput,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppRadius.input),
              borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppRadius.input),
              borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
            ),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
          ),
          hint: Text(
            context.l10n.labelGender,
            style: AppTextStyles.body1(AppColors.grey5),
          ),
          items: [
            DropdownMenuItem(
              value: 'male',
              child: Text(context.l10n.genderMale),
            ),
            DropdownMenuItem(
              value: 'female',
              child: Text(context.l10n.genderFemale),
            ),
            DropdownMenuItem(
              value: 'other',
              child: Text(context.l10n.genderOther),
            ),
          ],
          onChanged: onChanged,
        ),
      ],
    );
  }
}

/// Checkbox CGU — réutilisée sur les formulaires d'inscription.
class CguCheckbox extends StatelessWidget {
  const CguCheckbox({
    super.key,
    required this.value,
    required this.onChanged,
  });

  final bool value;
  final ValueChanged<bool?> onChanged;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 24,
          height: 24,
          child: Checkbox(
            value: value,
            onChanged: onChanged,
            activeColor: AppColors.accent,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(4),
            ),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: Wrap(
            children: [
              Text(
                context.l10n.registerCgu,
                style: AppTextStyles.body2(AppColors.grey3),
              ),
              GestureDetector(
                onTap: () {/* Phase A2: open CGU URL */},
                child: Text(
                  context.l10n.registerCguLink,
                  style: AppTextStyles.body2(AppColors.accent),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Bandeau d'erreur — réutilisé sur tous les formulaires d'authentification.
class AuthErrorBanner extends StatelessWidget {
  const AuthErrorBanner({super.key, required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.red.withOpacity(0.12),
        borderRadius: BorderRadius.circular(AppRadius.input),
        border: Border.all(color: AppColors.red.withOpacity(0.4)),
      ),
      child: Text(
        message,
        style: AppTextStyles.body2(AppColors.red),
        textAlign: TextAlign.center,
      ),
    );
  }
}
