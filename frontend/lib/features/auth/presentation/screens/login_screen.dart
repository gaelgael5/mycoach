import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/api/api_exception.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/gradient_button.dart';
import '../widgets/social_auth_button.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authStateProvider.notifier).login(
            email: _emailCtrl.text.trim(),
            password: _passwordCtrl.text,
          );
      // Navigation gérée par routerProvider via userRoleProvider
    } catch (e) {
      if (mounted) setState(() => _errorMessage = _localizeError(e));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  String _localizeError(Object e) {
    final l10n = context.l10n;
    final code = extractApiErrorCode(e);
    return switch (code) {
      ApiErrorCode.invalidCredentials => l10n.loginInvalidCredentials,
      ApiErrorCode.emailNotVerified => l10n.loginEmailNotVerified,
      ApiErrorCode.accountSuspended => l10n.loginAccountSuspended,
      ApiErrorCode.tooManyAttempts =>
        l10n.loginTooManyAttempts(extractRetryAfterMinutes(e)),
      _ => (e is AppDioException && e.response == null)
          ? l10n.errorNetwork
          : l10n.errorGeneric,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 24),
                // Logo
                Center(
                  child: Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      gradient: AppGradients.accentButton,
                      borderRadius: BorderRadius.circular(AppRadius.card),
                    ),
                    child: const Icon(
                      Icons.fitness_center,
                      color: AppColors.white,
                      size: 32,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                Text(
                  context.l10n.loginTitle,
                  style: AppTextStyles.headline1(AppColors.white),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  context.l10n.loginSubtitle,
                  style: AppTextStyles.body1(AppColors.grey3),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),

                // Email
                AuthTextField(
                  label: context.l10n.labelEmail,
                  hint: 'email@exemple.com',
                  controller: _emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  textInputAction: TextInputAction.next,
                  autofillHints: const [AutofillHints.email],
                  prefixIcon: const Icon(
                    Icons.email_outlined,
                    color: AppColors.grey5,
                    size: 20,
                  ),
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) {
                      return context.l10n.validationRequired;
                    }
                    if (!_isValidEmail(v.trim())) {
                      return context.l10n.validationEmailInvalid;
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Password
                AuthTextField(
                  label: context.l10n.labelPassword,
                  controller: _passwordCtrl,
                  isPassword: true,
                  textInputAction: TextInputAction.done,
                  autofillHints: const [AutofillHints.password],
                  prefixIcon: const Icon(
                    Icons.lock_outline,
                    color: AppColors.grey5,
                    size: 20,
                  ),
                  onSubmitted: (_) => _submit(),
                  validator: (v) {
                    if (v == null || v.isEmpty) {
                      return context.l10n.validationRequired;
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 8),

                // Forgot password
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () => context.push(AppRoutes.forgotPassword),
                    child: Text(context.l10n.loginForgotPassword),
                  ),
                ),
                const SizedBox(height: 8),

                // Error message
                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.red.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(AppRadius.input),
                      border: Border.all(color: AppColors.red.withOpacity(0.4)),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: AppTextStyles.body2(AppColors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // Login button
                GradientButton(
                  label: context.l10n.loginButton,
                  onPressed: _isLoading ? null : _submit,
                  isLoading: _isLoading,
                ),
                const SizedBox(height: 24),

                // Divider
                Row(
                  children: [
                    const Expanded(child: Divider(color: AppColors.grey7)),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      child: Text(
                        context.l10n.orSeparator,
                        style: AppTextStyles.caption(AppColors.grey5),
                      ),
                    ),
                    const Expanded(child: Divider(color: AppColors.grey7)),
                  ],
                ),
                const SizedBox(height: 16),

                // Google
                SocialAuthButton(
                  label: context.l10n.loginWithGoogle,
                  iconBuilder: () => const GoogleIcon(),
                  onPressed: null, // Phase A2
                ),
                const SizedBox(height: 32),

                // No account
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      context.l10n.loginNoAccount,
                      style: AppTextStyles.body2(AppColors.grey3),
                    ),
                    TextButton(
                      onPressed: () => context.go(AppRoutes.registerRole),
                      child: Text(context.l10n.loginSignUp),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static bool _isValidEmail(String v) =>
      RegExp(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$').hasMatch(v);
}
