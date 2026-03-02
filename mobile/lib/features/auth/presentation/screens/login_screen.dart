import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/mycoach_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../providers/auth_providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _obscure = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    ref.read(authStateProvider.notifier).login(
          _emailCtrl.text.trim(),
          _passwordCtrl.text,
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
            SnackBar(content: Text('Erreur de connexion: $e'), backgroundColor: AppColors.error),
          );
        },
      );
    });

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.fitness_center, size: 64, color: AppColors.primary),
                  const SizedBox(height: 16),
                  Text('MyCoach', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.primary)),
                  const SizedBox(height: 8),
                  Text('Connectez-vous à votre espace coach', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary)),
                  const SizedBox(height: 40),
                  MyCoachTextField(
                    controller: _emailCtrl,
                    label: 'Email',
                    hint: 'coach@example.com',
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: const Icon(Icons.email_outlined),
                    validator: (v) => v == null || !v.contains('@') ? 'Email invalide' : null,
                  ),
                  const SizedBox(height: 20),
                  MyCoachTextField(
                    controller: _passwordCtrl,
                    label: 'Mot de passe',
                    obscureText: _obscure,
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setState(() => _obscure = !_obscure),
                    ),
                    validator: (v) => v == null || v.length < 8 ? 'Min. 8 caractères' : null,
                  ),
                  const SizedBox(height: 32),
                  LoadingButton(
                    onPressed: _submit,
                    label: 'Se connecter',
                    isLoading: authState.isLoading,
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => context.push('/register'),
                    child: const Text("Pas encore de compte ? S'inscrire"),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
