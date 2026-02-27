import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/gym.dart';
import '../providers/onboarding_providers.dart';

/// Widget de recherche et sélection de salles de sport.
///
/// [selectedGyms] : salles déjà sélectionnées
/// [onToggle]     : callback pour ajouter/retirer une salle
/// [maxGyms]      : maximum de salles sélectionnables (défaut 5)
class GymSearchWidget extends ConsumerStatefulWidget {
  const GymSearchWidget({
    super.key,
    required this.selectedGyms,
    required this.onToggle,
    this.maxGyms = 5,
  });

  final List<Gym> selectedGyms;
  final void Function(Gym) onToggle;
  final int maxGyms;

  @override
  ConsumerState<GymSearchWidget> createState() => _GymSearchWidgetState();
}

class _GymSearchWidgetState extends ConsumerState<GymSearchWidget> {
  final _searchController = TextEditingController();
  final _debounce = ValueNotifier<String>('');

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      _debounce.value = _searchController.text;
    });
    _debounce.addListener(_onQueryChanged);
  }

  void _onQueryChanged() {
    final q = _debounce.value.trim();
    if (q.length >= 2) {
      ref.read(gymSearchProvider.notifier).search(q);
    } else if (q.isEmpty) {
      ref.read(gymSearchProvider.notifier).clear();
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    _debounce.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final searchState = ref.watch(gymSearchProvider);
    final l10n = context.l10n;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Barre de recherche
        TextField(
          controller: _searchController,
          decoration: InputDecoration(
            hintText: l10n.onboardingGymSearch,
            prefixIcon: const Icon(Icons.search, color: AppColors.grey5),
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear, color: AppColors.grey5),
                    onPressed: () {
                      _searchController.clear();
                      ref.read(gymSearchProvider.notifier).clear();
                    },
                  )
                : null,
          ),
        ),

        // Salles sélectionnées
        if (widget.selectedGyms.isNotEmpty) ...[
          const SizedBox(height: 16),
          Text(
            '${widget.selectedGyms.length}/${widget.maxGyms}',
            style: AppTextStyles.caption(AppColors.grey3),
          ),
          const SizedBox(height: 8),
          ...widget.selectedGyms.map(
            (gym) => _GymTile(
              gym: gym,
              isSelected: true,
              onTap: () => widget.onToggle(gym),
              actionLabel: l10n.onboardingGymRemove,
            ),
          ),
        ],

        const SizedBox(height: 12),

        // Résultats de recherche
        if (searchState.isLoading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(24),
              child: CircularProgressIndicator(color: AppColors.accent),
            ),
          )
        else if (searchState.results.isNotEmpty) ...[
          ...searchState.results
              .where((g) => !widget.selectedGyms.any((s) => s.id == g.id))
              .map(
                (gym) => _GymTile(
                  gym: gym,
                  isSelected: false,
                  onTap: widget.selectedGyms.length < widget.maxGyms
                      ? () => widget.onToggle(gym)
                      : null,
                  actionLabel: l10n.onboardingGymAdd,
                ),
              ),
        ] else if (searchState.query.isNotEmpty && !searchState.isLoading)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 24),
            child: Center(
              child: Text(
                'Aucun résultat',
                style: AppTextStyles.body2(AppColors.grey5),
              ),
            ),
          ),
      ],
    );
  }
}

class _GymTile extends StatelessWidget {
  const _GymTile({
    required this.gym,
    required this.isSelected,
    required this.actionLabel,
    this.onTap,
  });

  final Gym gym;
  final bool isSelected;
  final String actionLabel;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: isSelected ? AppColors.accentGlow : AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(
          color: isSelected ? AppColors.accent : AppColors.grey7,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          // Icône
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.bgInput,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.fitness_center, size: 18, color: AppColors.grey3),
          ),
          const SizedBox(width: 12),
          // Infos
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  gym.name,
                  style: AppTextStyles.body1(AppColors.white),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                if (gym.city.isNotEmpty)
                  Text(
                    gym.city,
                    style: AppTextStyles.caption(AppColors.grey5),
                  ),
              ],
            ),
          ),
          // Bouton action
          if (onTap != null)
            GestureDetector(
              onTap: onTap,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.red.withOpacity(0.15) : AppColors.accentGlow,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                  border: Border.all(
                    color: isSelected ? AppColors.red : AppColors.accent,
                    width: 1,
                  ),
                ),
                child: Text(
                  actionLabel,
                  style: AppTextStyles.caption(
                    isSelected ? AppColors.red : AppColors.accent,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
