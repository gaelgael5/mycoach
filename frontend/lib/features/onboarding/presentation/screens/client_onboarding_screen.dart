import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/widgets/gradient_button.dart';
import '../providers/onboarding_providers.dart';
import '../widgets/gym_search_widget.dart';
import '../widgets/onboarding_step_indicator.dart';
import '../widgets/specialty_selector.dart';

/// Wizard d'onboarding client — 4 étapes.
class ClientOnboardingScreen extends ConsumerWidget {
  const ClientOnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(clientOnboardingProvider);
    final l10n = context.l10n;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
              child: Column(
                children: [
                  Text(
                    l10n.onboardingClientTitle,
                    style: AppTextStyles.headline2(AppColors.white),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.onboardingStep(state.step + 1, ClientOnboardingNotifier.totalSteps),
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                  const SizedBox(height: 20),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: OnboardingStepIndicator(
                      currentStep: state.step,
                      totalSteps: ClientOnboardingNotifier.totalSteps,
                    ),
                  ),
                ],
              ),
            ),

            // Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
                child: _stepContent(context, ref, state),
              ),
            ),

            // Error
            if (state.error != null)
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: Text(
                  state.error!,
                  style: AppTextStyles.caption(AppColors.red),
                  textAlign: TextAlign.center,
                ),
              ),

            // Navigation buttons
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
              child: _navigationButtons(context, ref, state),
            ),
          ],
        ),
      ),
    );
  }

  Widget _stepContent(
    BuildContext context,
    WidgetRef ref,
    ClientOnboardingState state,
  ) {
    return switch (state.step) {
      0 => _Step1BasicInfo(state: state),
      1 => _Step2Goals(state: state),
      2 => _Step3Gyms(state: state),
      _ => _Step4Recap(state: state),
    };
  }

  Widget _navigationButtons(
    BuildContext context,
    WidgetRef ref,
    ClientOnboardingState state,
  ) {
    final notifier = ref.read(clientOnboardingProvider.notifier);
    final l10n = context.l10n;
    final isLast = state.step == ClientOnboardingNotifier.totalSteps - 1;
    final isFirst = state.step == 0;
    final isGymStep = state.step == 2;

    return Column(
      children: [
        GradientButton(
          label: isLast ? l10n.onboardingFinish : l10n.onboardingNext,
          isLoading: state.isLoading,
          onPressed: () async {
            if (state.step == 0) {
              final ok = await notifier.saveStep1();
              if (ok && context.mounted) notifier.nextStep();
            } else if (state.step == 2) {
              if (state.selectedGyms.isNotEmpty) {
                await notifier.saveGyms();
              }
              notifier.nextStep();
            } else if (isLast) {
              if (context.mounted) context.go(AppRoutes.clientHome);
            } else {
              notifier.nextStep();
            }
          },
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (!isFirst)
              TextButton(
                onPressed: notifier.previousStep,
                child: Text(l10n.onboardingBack),
              ),
            if (isGymStep) ...[
              if (!isFirst) const SizedBox(width: 16),
              TextButton(
                onPressed: notifier.nextStep,
                child: Text(l10n.onboardingSkip),
              ),
            ],
          ],
        ),
      ],
    );
  }
}

// ── Étape 1 — Infos de base ──────────────────────────────────────────────────

class _Step1BasicInfo extends ConsumerStatefulWidget {
  const _Step1BasicInfo({required this.state});
  final ClientOnboardingState state;

  @override
  ConsumerState<_Step1BasicInfo> createState() => _Step1BasicInfoState();
}

class _Step1BasicInfoState extends ConsumerState<_Step1BasicInfo> {
  late final TextEditingController _firstNameCtrl;
  late final TextEditingController _lastNameCtrl;
  late final TextEditingController _birthYearCtrl;
  String? _gender;

