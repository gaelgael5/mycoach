import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

/// Bouton primaire avec gradient orange du design system.
/// Utilisé sur tous les formulaires d'authentification.
class GradientButton extends StatelessWidget {
  const GradientButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.isLoading = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final active = onPressed != null && !isLoading;
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: active ? AppGradients.accentButton : null,
        color: active ? null : AppColors.grey5,
        borderRadius: BorderRadius.circular(AppRadius.card),
        boxShadow: active ? AppShadows.accent : null,
      ),
      child: ElevatedButton(
        onPressed: (isLoading || onPressed == null) ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          disabledBackgroundColor: Colors.transparent,
          minimumSize: const Size(double.infinity, 54),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.card),
          ),
        ),
        child: isLoading
            ? const SizedBox(
                height: 22,
                width: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.5,
                  color: AppColors.white,
                ),
              )
            : Text(label, style: AppTextStyles.buttonPrimary()),
      ),
    );
  }
}
