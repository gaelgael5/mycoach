import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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

/// Écran d'inscription pour un client (sportif).
/// Flow : RegisterClientScreen → POST register → EmailVerificationScreen → ClientHome
class RegisterClientScreen extends ConsumerStatefulWidget {
  const RegisterClientScreen({super.key});

  @override
  ConsumerState<RegisterClientScreen> createState() =>
      _RegisterClientScreenState();
}

class _RegisterClientScreenState extends ConsumerState<RegisterClientScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmPasswordCtrl = TextEditingController();
  final _birthYearCtrl = TextEditingController();

  String? _selectedGender;
  bool _isLoading = false;
  String? _errorMessage;
  bool _acceptedCgu = false;

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmPasswordCtrl.dispose();
    _birthYearCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (!_acceptedCgu) {
      setState(() => _errorMessage = context.l10n.registerCguRequired);
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authStateProvider.notifier).register(
            email: _emailCtrl.text.trim(),
            password: _passwordCtrl.text,
            firstName: _firstNameCtrl.text.trim(),
            lastName: _lastNameCtrl.text.trim(),
            role: 'client',
            gender: _selectedGender,
            birthYear: _birthYearCtrl.text.isNotEmpty
                ? int.tryParse(_birthYearCtrl.text)
                : null,
          );
      if (mounted) context.go(AppRoutes.verifyEmail);
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
      ApiErrorCode.emailAlreadyExists => l10n.registerEmailAlreadyExists,
      ApiErrorCode.blockedEmailDomain => l10n.registerEmailBlocked,
      _ => (e is AppDioException && e.response == null)
          ? l10n.errorNetwork
          : l10n.errorGeneric,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.grey1),
          onPressed: () => context.go(AppRoutes.registerRole),
        ),
        title: Text(
          context.l10n.registerClientTitle,
          style: AppTextStyles.headline4(AppColors.white),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // First Name + Last Name
                Row(
                  children: [
                    Expanded(
                      child: AuthTextField(
                        label: context.l10n.labelFirstName,
                        controller: _firstNameCtrl,
                        textInputAction: TextInputAction.next,
                        autofillHints: const [AutofillHints.givenName],
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? context.l10n.validationRequired
                            : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: AuthTextField(
                        label: context.l10n.labelLastName,
                        controller: _lastNameCtrl,
                        textInputAction: TextInputAction.next,
                        autofillHints: const [AutofillHints.familyName],
                        validator: (v) => (v == null || v.trim().isEmpty)
                            ? context.l10n.validationRequired
                            : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

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
                  textInputAction: TextInputAction.next,
                  autofillHints: const [AutofillHints.newPassword],
                  validator: (v) {
                    if (v == null || v.isEmpty) {
                      return context.l10n.validationRequired;
                    }
                    if (!_isStrongPassword(v)) {
                      return context.l10n.registerPasswordWeak;
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Confirm password
                AuthTextField(
                  label: context.l10n.labelPasswordConfirm,
                  controller: _confirmPasswordCtrl,
                  isPassword: true,
                  textInputAction: TextInputAction.next,
                  validator: (v) {
                    if (v != _passwordCtrl.text) {
                      return context.l10n.registerPasswordMismatch;
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // Gender (optional)
                GenderDropdown(
                  value: _selectedGender,
                  onChanged: (v) => setState(() => _selectedGender = v),
                ),
                const SizedBox(height: 16),

                // Birth year (optional)
                AuthTextField(
                  label:
                      '${context.l10n.labelBirthYear} (${context.l10n.labelOptional})',
                  hint: '1990',
                  controller: _birthYearCtrl,
                  keyboardType: TextInputType.number,
                  textInputAction: TextInputAction.done,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(4),
                  ],
                  validator: (v) {
                    if (v == null || v.isEmpty) return null;
                    final year = int.tryParse(v);
                    if (year == null || year < 1900 || year > 2015) {
                      return context.l10n.validationBirthYearInvalid;
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                // CGU
                CguCheckbox(
                  value: _acceptedCgu,
                  onChanged: (v) => setState(() => _acceptedCgu = v ?? false),
                ),
                const SizedBox(height: 16),

                // Error
                if (_errorMessage != null) ...[
                  AuthErrorBanner(message: _errorMessage!),
                  const SizedBox(height: 16),
                ],

                // Submit
                GradientButton(
                  label: context.l10n.registerCreateAccount,
                  onPressed: _isLoading ? null : _submit,
                  isLoading: _isLoading,
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  static bool _isValidEmail(String v) =>
      RegExp(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$').hasMatch(v);

  static bool _isStrongPassword(String v) =>
      v.length >= 8 &&
      v.contains(RegExp(r'[A-Z]')) &&
      v.contains(RegExp(r'[0-9]'));
}
