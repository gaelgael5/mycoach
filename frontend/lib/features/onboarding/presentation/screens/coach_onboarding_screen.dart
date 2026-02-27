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

/// Wizard d'onboarding coach — 5 étapes.
class CoachOnboardingScreen extends ConsumerWidget {
  const CoachOnboardingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(coachOnboardingProvider);
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
                    l10n.onboardingCoachTitle,
                    style: AppTextStyles.headline2(AppColors.white),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    l10n.onboardingStep(state.step + 1, CoachOnboardingNotifier.totalSteps),
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                  const SizedBox(height: 20),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: OnboardingStepIndicator(
                      currentStep: state.step,
                      totalSteps: CoachOnboardingNotifier.totalSteps,
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

            // Navigation
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
    CoachOnboardingState state,
  ) {
    return switch (state.step) {
      0 => _Step1BioCityPhoto(state: state),
      1 => _Step2Specialties(state: state),
      2 => _Step3Pricing(state: state),
      3 => _Step4Gyms(state: state),
      _ => _Step5Recap(state: state),
    };
  }

  Widget _navigationButtons(
    BuildContext context,
    WidgetRef ref,
    CoachOnboardingState state,
  ) {
    final notifier = ref.read(coachOnboardingProvider.notifier);
    final l10n = context.l10n;
    final isLast = state.step == CoachOnboardingNotifier.totalSteps - 1;
    final isFirst = state.step == 0;
    final isGymStep = state.step == 3;
    final isSpecialtyStep = state.step == 1;
    final canProceed = isSpecialtyStep ? state.canProceedFromStep2 : true;

    return Column(
      children: [
        GradientButton(
          label: isLast ? l10n.onboardingPublish : l10n.onboardingNext,
          isLoading: state.isLoading,
          onPressed: canProceed
              ? () async {
                  if (isLast) {
                    final ok = await notifier.publishProfile();
                    if (ok && context.mounted) context.go(AppRoutes.coachHome);
                  } else {
                    notifier.nextStep();
                  }
                }
              : null,
        ),
        if (isSpecialtyStep && !canProceed)
          Padding(
            padding: const EdgeInsets.only(top: 8),
            child: Text(
              l10n.onboardingSpecialtyRequired,
              style: AppTextStyles.caption(AppColors.red),
            ),
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

// ── Étape 1 — Photo + Bio + Ville ────────────────────────────────────────────

class _Step1BioCityPhoto extends ConsumerStatefulWidget {
  const _Step1BioCityPhoto({required this.state});
  final CoachOnboardingState state;

  @override
  ConsumerState<_Step1BioCityPhoto> createState() => _Step1BioCityPhotoState();
}

class _Step1BioCityPhotoState extends ConsumerState<_Step1BioCityPhoto> {
  late final TextEditingController _bioCtrl;
  late final TextEditingController _cityCtrl;

  @override
  void initState() {
    super.initState();
    _bioCtrl = TextEditingController(text: widget.state.bio);
    _cityCtrl = TextEditingController(text: widget.state.city);
  }

  @override
  void dispose() {
    _bioCtrl.dispose();
    _cityCtrl.dispose();
    super.dispose();
  }

  void _sync() {
    ref.read(coachOnboardingProvider.notifier).updateBioCity(
          bio: _bioCtrl.text,
          city: _cityCtrl.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingBio,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingBioStepSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),

        // Bio
        TextField(
          controller: _bioCtrl,
          onChanged: (_) => _sync(),
          maxLines: 4,
          maxLength: 500,
          decoration: InputDecoration(
            labelText: l10n.onboardingBio,
            hintText: l10n.onboardingBioHint,
            alignLabelWithHint: true,
          ),
        ),
        const SizedBox(height: 16),

        // Ville
        TextField(
          controller: _cityCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(labelText: l10n.onboardingCity),
          textCapitalization: TextCapitalization.words,
        ),
      ],
    );
  }
}

// ── Étape 2 — Spécialités ────────────────────────────────────────────────────

class _Step2Specialties extends ConsumerWidget {
  const _Step2Specialties({required this.state});
  final CoachOnboardingState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final notifier = ref.read(coachOnboardingProvider.notifier);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingSpecialties,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 4),
        Text(
          l10n.onboardingSpecialtiesSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),
        SpecialtySelector(
          selectedSpecialties: state.selectedSpecialties,
          onToggle: notifier.toggleSpecialty,
        ),
      ],
    );
  }
}

// ── Étape 3 — Tarifs & Expérience ────────────────────────────────────────────

class _Step3Pricing extends ConsumerStatefulWidget {
  const _Step3Pricing({required this.state});
  final CoachOnboardingState state;

  @override
  ConsumerState<_Step3Pricing> createState() => _Step3PricingState();
}

class _Step3PricingState extends ConsumerState<_Step3Pricing> {
  late final TextEditingController _rateCtrl;
  late final TextEditingController _maxClientsCtrl;
  late double _experienceSlider;
  late bool _offersDiscovery;

