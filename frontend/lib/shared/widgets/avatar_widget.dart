import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../shared/models/user.dart';

/// Widget d'avatar utilisateur avec placeholder selon le genre.
///
/// - Si [avatarUrl] est fourni → affiche l'image avec fallback
/// - Sinon → icône placeholder selon [gender]
/// - Si [editable] → overlay avec bouton appareil photo
class AvatarWidget extends StatelessWidget {
  const AvatarWidget({
    super.key,
    this.avatarUrl,
    this.gender,
    this.size = 80,
    this.editable = false,
    this.onEditTap,
  });

  final String? avatarUrl;
  final Gender? gender;
  final double size;
  final bool editable;
  final VoidCallback? onEditTap;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        _buildAvatar(),
        if (editable) _buildEditOverlay(),
      ],
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.bgCard,
        border: Border.all(
          color: AppColors.accent.withOpacity(0.4),
          width: 2,
        ),
      ),
      clipBehavior: Clip.antiAlias,
      child: avatarUrl != null ? _buildNetworkImage() : _buildPlaceholder(),
    );
  }

  Widget _buildNetworkImage() {
    return Image.network(
      avatarUrl!,
      width: size,
      height: size,
      fit: BoxFit.cover,
      errorBuilder: (context, error, stackTrace) => _buildPlaceholder(),
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Center(
          child: CircularProgressIndicator(
            value: loadingProgress.expectedTotalBytes != null
                ? loadingProgress.cumulativeBytesLoaded /
                    loadingProgress.expectedTotalBytes!
                : null,
            strokeWidth: 2,
            color: AppColors.accent,
          ),
        );
      },
    );
  }

  Widget _buildPlaceholder() {
    final icon = _genderIcon();
    return Container(
      width: size,
      height: size,
      color: AppColors.bgInput,
      child: Icon(
        icon,
        size: size * 0.55,
        color: AppColors.grey5,
      ),
    );
  }

  IconData _genderIcon() {
    switch (gender) {
      case Gender.male:
        return Icons.person;
      case Gender.female:
        return Icons.person_outline;
      case Gender.other:
        return Icons.person_2_outlined;
      case null:
        return Icons.account_circle_outlined;
    }
  }

  Widget _buildEditOverlay() {
    return Positioned(
      bottom: 0,
      right: 0,
      child: GestureDetector(
        onTap: onEditTap,
        child: Container(
          width: size * 0.33,
          height: size * 0.33,
          decoration: BoxDecoration(
            color: AppColors.accent,
            shape: BoxShape.circle,
            border: Border.all(color: AppColors.bgDark, width: 2),
          ),
          child: Icon(
            Icons.camera_alt,
            size: size * 0.18,
            color: AppColors.white,
          ),
        ),
      ),
    );
  }
}
