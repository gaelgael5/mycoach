import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';

/// Badge "Record Personnel" affiché sur les séries records.
class PrBadge extends StatelessWidget {
  const PrBadge({super.key, this.small = false});

  final bool small;

  @override
  Widget build(BuildContext context) {
    final size = small ? 10.0 : 12.0;
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: small ? 6 : 8,
        vertical: small ? 2 : 3,
      ),
      decoration: BoxDecoration(
        color: AppColors.yellow.withOpacity(0.15),
        borderRadius: BorderRadius.circular(AppRadius.pill),
        border: Border.all(color: AppColors.yellow, width: 1),
      ),
      child: Text(
        context.l10n.performancePR,
        style: AppTextStyles.caption(AppColors.yellow).copyWith(
          fontSize: size,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}
