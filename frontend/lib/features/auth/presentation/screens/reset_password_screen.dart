import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/api/api_exception.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';
import '../widgets/auth_form_widgets.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';

/// Écran de réinitialisation du mot de passe.
/// Reçoit le [token] en paramètre de route (/reset-password?token=xxx).
class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({super.key, this.token});

  final String? token;

  @override
  ConsumerState<ResetPasswordScreen> createState() =>
      _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();

  bool _isLoading = false;
  bool _success = false;
  String? _errorMessage;

  @override
  void dispose() {
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final token = widget.token;
    if (token == null || token.isEmpty) {
      setState(() => _errorMessage = context.l10n.resetPasswordLinkExpired);
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authServiceProvider).resetPassword(
            token: token,
            newPassword: _passwordCtrl.text,
          );
      if (mounted) setState(() => _success = true);
    } catch (e) {
      if (mounted) {
        final code = extractApiErrorCode(e);
        setState(() {
          _errorMessage = switch (code) {
            ApiErrorCode.unknown => context.l10n.resetPasswordLinkExpired,
            _ => context.l10n.errorGeneric,
          };
        });
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.grey1),
          onPressed: () => context.go(AppRoutes.login),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: _success ? _buildSuccess(context) : _buildForm(context),
        ),
      ),
    );
  }

  Widget _buildForm(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 16),
          Center(
            child: Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: AppColors.accent.withOpacity(0.12),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.lock_outline,
                color: AppColors.accent,
                size: 36,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            context.l10n.resetPasswordTitle,
            style: AppTextStyles.headline2(AppColors.white),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          AuthTextField(
            label: context.l10n.labelPassword,
            controller: _passwordCtrl,
            isPassword: true,
            textInputAction: TextInputAction.next,
            autofillHints: const [AutofillHints.newPassword],
            validator: (v) {
              if (v == null || v.isEmpty) return context.l10n.validationRequired;
              if (v.length < 8 ||
                  !v.contains(RegExp(r'[A-Z]')) ||
                  !v.contains(RegExp(r'[0-9]'))) {
                return context.l10n.registerPasswordWeak;
              }
              return null;
            },
          ),
          const SizedBox(height: 16),
          AuthTextField(
            label: context.l10n.labelPasswordConfirm,
            controller: _confirmCtrl,
            isPassword: true,
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _submit(),
            validator: (v) {
              if (v != _passwordCtrl.text) {
                return context.l10n.registerPasswordMismatch;
              }
              return null;
            },
          ),
          const SizedBox(height: 24),
          if (_errorMessage != null) ...[
            AuthErrorBanner(message: _errorMessage!),
            const SizedBox(height: 16),
          ],
          GradientButton(
            label: context.l10n.resetPasswordButton,
            onPressed: _isLoading ? null : _submit,
            isLoading: _isLoading,
          ),
        ],
      ),
    );
  }

  Widget _buildSuccess(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 48),
        Center(
          child: Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.green.withOpacity(0.12),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check_circle_outline,
              color: AppColors.green,
              size: 44,
            ),
          ),
        ),
        const SizedBox(height: 24),
        Text(
          context.l10n.resetPasswordSuccess,
          style: AppTextStyles.headline3(AppColors.white),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 40),
        GradientButton(
          label: context.l10n.loginButton,
          onPressed: () => context.go(AppRoutes.login),
        ),
      ],
    );
  }
}
