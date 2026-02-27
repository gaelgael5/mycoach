import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

/// Liste des spécialités disponibles pour les coachs.
const kCoachSpecialties = [
  'Musculation',
  'Cardio',
  'Yoga',
  'Pilates',
  'CrossFit',
  'Natation',
  'Running',
  'Boxe',
  'Arts martiaux',
  'Nutrition',
  'Rééducation',
  'Stretching',
  'HIIT',
  'Cyclisme',
  'Danse',
  'Escalade',
  'Surf',
  'Ski',
  'Tennis',
  'Golf',
];

/// Sélecteur de spécialités par chips multi-sélection.
class SpecialtySelector extends StatelessWidget {
  const SpecialtySelector({
    super.key,
    required this.selectedSpecialties,
    required this.onToggle,
    this.specialties = kCoachSpecialties,
  });

  final List<String> selectedSpecialties;
  final void Function(String) onToggle;
  final List<String> specialties;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: specialties.map((specialty) {
        final isSelected = selectedSpecialties.contains(specialty);
        return _SpecialtyChip(
          label: specialty,
          isSelected: isSelected,
          onTap: () => onToggle(specialty),
        );
      }).toList(),
    );
  }
}

class _SpecialtyChip extends StatelessWidget {
  const _SpecialtyChip({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.accentGlow : AppColors.bgInput,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          border: Border.all(
            color: isSelected ? AppColors.accent : AppColors.grey7,
            width: 1.5,
          ),
        ),
        child: Text(
          label,
          style: AppTextStyles.label(
            isSelected ? AppColors.accent : AppColors.grey3,
          ),
        ),
      ),
    );
  }
}

// ── Sélecteur d'objectifs client ────────────────────────────────────────────

const kClientGoals = [
  'weight_loss',
  'muscle_gain',
  'endurance',
  'flexibility',
  'wellness',
  'sport_competition',
  'rehabilitation',
  'other',
];

/// Sélecteur d'objectifs client par chips multi-sélection.
/// [goalLabels] : map goal_key → label affiché.
class GoalSelector extends StatelessWidget {
  const GoalSelector({
    super.key,
    required this.selectedGoals,
    required this.goalLabels,
    required this.onToggle,
  });

  final List<String> selectedGoals;
  final Map<String, String> goalLabels;
  final void Function(String) onToggle;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: kClientGoals.map((goal) {
        final isSelected = selectedGoals.contains(goal);
        final label = goalLabels[goal] ?? goal;
        return _SpecialtyChip(
          label: label,
          isSelected: isSelected,
          onTap: () => onToggle(goal),
        );
      }).toList(),
    );
  }
}
