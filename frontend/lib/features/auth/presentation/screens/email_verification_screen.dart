import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';
import '../widgets/auth_form_widgets.dart';
import '../widgets/gradient_button.dart';

/// Écran de vérification email.
/// Permet de renvoyer le lien de vérification.
class EmailVerificationScreen extends ConsumerStatefulWidget {
  const EmailVerificationScreen({super.key});

  @override
  ConsumerState<EmailVerificationScreen> createState() =>
      _EmailVerificationScreenState();
}

class _EmailVerificationScreenState
    extends ConsumerState<EmailVerificationScreen> {
  bool _isResending = false;
  bool _resentSuccess = false;
  String? _errorMessage;

  String get _email {
    final user = ref.read(authStateProvider).valueOrNull;
    return user?.email ?? '';
  }

  Future<void> _resend() async {
    setState(() {
      _isResending = true;
      _resentSuccess = false;
      _errorMessage = null;
    });
    try {
      await ref.read(authServiceProvider).requestEmailVerification();
      if (mounted) setState(() => _resentSuccess = true);
    } catch (_) {
      if (mounted) setState(() => _errorMessage = context.l10n.errorGeneric);
    } finally {
      if (mounted) setState(() => _isResending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),

              // Icon
              Center(
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppColors.accent.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.mark_email_unread_outlined,
                    color: AppColors.accent,
                    size: 40,
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Title
              Text(
                context.l10n.emailVerifTitle,
                style: AppTextStyles.headline2(AppColors.white),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),
              if (_email.isNotEmpty)
                Text(
                  context.l10n.emailVerifSubtitle(_email),
                  style: AppTextStyles.body1(AppColors.grey3),
                  textAlign: TextAlign.center,
                ),
              const SizedBox(height: 48),

              // Success feedback
              if (_resentSuccess) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.green.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(AppRadius.input),
                    border: Border.all(color: AppColors.green.withOpacity(0.4)),
                  ),
                  child: Text(
                    context.l10n.emailVerifResendSuccess,
                    style: AppTextStyles.body2(AppColors.green),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Error
              if (_errorMessage != null) ...[
                AuthErrorBanner(message: _errorMessage!),
                const SizedBox(height: 16),
              ],

              // Resend button
              GradientButton(
                label: context.l10n.emailVerifResend,
                onPressed: _isResending ? null : _resend,
                isLoading: _isResending,
              ),
              const SizedBox(height: 16),

              // Wrong email link
              TextButton(
                onPressed: () => context.go(AppRoutes.registerRole),
                child: Text(
                  context.l10n.emailVerifWrongEmail,
                  textAlign: TextAlign.center,
                ),
              ),

              const Spacer(),
            ],
          ),
        ),
      ),
    );
  }
}
