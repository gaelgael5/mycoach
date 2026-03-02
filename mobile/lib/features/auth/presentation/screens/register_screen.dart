import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl_phone_field/intl_phone_field.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/mycoach_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../providers/auth_providers.dart';

class RegisterScreen extends ConsumerStatefulWidget {
  const RegisterScreen({super.key});

  @override
  ConsumerState<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends ConsumerState<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _firstNameCtrl = TextEditingController();
  final _lastNameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  String? _fullPhoneNumber;

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    ref.read(authStateProvider.notifier).register(
          email: _emailCtrl.text.trim(),
          password: _passwordCtrl.text,
          firstName: _firstNameCtrl.text.trim(),
          lastName: _lastNameCtrl.text.trim(),
          phone: _fullPhoneNumber,
        );
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);

    ref.listen(authStateProvider, (prev, next) {
      next.whenOrNull(
        data: (user) {
          if (user != null) context.go('/dashboard');
        },
        error: (e, _) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erreur: $e'), backgroundColor: AppColors.error),
          );
        },
      );
    });

    // Detect country from device locale
    final locale = Localizations.localeOf(context);
    final initialCountry = locale.countryCode ?? 'FR';

    return Scaffold(
      appBar: AppBar(title: const Text('Créer un compte')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  Expanded(child: MyCoachTextField(controller: _firstNameCtrl, label: 'Prénom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                  const SizedBox(width: 12),
                  Expanded(child: MyCoachTextField(controller: _lastNameCtrl, label: 'Nom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                ]),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _emailCtrl, label: 'Email', keyboardType: TextInputType.emailAddress, prefixIcon: const Icon(Icons.email_outlined), validator: (v) => v == null || !v.contains('@') ? 'Email invalide' : null),
                const SizedBox(height: 16),
                Text('Téléphone (optionnel)', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 8),
                IntlPhoneField(
                  decoration: const InputDecoration(
                    hintText: '6 12 34 56 78',
                    counterText: '',
                  ),
                  initialCountryCode: initialCountry,
                  languageCode: locale.languageCode,
                  disableLengthCheck: false,
                  onChanged: (phone) {
                    _fullPhoneNumber = phone.completeNumber;
                  },
                  validator: (phone) {
                    // Optional field — only validate if user typed something
                    if (phone == null || phone.number.isEmpty) return null;
                    if (phone.number.length < 9) return 'Min. 9 chiffres';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _passwordCtrl, label: 'Mot de passe', obscureText: true, prefixIcon: const Icon(Icons.lock_outline), validator: (v) => v == null || v.length < 8 ? 'Min. 8 caractères' : null),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _confirmCtrl, label: 'Confirmer le mot de passe', obscureText: true, prefixIcon: const Icon(Icons.lock_outline), validator: (v) => v?.trim() != _passwordCtrl.text.trim() ? 'Les mots de passe ne correspondent pas' : null),
                const SizedBox(height: 32),
                LoadingButton(onPressed: _submit, label: "S'inscrire", isLoading: authState.isLoading),
                const SizedBox(height: 16),
                Center(child: TextButton(onPressed: () => context.pop(), child: const Text('Déjà un compte ? Se connecter'))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
