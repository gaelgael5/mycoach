import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl_phone_field/intl_phone_field.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/mycoach_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../providers/auth_providers.dart';

const _activitySectors = [
  'Coach sportif',
  'Préparateur physique',
  'Professeur de Yoga',
  'Professeur de Pilates',
  'Coach bien-être',
  'Nutritionniste',
  'Kinésithérapeute',
  'Professeur de danse',
  'Coach de CrossFit',
  'Personal trainer',
  'Autre',
];

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
  String? _selectedSector;
  bool _passwordVisible = false;

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) return 'Requis';
    if (value.length < 8) return 'Min. 8 caractères';
    if (!value.contains(RegExp(r'[A-Z]'))) return 'Au moins 1 majuscule';
    if (!value.contains(RegExp(r'[0-9]'))) return 'Au moins 1 chiffre';
    return null;
  }
  List<String> _getMissingPasswordCriteria(String? password) {
    final missing = <String>[];
    if (password == null || password.isEmpty) {
      missing.add('Le mot de passe est requis');
      return missing;
    }
    if (password.length < 8) missing.add('Au moins 8 caractères');
    if (!password.contains(RegExp(r'[A-Z]'))) missing.add('Au moins 1 majuscule (A-Z)');
    if (!password.contains(RegExp(r'[0-9]'))) missing.add('Au moins 1 chiffre (0-9)');
    return missing;
  }


  Widget _buildPasswordCriteria() {
    final password = _passwordCtrl.text;
    final hasLength = password.length >= 8;
    final hasUpper = password.contains(RegExp(r'[A-Z]'));
    final hasDigit = password.contains(RegExp(r'[0-9]'));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 8),
        Text('Le mot de passe doit contenir :', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 4),
        _PasswordCriterion('Au moins 8 caractères', hasLength),
        _PasswordCriterion('Au moins 1 majuscule (A-Z)', hasUpper),
        _PasswordCriterion('Au moins 1 chiffre (0-9)', hasDigit),
      ],
    );
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedSector == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez sélectionner votre secteur d\'activité'), backgroundColor: AppColors.error),
      );
      return;
    }
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
                // Header
                Text('Rejoignez +500 professionnels', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.textSecondary)),
                const SizedBox(height: 24),

                // Je suis un professionnel
                Text('Je suis un professionnel', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 12),

                // Activity sector dropdown
                DropdownButtonFormField<String>(
                  value: _selectedSector,
                  decoration: InputDecoration(
                    labelText: 'Secteur d\'activité *',
                    prefixIcon: const Icon(Icons.work_outline),
                    filled: true,
                    fillColor: AppColors.surfaceVariant,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  items: _activitySectors.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
                  onChanged: (v) => setState(() => _selectedSector = v),
                  validator: (v) => v == null ? 'Requis' : null,
                ),

                const SizedBox(height: 24),

                // Personal info
                Text('Mes informations', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 12),

                Row(children: [
                  Expanded(child: MyCoachTextField(controller: _firstNameCtrl, label: 'Prénom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                  const SizedBox(width: 12),
                  Expanded(child: MyCoachTextField(controller: _lastNameCtrl, label: 'Nom', validator: (v) => v == null || v.isEmpty ? 'Requis' : null)),
                ]),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _emailCtrl, label: 'Email', keyboardType: TextInputType.emailAddress, prefixIcon: const Icon(Icons.email_outlined), validator: (v) => v == null || !v.contains('@') ? 'Email invalide' : null),
                const SizedBox(height: 16),

                // Phone
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
                    if (phone == null || phone.number.isEmpty) return null;
                    if (phone.number.length < 9) return 'Min. 9 chiffres';
                    return null;
                  },
                ),

                const SizedBox(height: 24),

                // Password section
                Text('Sécurité', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 12),

                MyCoachTextField(
                  controller: _passwordCtrl,
                  label: 'Mot de passe',
                  obscureText: !_passwordVisible,
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(_passwordVisible ? Icons.visibility_off : Icons.visibility, size: 20),
                    onPressed: () => setState(() => _passwordVisible = !_passwordVisible),
                  ),
                  onChanged: (v) => setState(() {}),
                  validator: _validatePassword,
                ),
                _buildPasswordCriteria(),
                const SizedBox(height: 16),
                MyCoachTextField(controller: _confirmCtrl, label: 'Confirmer le mot de passe', obscureText: true, prefixIcon: const Icon(Icons.lock_outline), validator: (v) => v?.trim() != _passwordCtrl.text.trim() ? 'Les mots de passe ne correspondent pas' : null),
                const SizedBox(height: 32),

                // Submit
                LoadingButton(onPressed: _submit, label: "Créer mon compte", isLoading: authState.isLoading),
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

class _PasswordCriterion extends StatelessWidget {
  final String text;
  final bool valid;

  const _PasswordCriterion(this.text, this.valid);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(
            valid ? Icons.check_circle : Icons.radio_button_unchecked,
            size: 16,
            color: valid ? AppColors.secondary : AppColors.outline,
          ),
          const SizedBox(width: 8),
          Text(
            text,
            style: TextStyle(
              fontSize: 12,
              color: valid ? AppColors.secondary : AppColors.textSecondary,
              fontWeight: valid ? FontWeight.w500 : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }
}