  @override
  void initState() {
    super.initState();
    _firstNameCtrl = TextEditingController(text: widget.state.firstName);
    _lastNameCtrl = TextEditingController(text: widget.state.lastName);
    _birthYearCtrl = TextEditingController(
      text: widget.state.birthYear?.toString() ?? '',
    );
    _gender = widget.state.gender;
  }

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _birthYearCtrl.dispose();
    super.dispose();
  }

  void _sync() {
    ref.read(clientOnboardingProvider.notifier).updateBasicInfo(
          firstName: _firstNameCtrl.text,
          lastName: _lastNameCtrl.text,
          gender: _gender,
          birthYear: int.tryParse(_birthYearCtrl.text),
        );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingClientStep1Title,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingClientSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),

        // Prénom
        TextField(
          controller: _firstNameCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(labelText: l10n.labelFirstName),
          textCapitalization: TextCapitalization.words,
        ),
        const SizedBox(height: 16),

        // Nom
        TextField(
          controller: _lastNameCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(labelText: l10n.labelLastName),
          textCapitalization: TextCapitalization.words,
        ),
        const SizedBox(height: 16),

        // Genre
        Text(l10n.labelGender, style: AppTextStyles.label(AppColors.grey3)),
        const SizedBox(height: 8),
        Row(
          children: [
            _GenderChip(
              label: l10n.genderMale,
              value: 'male',
              selected: _gender == 'male',
              onTap: () => setState(() { _gender = 'male'; _sync(); }),
            ),
            const SizedBox(width: 8),
            _GenderChip(
              label: l10n.genderFemale,
              value: 'female',
              selected: _gender == 'female',
              onTap: () => setState(() { _gender = 'female'; _sync(); }),
            ),
            const SizedBox(width: 8),
            _GenderChip(
              label: l10n.genderOther,
              value: 'other',
              selected: _gender == 'other',
              onTap: () => setState(() { _gender = 'other'; _sync(); }),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Année de naissance
        TextField(
          controller: _birthYearCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(labelText: l10n.labelBirthYear),
          keyboardType: TextInputType.number,
        ),
      ],
    );
  }
}

class _GenderChip extends StatelessWidget {
  const _GenderChip({
    required this.label,
    required this.value,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final String value;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? AppColors.accentGlow : AppColors.bgInput,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          border: Border.all(
            color: selected ? AppColors.accent : AppColors.grey7,
            width: 1.5,
          ),
        ),
        child: Text(
          label,
          style: AppTextStyles.label(selected ? AppColors.accent : AppColors.grey3),
        ),
      ),
    );
  }
}

// ── Étape 2 — Objectifs ──────────────────────────────────────────────────────

class _Step2Goals extends ConsumerWidget {
  const _Step2Goals({required this.state});
  final ClientOnboardingState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final notifier = ref.read(clientOnboardingProvider.notifier);

    final goalLabels = {
      'weight_loss': l10n.onboardingGoalWeightLoss,
      'muscle_gain': l10n.onboardingGoalMuscleGain,
      'endurance': l10n.onboardingGoalEndurance,
      'flexibility': l10n.onboardingGoalFlexibility,
      'wellness': l10n.onboardingGoalWellness,
      'sport_competition': l10n.onboardingGoalSportCompetition,
      'rehabilitation': l10n.onboardingGoalRehabilitation,
      'other': l10n.onboardingGoalOther,
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingGoals,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingGoalsSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),
        GoalSelector(
          selectedGoals: state.selectedGoals,
          goalLabels: goalLabels,
          onToggle: notifier.toggleGoal,
        ),
      ],
    );
  }
}

// ── Étape 3 — Salles favorites ───────────────────────────────────────────────

class _Step3Gyms extends ConsumerWidget {
  const _Step3Gyms({required this.state});
  final ClientOnboardingState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final notifier = ref.read(clientOnboardingProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingGyms,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingGymsSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),
        GymSearchWidget(
          selectedGyms: state.selectedGyms,
          onToggle: notifier.toggleGym,
        ),
      ],
    );
  }
}

// ── Étape 4 — Récapitulatif ──────────────────────────────────────────────────

class _Step4Recap extends ConsumerWidget {
  const _Step4Recap({required this.state});
  final ClientOnboardingState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingRecapTitle,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingRecapSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),

        // Infos personnelles
        _RecapCard(
          title: l10n.onboardingRecapPersonalInfo,
          items: [
            if (state.firstName.isNotEmpty || state.lastName.isNotEmpty)
              '${state.firstName} ${state.lastName}'.trim(),
            if (state.gender != null) state.gender!,
            if (state.birthYear != null) state.birthYear.toString(),
          ],
        ),

        const SizedBox(height: 12),

        // Objectifs
        if (state.selectedGoals.isNotEmpty)
          _RecapCard(
            title: l10n.onboardingGoals,
            items: state.selectedGoals,
          ),

        const SizedBox(height: 12),

        // Salles
        if (state.selectedGyms.isNotEmpty)
          _RecapCard(
            title: l10n.onboardingGyms,
            items: state.selectedGyms.map((g) => g.name).toList(),
          ),
      ],
    );
  }
}

class _RecapCard extends StatelessWidget {
  const _RecapCard({required this.title, required this.items});
  final String title;
  final List<String> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: AppTextStyles.label(AppColors.grey3)),
          const SizedBox(height: 8),
          ...items.map(
            (item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  const Icon(Icons.check, size: 14, color: AppColors.green),
                  const SizedBox(width: 8),
                  Text(item, style: AppTextStyles.body1(AppColors.white)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
