import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/social_link.dart';

/// Icône correspondant à la plateforme d'un lien social.
IconData platformIcon(String? platform) {
  switch (platform) {
    case 'instagram':
      return Icons.camera_alt;
    case 'youtube':
      return Icons.play_circle;
    case 'tiktok':
      return Icons.music_note;
    case 'linkedin':
      return Icons.work;
    case 'x':
    case 'twitter':
      return Icons.alternate_email;
    case 'facebook':
      return Icons.facebook;
    case 'twitch':
      return Icons.videogame_asset;
    case 'website':
      return Icons.language;
    default:
      return Icons.link;
  }
}

/// Couleur correspondant à la plateforme d'un lien social.
Color platformColor(String? platform) {
  switch (platform) {
    case 'instagram':
      return const Color(0xFFE1306C);
    case 'youtube':
      return const Color(0xFFFF0000);
    case 'tiktok':
      return const Color(0xFF69C9D0);
    case 'linkedin':
      return const Color(0xFF0077B5);
    case 'x':
    case 'twitter':
      return const Color(0xFF1DA1F2);
    case 'facebook':
      return const Color(0xFF1877F2);
    case 'twitch':
      return const Color(0xFF9146FF);
    case 'website':
      return AppColors.blue;
    default:
      return AppColors.grey3;
  }
}

/// Tuile représentant un lien social avec action de suppression.
class SocialLinkTile extends StatelessWidget {
  const SocialLinkTile({
    super.key,
    required this.link,
    this.onDelete,
  });

  final SocialLink link;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final color = platformColor(link.platform);
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7),
      ),
      child: ListTile(
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(platformIcon(link.platform), color: color, size: 20),
        ),
        title: Text(
          link.displayLabel,
          style: AppTextStyles.body1(AppColors.white),
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          link.url,
          style: AppTextStyles.caption(AppColors.grey3),
          overflow: TextOverflow.ellipsis,
        ),
        trailing: onDelete != null
            ? IconButton(
                icon: const Icon(Icons.close, color: AppColors.red, size: 20),
                onPressed: onDelete,
              )
            : null,
      ),
    );
  }
}
