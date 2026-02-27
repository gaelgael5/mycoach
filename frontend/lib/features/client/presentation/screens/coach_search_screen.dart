import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../providers/coach_search_providers.dart';
import '../widgets/coach_card.dart';

class CoachSearchScreen extends ConsumerWidget {
  const CoachSearchScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final params = ref.watch(coachSearchParamsProvider);
    final results = ref.watch(coachSearchResultsProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.coachSearchTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: TextField(
              style: AppTextStyles.body1(AppColors.white),
              decoration: InputDecoration(
                hintText: l10n.coachSearchHint,
                prefixIcon: const Icon(Icons.search, color: AppColors.grey3),
                suffixIcon: params.query.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear,
                            color: AppColors.grey3),
                        onPressed: () {
                          ref
                              .read(coachSearchParamsProvider.notifier)
                              .state = params.copyWith(query: '');
                        },
                      )
                    : null,
              ),
              onChanged: (v) {
                ref.read(coachSearchParamsProvider.notifier).state =
                    params.copyWith(query: v);
              },
            ),
          ),
          // Filter chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                _FilterChip(
                  label: l10n.coachDiscoveryBadge,
                  selected: params.discoveryOnly,
                  onSelected: (v) {
                    ref
                        .read(coachSearchParamsProvider.notifier)
                        .state = params.copyWith(discoveryOnly: v);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          // Results
          Expanded(
            child: results.when(
              data: (coaches) {
                if (coaches.isEmpty) {
                  return Center(
                    child: Text(
                      l10n.coachSearchTitle,
                      style: AppTextStyles.body1(AppColors.grey3),
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () =>
                      ref.refresh(coachSearchResultsProvider.future),
                  child: ListView.builder(
                    itemCount: coaches.length,
                    itemBuilder: (ctx, i) => CoachCard(
                      coach: coaches[i],
                      onTap: () => context
                          .go('${AppRoutes.coachSearch}/${coaches[i].id}'),
                    ),
                  ),
                );
              },
              loading: () => const Center(
                  child: CircularProgressIndicator(
                      color: AppColors.accent)),
              error: (e, _) => Center(
                child: Text(
                  context.l10n.errorGeneric,
                  style: AppTextStyles.body1(AppColors.red),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onSelected,
  });
  final String label;
  final bool selected;
  final ValueChanged<bool> onSelected;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: selected,
        onSelected: onSelected,
        selectedColor: AppColors.accent.withOpacity(0.2),
        checkmarkColor: AppColors.accent,
        backgroundColor: AppColors.bgInput,
        labelStyle: AppTextStyles.caption(
            selected ? AppColors.accent : AppColors.grey3),
        side: BorderSide(
            color: selected ? AppColors.accent : AppColors.grey7),
      ),
    );
  }
}
