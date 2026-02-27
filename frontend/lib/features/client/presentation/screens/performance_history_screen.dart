import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../providers/performance_providers.dart';
import '../widgets/performance_chart.dart';
import '../widgets/pr_badge.dart';

class PerformanceHistoryScreen extends ConsumerWidget {
  const PerformanceHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final prsAsync = ref.watch(personalRecordsProvider);
    final sessionsAsync = ref.watch(performanceSessionsProvider);
    final selectedSlug = ref.watch(selectedExerciseSlugProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.performanceTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(personalRecordsProvider);
          ref.invalidate(performanceSessionsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // PR list
              prsAsync.when(
                loading: () => const Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(
                      color: AppColors.accent),
                ),
                error: (_, __) => const SizedBox.shrink(),
                data: (prs) {
                  if (prs.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(20),
                      child: Text(l10n.performanceEmpty,
                          style:
                              AppTextStyles.body1(AppColors.grey3)),
                    );
                  }
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                        child: Text(
                          l10n.performancePR,
                          style: AppTextStyles.headline4(AppColors.white),
                        ),
                      ),
                      SizedBox(
                        height: 88,
                        child: ListView.separated(
                          scrollDirection: Axis.horizontal,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16),
                          itemCount: prs.length,
                          separatorBuilder: (_, __) =>
                              const SizedBox(width: 12),
                          itemBuilder: (ctx, i) {
                            final pr = prs[i];
                            final isSelected =
                                selectedSlug == pr.exerciseSlug;
                            return GestureDetector(
                              onTap: () {
                                ref
                                    .read(selectedExerciseSlugProvider
                                        .notifier)
                                    .state = isSelected
                                    ? null
                                    : pr.exerciseSlug;
                              },
                              child: Container(
                                width: 140,
                                padding: const EdgeInsets.all(10),
                                decoration: BoxDecoration(
                                  color: isSelected
                                      ? AppColors.accent.withOpacity(0.15)
                                      : AppColors.bgCard,
                                  borderRadius: BorderRadius.circular(
                                      AppRadius.card),
                                  border: Border.all(
                                    color: isSelected
                                        ? AppColors.accent
                                        : AppColors.grey7,
                                    width: isSelected ? 1.5 : 1,
                                  ),
                                ),
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      pr.exerciseName,
                                      style: AppTextStyles.label(
                                          AppColors.white),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    const SizedBox(height: 4),
                                    if (pr.weight != null)
                                      Text(
                                        '${pr.weight!.toStringAsFixed(1)} kg',
                                        style: AppTextStyles.headline4(
                                            AppColors.accent),
                                      ),
                                    const SizedBox(height: 4),
                                    const PrBadge(small: true),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(height: 8),
              // Chart
              if (selectedSlug != null)
                sessionsAsync.when(
                  loading: () => const Padding(
                    padding: EdgeInsets.all(20),
                    child: CircularProgressIndicator(
                        color: AppColors.accent),
                  ),
                  error: (_, __) => const SizedBox.shrink(),
                  data: (sessions) => Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Progression',
                          style:
                              AppTextStyles.headline4(AppColors.white),
                        ),
                        const SizedBox(height: 12),
                        PerformanceChart(
                          sessions: sessions,
                          exerciseSlug: selectedSlug,
                        ),
                      ],
                    ),
                  ),
                ),
              // Sessions history
              sessionsAsync.when(
                loading: () => const SizedBox.shrink(),
                error: (_, __) => const SizedBox.shrink(),
                data: (sessions) {
                  if (sessions.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(20),
                      child: Text(l10n.performanceEmpty,
                          style:
                              AppTextStyles.body1(AppColors.grey3)),
                    );
                  }
                  final dateFmt = DateFormat('d MMM yyyy', 'fr_FR');
                  return Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.performanceTitle,
                          style:
                              AppTextStyles.headline4(AppColors.white),
                        ),
                        const SizedBox(height: 12),
                        ...sessions.map(
                          (session) => Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: AppColors.bgCard,
                              borderRadius: BorderRadius.circular(
                                  AppRadius.card),
                              border:
                                  Border.all(color: AppColors.grey7),
                            ),
                            child: Column(
                              crossAxisAlignment:
                                  CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: [
                                    Text(
                                      dateFmt.format(
                                          session.date.toLocal()),
                                      style: AppTextStyles.label(
                                          AppColors.grey3),
                                    ),
                                    if (session.coachFirstName != null)
                                      Text(
                                        session.coachFullName,
                                        style: AppTextStyles.caption(
                                            AppColors.grey3),
                                      ),
                                  ],
                                ),
                                const SizedBox(height: 8),
                                ...session.sets.map(
                                  (s) => Padding(
                                    padding: const EdgeInsets.only(
                                        bottom: 6),
                                    child: Row(
                                      children: [
                                        Expanded(
                                          child: Text(
                                            s.exerciseName,
                                            style: AppTextStyles.body2(
                                                AppColors.white),
                                          ),
                                        ),
                                        if (s.reps != null)
                                          Text(
                                            '${s.reps} reps',
                                            style: AppTextStyles.caption(
                                                AppColors.grey3),
                                          ),
                                        if (s.weight != null) ...[
                                          const SizedBox(width: 8),
                                          Text(
                                            '${s.weight!.toStringAsFixed(1)} kg',
                                            style:
                                                AppTextStyles.caption(
                                                    AppColors.grey3),
                                          ),
                                        ],
                                        if (s.isPr) ...[
                                          const SizedBox(width: 8),
                                          const PrBadge(small: true),
                                        ],
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}
