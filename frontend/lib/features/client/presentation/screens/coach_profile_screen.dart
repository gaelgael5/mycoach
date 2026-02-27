import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../providers/coach_search_providers.dart';

class CoachProfileScreen extends ConsumerWidget {
  const CoachProfileScreen({super.key, required this.coachId});

  final String coachId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final profileAsync = ref.watch(coachProfileProvider(coachId));

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: profileAsync.when(
        loading: () => const Center(
            child: CircularProgressIndicator(color: AppColors.accent)),
        error: (e, _) => Center(
          child: Text(l10n.errorGeneric,
              style: AppTextStyles.body1(AppColors.red)),
        ),
        data: (coach) => CustomScrollView(
          slivers: [
            // App bar with avatar
            SliverAppBar(
              expandedHeight: 220,
              backgroundColor: AppColors.bgDark,
              pinned: true,
              leading: IconButton(
                icon: const Icon(Icons.arrow_back, color: AppColors.white),
                onPressed: () => context.pop(),
              ),
              flexibleSpace: FlexibleSpaceBar(
                background: Stack(
                  fit: StackFit.expand,
                  children: [
                    if (coach.resolvedAvatarUrl != null)
                      CachedNetworkImage(
                        imageUrl: coach.resolvedAvatarUrl!,
                        fit: BoxFit.cover,
                        errorWidget: (_, __, ___) => Container(
                            color: AppColors.bgCard),
                      )
                    else
                      Container(
                        color: AppColors.bgCard,
                        child: const Icon(Icons.person,
                            color: AppColors.grey5, size: 80),
                      ),
                    Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [
                            Colors.transparent,
                            AppColors.bgDark,
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // Name + city
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              coach.fullName,
                              style: AppTextStyles.headline2(AppColors.white),
                            ),
                            if (coach.gyms.isNotEmpty)
                              Text(
                                coach.gyms.first.city,
                                style:
                                    AppTextStyles.body2(AppColors.grey3),
                              ),
                          ],
                        ),
                      ),
                      if (coach.isCertified)
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.blueSurface,
                            borderRadius:
                                BorderRadius.circular(AppRadius.pill),
                          ),
                          child: Text(
                            l10n.coachProfileCertifiedBadge,
                            style: AppTextStyles.caption(AppColors.blue),
                          ),
                        ),
                    ],
                  ),
                  // Rating
                  if (coach.rating != null) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.star,
                            color: AppColors.yellow, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          l10n.coachProfileRating(
                              coach.rating!, coach.reviewCount),
                          style: AppTextStyles.body2(AppColors.grey3),
                        ),
                      ],
                    ),
                  ],
                  const SizedBox(height: 16),
                  // Price
                  if (coach.sessionPriceCents != null) ...[
                    Row(
                      children: [
                        Text(
                          l10n.coachProfilePricePerSession(
                              coach.sessionPriceCents! ~/ 100),
                          style: AppTextStyles.headline4(AppColors.accent),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                  ],
                  // Discovery badge
                  if (coach.offersDiscovery) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.greenSurface,
                        borderRadius:
                            BorderRadius.circular(AppRadius.card),
                        border: Border.all(color: AppColors.green),
                      ),
                      child: Text(
                        l10n.coachDiscoveryBadge,
                        style: AppTextStyles.body1(AppColors.green),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  // Specialties
                  if (coach.specialties.isNotEmpty) ...[
                    Text(
                      l10n.onboardingSpecialties,
                      style: AppTextStyles.label(AppColors.grey3),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 6,
                      children: coach.specialties
                          .map(
                            (s) => Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 5),
                              decoration: BoxDecoration(
                                color: AppColors.bgInput,
                                borderRadius: BorderRadius.circular(
                                    AppRadius.pill),
                                border: Border.all(
                                    color: AppColors.grey7, width: 1),
                              ),
                              child: Text(s,
                                  style:
                                      AppTextStyles.body2(AppColors.grey3)),
                            ),
                          )
                          .toList(),
                    ),
                    const SizedBox(height: 16),
                  ],
                  // Bio
                  if (coach.bio != null && coach.bio!.isNotEmpty) ...[
                    Text(
                      l10n.coachProfileAbout,
                      style: AppTextStyles.label(AppColors.grey3),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      coach.bio!,
                      style: AppTextStyles.body1(AppColors.grey1),
                    ),
                    const SizedBox(height: 24),
                  ],
                  // Book button
                  ElevatedButton(
                    onPressed: () => context.go(
                        '${AppRoutes.coachSearch}/$coachId/book'),
                    child: Text(l10n.coachProfileBook),
                  ),
                  const SizedBox(height: 32),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
