import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

/// Bouton d'authentification sociale (Google, Apple…).
/// Affiche une icône + un texte, style outlined sur fond sombre.
class SocialAuthButton extends StatelessWidget {
  const SocialAuthButton({
    super.key,
    required this.label,
    required this.iconBuilder,
    required this.onPressed,
    this.isLoading = false,
  });

  final String label;
  final Widget Function() iconBuilder;
  final VoidCallback? onPressed;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: isLoading ? null : onPressed,
      style: OutlinedButton.styleFrom(
        backgroundColor: AppColors.bgCard,
        foregroundColor: AppColors.white,
        side: BorderSide(color: AppColors.grey7, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppRadius.card),
        ),
        minimumSize: const Size(double.infinity, 52),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      ),
      child: isLoading
          ? SizedBox(
              height: 20,
              width: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: AppColors.grey3,
              ),
            )
          : Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                iconBuilder(),
                const SizedBox(width: 12),
                Text(
                  label,
                  style: AppTextStyles.body1(AppColors.grey1),
                ),
              ],
            ),
    );
  }
}

/// Widget icône Google (lettres colorées) — pas besoin d'asset externe.
class GoogleIcon extends StatelessWidget {
  const GoogleIcon({super.key, this.size = 20.0});

  final double size;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        children: [
          Center(
            child: Text(
              'G',
              style: TextStyle(
                fontSize: size * 0.85,
                fontWeight: FontWeight.w700,
                color: const Color(0xFF4285F4), // bleu Google
                fontFamily: 'Arial',
              ),
            ),
          ),
        ],
      ),
    );
  }
}