  @override
  void initState() {
    super.initState();
    _rateCtrl = TextEditingController(
      text: widget.state.hourlyRateEuros > 0
          ? widget.state.hourlyRateEuros.toString()
          : '',
    );
    _maxClientsCtrl = TextEditingController(
      text: widget.state.maxClients?.toString() ?? '',
    );
    _experienceSlider = widget.state.experienceYears.toDouble();
    _offersDiscovery = widget.state.offersDiscovery;
  }

  @override
  void dispose() {
    _rateCtrl.dispose();
    _maxClientsCtrl.dispose();
    super.dispose();
  }

  void _sync() {
    ref.read(coachOnboardingProvider.notifier).updatePricing(
          hourlyRateEuros: int.tryParse(_rateCtrl.text) ?? 0,
          experienceYears: _experienceSlider.round(),
          offersDiscovery: _offersDiscovery,
          maxClients: int.tryParse(_maxClientsCtrl.text),
        );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.onboardingPricingTitle,
          style: AppTextStyles.headline3(AppColors.white),
        ),
        const SizedBox(height: 24),

        // Tarif horaire
        TextField(
          controller: _rateCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(
            labelText: l10n.onboardingHourlyRate,
            prefixIcon: const Padding(
              padding: EdgeInsets.only(left: 12, right: 4),
              child: Text('€', style: TextStyle(color: AppColors.grey3, fontSize: 16)),
            ),
            prefixIconConstraints: const BoxConstraints(minWidth: 0, minHeight: 0),
          ),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 24),

        // Années d'expérience
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              l10n.onboardingExperience,
              style: AppTextStyles.label(AppColors.grey3),
            ),
            Text(
              '${_experienceSlider.round()} ans',
              style: AppTextStyles.body1(AppColors.accent),
            ),
          ],
        ),
        Slider(
          value: _experienceSlider,
          min: 0,
          max: 40,
          divisions: 40,
          activeColor: AppColors.accent,
          inactiveColor: AppColors.grey7,
          onChanged: (v) {
            setState(() { _experienceSlider = v; });
            _sync();
          },
        ),
        const SizedBox(height: 16),

        // Max clients
        TextField(
          controller: _maxClientsCtrl,
          onChanged: (_) => _sync(),
          decoration: InputDecoration(
            labelText: '${l10n.onboardingMaxClients} (${l10n.labelOptional})',
          ),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 24),

        // Séance découverte
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(AppRadius.card),
            border: Border.all(color: AppColors.grey7, width: 1),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.onboardingDiscovery,
                      style: AppTextStyles.body1(AppColors.white),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      l10n.onboardingDiscoveryHint,
                      style: AppTextStyles.caption(AppColors.grey5),
                    ),
                  ],
                ),
              ),
              Switch(
                value: _offersDiscovery,
                onChanged: (v) {
                  setState(() { _offersDiscovery = v; });
                  _sync();
                },
                activeColor: AppColors.accent,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Étape 4 — Salles ────────────────────────────────────────────────────────

class _Step4Gyms extends ConsumerWidget {
  const _Step4Gyms({required this.state});
  final CoachOnboardingState state;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final notifier = ref.read(coachOnboardingProvider.notifier);

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

// ── Étape 5 — Récapitulatif & Publication ────────────────────────────────────

class _Step5Recap extends ConsumerWidget {
  const _Step5Recap({required this.state});
  final CoachOnboardingState state;

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
          l10n.onboardingCoachRecapSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
        ),
        const SizedBox(height: 24),

        // Bio
        if (state.bio.isNotEmpty)
          _CoachRecapCard(
            title: l10n.onboardingBio,
            content: state.bio,
          ),
        const SizedBox(height: 12),

        // Ville
        if (state.city.isNotEmpty)
          _CoachRecapCard(
            title: l10n.onboardingCity,
            content: state.city,
          ),
        const SizedBox(height: 12),

        // Spécialités
        if (state.selectedSpecialties.isNotEmpty)
          _CoachRecapCard(
            title: l10n.onboardingSpecialties,
            content: state.selectedSpecialties.join(', '),
          ),
        const SizedBox(height: 12),

        // Tarif
        if (state.hourlyRateEuros > 0)
          _CoachRecapCard(
            title: l10n.onboardingHourlyRate,
            content: '${state.hourlyRateEuros}€/h',
          ),
        const SizedBox(height: 12),

        // Expérience
        _CoachRecapCard(
          title: l10n.onboardingExperience,
          content: '${state.experienceYears} ans',
        ),
        const SizedBox(height: 12),

        // Séance découverte
        _CoachRecapCard(
          title: l10n.onboardingDiscovery,
          content: state.offersDiscovery ? '✓' : '✗',
        ),
        const SizedBox(height: 12),

        // Salles
        if (state.selectedGyms.isNotEmpty)
          _CoachRecapCard(
            title: l10n.onboardingGyms,
            content: state.selectedGyms.map((g) => g.name).join(', '),
          ),
      ],
    );
  }
}

class _CoachRecapCard extends StatelessWidget {
  const _CoachRecapCard({required this.title, required this.content});
  final String title;
  final String content;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
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
          const SizedBox(height: 6),
          Text(content, style: AppTextStyles.body1(AppColors.white)),
        ],
      ),
    );
  }
}
