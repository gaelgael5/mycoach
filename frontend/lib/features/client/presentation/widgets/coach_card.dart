import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/coach_search_result.dart';

/// Carte coach pour les résultats de recherche.
class CoachCard extends StatelessWidget {
  const CoachCard({
    super.key,
    required this.coach,
    required this.onTap,
  });

  final CoachSearchResult coach;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.card),
          border: Border.all(color: AppColors.grey7, width: 1),
          boxShadow: AppShadows.card,
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _Avatar(url: coach.resolvedAvatarUrl),
              const SizedBox(width: 12),
              Expanded(child: _Info(coach: coach)),
            ],
          ),
        ),
      ),
    );
  }
}

class _Avatar extends StatelessWidget {
  const _Avatar({this.url});
  final String? url;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(AppRadius.avatar),
      child: url != null
          ? CachedNetworkImage(
              imageUrl: url!,
              width: 64,
              height: 64,
              fit: BoxFit.cover,
              errorWidget: (_, __, ___) => _fallback(),
            )
          : _fallback(),
    );
  }

  Widget _fallback() => Container(
        width: 64,
        height: 64,
        color: AppColors.bgInput,
        child: const Icon(Icons.person, color: AppColors.grey5, size: 32),
      );
}

class _Info extends StatelessWidget {
  const _Info({required this.coach});
  final CoachSearchResult coach;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                coach.fullName,
                style: AppTextStyles.headline4(AppColors.white),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (coach.isCertified)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.blueSurface,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
                child: Text(
                  '✓',
                  style: AppTextStyles.caption(AppColors.blue),
                ),
              ),
          ],
        ),
        if (coach.city != null) ...[
          const SizedBox(height: 2),
          Text(
            coach.city!,
            style: AppTextStyles.caption(AppColors.grey3),
          ),
        ],
        const SizedBox(height: 6),
        if (coach.specialties.isNotEmpty)
          Wrap(
            spacing: 4,
            runSpacing: 4,
            children: coach.specialties
                .take(3)
                .map(
                  (s) => Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.bgInput,
                      borderRadius: BorderRadius.circular(AppRadius.pill),
                      border:
                          Border.all(color: AppColors.grey7, width: 1),
                    ),
                    child: Text(s,
                        style: AppTextStyles.caption(AppColors.grey3)),
                  ),
                )
                .toList(),
          ),
        const SizedBox(height: 6),
        Row(
          children: [
            if (coach.hourlyRate != null)
              Text(
                '${coach.hourlyRate}€/h',
                style: AppTextStyles.label(AppColors.accent),
              ),
            if (coach.hourlyRate != null && coach.offersDiscovery)
              const SizedBox(width: 8),
            if (coach.offersDiscovery)
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.greenSurface,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
                child: Text(
                  l10n.coachDiscoveryBadge,
                  style: AppTextStyles.caption(AppColors.green),
                ),
              ),
            const Spacer(),
            if (coach.rating != null)
              Row(
                children: [
                  const Icon(Icons.star,
                      color: AppColors.yellow, size: 14),
                  const SizedBox(width: 2),
                  Text(
                    coach.rating!.toStringAsFixed(1),
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                ],
              ),
          ],
        ),
      ],
    );
  }
}
