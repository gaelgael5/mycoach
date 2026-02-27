import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/providers/auth_providers.dart';
import '../../../../features/auth/presentation/widgets/gradient_button.dart';
import '../providers/onboarding_providers.dart';

/// Écran d'enrollment via deep link.
/// Route : /enroll/:token
class EnrollmentLinkScreen extends ConsumerStatefulWidget {
  const EnrollmentLinkScreen({super.key, required this.token});

  final String token;

  @override
  ConsumerState<EnrollmentLinkScreen> createState() => _EnrollmentLinkScreenState();
}

class _EnrollmentLinkScreenState extends ConsumerState<EnrollmentLinkScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(enrollmentProvider.notifier).loadToken(widget.token);
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(enrollmentProvider);
    final authState = ref.watch(authStateProvider);
    final l10n = context.l10n;
    final isLoggedIn = authState.valueOrNull != null;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.enrollmentTitle),
        leading: BackButton(
          onPressed: () {
            if (context.canPop()) {
              context.pop();
            } else {
              context.go(AppRoutes.login);
            }
          },
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: state.isLoading
              ? const Center(
                  child: CircularProgressIndicator(color: AppColors.accent),
                )
              : state.error != null
                  ? _ErrorView(
                      message: l10n.enrollmentInvalidToken,
                      onBack: () => context.go(AppRoutes.login),
                    )
                  : state.coachData == null
                      ? const SizedBox.shrink()
                      : _CoachInviteCard(
                          coachData: state.coachData!,
                          token: widget.token,
                          isLoggedIn: isLoggedIn,
                          isEnrolling: state.isEnrolling,
                          enrolled: state.enrolled,
                        ),
        ),
      ),
    );
  }
}

class _CoachInviteCard extends ConsumerWidget {
  const _CoachInviteCard({
    required this.coachData,
    required this.token,
    required this.isLoggedIn,
    required this.isEnrolling,
    required this.enrolled,
  });

  final Map<String, dynamic> coachData;
  final String token;
  final bool isLoggedIn;
  final bool isEnrolling;
  final bool enrolled;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final coach = coachData['coach'] as Map<String, dynamic>? ?? {};
    final firstName = coach['first_name'] as String? ?? '';
    final lastName = coach['last_name'] as String? ?? '';
    final avatarUrl = coach['resolved_avatar_url'] as String?;
    final specialties = (coach['specialties'] as List<dynamic>?)
        ?.map((e) => e.toString())
        .toList() ?? [];
    final coachName = '$firstName $lastName'.trim();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const SizedBox(height: 24),

        // Sous-titre
        Text(
          l10n.enrollmentSubtitle,
          style: AppTextStyles.body2(AppColors.grey3),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 24),

        // Avatar coach
        _CoachAvatar(avatarUrl: avatarUrl, name: coachName),
        const SizedBox(height: 16),

        // Nom coach
        Text(
          coachName,
          style: AppTextStyles.headline3(AppColors.white),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),

        // Spécialités
        if (specialties.isNotEmpty) ...[
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: specialties
                .map(
                  (s) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.accentGlow,
                      borderRadius: BorderRadius.circular(AppRadius.pill),
                      border: Border.all(color: AppColors.accent, width: 1),
                    ),
                    child: Text(s, style: AppTextStyles.caption(AppColors.accent)),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 32),
        ],

        // Enrolled confirmation
        if (enrolled)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.greenSurface,
              borderRadius: BorderRadius.circular(AppRadius.card),
              border: Border.all(color: AppColors.green, width: 1),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.check_circle, color: AppColors.green),
                const SizedBox(width: 8),
                Text(
                  l10n.enrollmentSuccess,
                  style: AppTextStyles.body1(AppColors.green),
                ),
              ],
            ),
          )
        else if (isLoggedIn)
          // Utilisateur connecté → rejoindre directement
          GradientButton(
            label: l10n.enrollmentJoin,
            isLoading: isEnrolling,
            onPressed: () async {
              final ok = await ref.read(enrollmentProvider.notifier).enroll(token);
              if (ok && context.mounted) {
                context.go(AppRoutes.clientHome);
              }
            },
          )
        else
          // Non connecté → inscription avec token pré-rempli
          Column(
            children: [
              GradientButton(
                label: l10n.enrollmentJoin,
                onPressed: () {
                  context.go(
                    '${AppRoutes.registerClient}?enrollment_token=$token',
                  );
                },
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () {
                  context.go('${AppRoutes.login}?enrollment_token=$token');
                },
                child: Text(l10n.loginButton),
              ),
            ],
          ),
      ],
    );
  }
}

class _CoachAvatar extends StatelessWidget {
  const _CoachAvatar({required this.avatarUrl, required this.name});

  final String? avatarUrl;
  final String name;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.accent, width: 2),
      ),
      clipBehavior: Clip.antiAlias,
      child: avatarUrl != null
          ? Image.network(
              avatarUrl!,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => _initials(name),
            )
          : _initials(name),
    );
  }

  Widget _initials(String name) {
    final parts = name.trim().split(' ');
    final initials = parts.length >= 2
        ? '${parts[0][0]}${parts[1][0]}'.toUpperCase()
        : name.isNotEmpty
            ? name[0].toUpperCase()
            : '?';
    return Center(
      child: Text(
        initials,
        style: AppTextStyles.headline2(AppColors.white),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onBack});

  final String message;
  final VoidCallback onBack;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.link_off, size: 64, color: AppColors.grey5),
          const SizedBox(height: 24),
          Text(
            message,
            style: AppTextStyles.body1(AppColors.grey3),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          ElevatedButton(
            onPressed: onBack,
            child: Text(l10n.onboardingBack),
          ),
        ],
      ),
    );
  }
}
