import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';
import '../widgets/auth_form_widgets.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';

/// Écran "Mot de passe oublié".
class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() =>
      _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();

  bool _isLoading = false;
  bool _sent = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref
          .read(authServiceProvider)
          .forgotPassword(_emailCtrl.text.trim());
    } catch (_) {
      // Le backend retourne 204 même si l'email n'existe pas (sécurité)
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _sent = true; // Toujours afficher le succès
        });
      }
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
          child: _sent ? _buildSuccess(context) : _buildForm(context),
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
                Icons.lock_reset,
                color: AppColors.accent,
                size: 36,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            context.l10n.forgotPasswordTitle,
            style: AppTextStyles.headline2(AppColors.white),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            context.l10n.forgotPasswordSubtitle,
            style: AppTextStyles.body1(AppColors.grey3),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          AuthTextField(
            label: context.l10n.labelEmail,
            hint: 'email@exemple.com',
            controller: _emailCtrl,
            keyboardType: TextInputType.emailAddress,
            textInputAction: TextInputAction.done,
            autofillHints: const [AutofillHints.email],
            prefixIcon: const Icon(
              Icons.email_outlined,
              color: AppColors.grey5,
              size: 20,
            ),
            onSubmitted: (_) => _submit(),
            validator: (v) {
              if (v == null || v.trim().isEmpty) {
                return context.l10n.validationRequired;
              }
              if (!RegExp(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$').hasMatch(v.trim())) {
                return context.l10n.validationEmailInvalid;
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
            label: context.l10n.forgotPasswordButton,
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
          context.l10n.forgotPasswordTitle,
          style: AppTextStyles.headline2(AppColors.white),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        Text(
          context.l10n.forgotPasswordSuccess,
          style: AppTextStyles.body1(AppColors.grey3),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 40),
        TextButton(
          onPressed: () => context.go(AppRoutes.login),
          child: Text(context.l10n.btnBack),
        ),
      ],
    );
  }
}
