import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
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
  final _phoneCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
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
          phone: _phoneCtrl.text.trim().isEmpty ? null : _phoneCtrl.text.trim(),
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

    return Scaffold(
      appBar: AppBar(title: const Text('Créer un compte')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                Row(children: [
                  Expanded(child: MyCoachTextField(controller: _firstNameCtrl, label: 'Prénom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                  const SizedBox(width: 12),
                  Expanded(child: MyCoachTextField(controller: _lastNameCtrl, label: 'Nom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                ]),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _emailCtrl, label: 'Email', keyboardType: TextInputType.emailAddress, prefixIcon: const Icon(Icons.email_outlined), validator: (v) => v == null || !v.contains('@') ? 'Email invalide' : null),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _phoneCtrl, label: 'Téléphone (optionnel)', keyboardType: TextInputType.phone, prefixIcon: const Icon(Icons.phone_outlined)),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _passwordCtrl, label: 'Mot de passe', obscureText: true, prefixIcon: const Icon(Icons.lock_outline), validator: (v) => v == null || v.length < 6 ? 'Min. 6 caractères' : null),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _confirmCtrl, label: 'Confirmer le mot de passe', obscureText: true, prefixIcon: const Icon(Icons.lock_outline), validator: (v) => v?.trim() != _passwordCtrl.text.trim() ? 'Les mots de passe ne correspondent pas' : null),
                const SizedBox(height: 32),
                LoadingButton(onPressed: _submit, label: "S'inscrire", isLoading: authState.isLoading),
                const SizedBox(height: 16),
                TextButton(onPressed: () => context.pop(), child: const Text('Déjà un compte ? Se connecter')),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
