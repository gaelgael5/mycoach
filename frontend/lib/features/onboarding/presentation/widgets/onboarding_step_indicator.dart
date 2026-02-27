import 'package:flutter/material.dart';
import '../../../../core/theme/app_theme.dart';

/// Indicateur de progression du wizard onboarding.
/// - Étape passée : cercle vert avec checkmark
/// - Étape active : cercle orange accent rempli
/// - Étape future : cercle gris
class OnboardingStepIndicator extends StatelessWidget {
  const OnboardingStepIndicator({
    super.key,
    required this.currentStep,
    required this.totalSteps,
  });

  final int currentStep; // 0-based
  final int totalSteps;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(totalSteps * 2 - 1, (index) {
        if (index.isOdd) {
          // Ligne entre les cercles
          final stepIndex = index ~/ 2;
          final isDone = stepIndex < currentStep;
          return Expanded(
            child: Container(
              height: 2,
              color: isDone ? AppColors.green : AppColors.grey7,
            ),
          );
        }
        final stepIndex = index ~/ 2;
        return _StepCircle(
          stepNumber: stepIndex + 1,
          state: stepIndex < currentStep
              ? _StepState.done
              : stepIndex == currentStep
                  ? _StepState.active
                  : _StepState.upcoming,
        );
      }),
    );
  }
}

enum _StepState { done, active, upcoming }

class _StepCircle extends StatelessWidget {
  const _StepCircle({
    required this.stepNumber,
    required this.state,
  });

  final int stepNumber;
  final _StepState state;

  @override
  Widget build(BuildContext context) {
    final (bgColor, borderColor, child) = switch (state) {
      _StepState.done => (
          AppColors.greenSurface,
          AppColors.green,
          const Icon(Icons.check, size: 14, color: AppColors.green),
        ),
      _StepState.active => (
          AppColors.accent,
          AppColors.accent,
          Text(
            '$stepNumber',
            style: AppTextStyles.label(AppColors.white),
          ),
        ),
      _StepState.upcoming => (
          AppColors.bgInput,
          AppColors.grey7,
          Text(
            '$stepNumber',
            style: AppTextStyles.label(AppColors.grey5),
          ),
        ),
    };

    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: bgColor,
        shape: BoxShape.circle,
        border: Border.all(color: borderColor, width: 1.5),
      ),
      child: Center(child: child),
    );
  }
}
