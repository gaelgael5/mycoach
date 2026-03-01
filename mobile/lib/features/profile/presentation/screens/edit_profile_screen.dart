import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/mycoach_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../providers/profile_providers.dart';
import '../../data/profile_repository.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  final CoachProfile profile;
  const EditProfileScreen({super.key, required this.profile});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  late final TextEditingController _firstNameCtrl;
  late final TextEditingController _lastNameCtrl;
  late final TextEditingController _phoneCtrl;
  late final TextEditingController _bioCtrl;
  late final TextEditingController _specialtiesCtrl;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _firstNameCtrl = TextEditingController(text: widget.profile.firstName);
    _lastNameCtrl = TextEditingController(text: widget.profile.lastName);
    _phoneCtrl = TextEditingController(text: widget.profile.phone ?? '');
    _bioCtrl = TextEditingController(text: widget.profile.bio ?? '');
    _specialtiesCtrl =
        TextEditingController(text: widget.profile.specialties.join(', '));
  }

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _phoneCtrl.dispose();
    _bioCtrl.dispose();
    _specialtiesCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final specialties = _specialtiesCtrl.text
          .split(',')
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList();
      await ref.read(profileProvider.notifier).updateProfile({
        'first_name': _firstNameCtrl.text.trim(),
        'last_name': _lastNameCtrl.text.trim(),
        'phone': _phoneCtrl.text.trim().isEmpty ? null : _phoneCtrl.text.trim(),
        'bio': _bioCtrl.text.trim().isEmpty ? null : _bioCtrl.text.trim(),
        'specialties': specialties,
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Profil mis à jour ✓'),
            backgroundColor: AppColors.secondary,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: $e'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Modifier le profil')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          MyCoachTextField(controller: _firstNameCtrl, label: 'Prénom'),
          const SizedBox(height: 12),
          MyCoachTextField(controller: _lastNameCtrl, label: 'Nom'),
          const SizedBox(height: 12),
          MyCoachTextField(
              controller: _phoneCtrl,
              label: 'Téléphone',
              keyboardType: TextInputType.phone),
          const SizedBox(height: 12),
          MyCoachTextField(
              controller: _specialtiesCtrl,
              label: 'Spécialités (séparées par des virgules)'),
          const SizedBox(height: 12),
          MyCoachTextField(
              controller: _bioCtrl,
              label: 'Bio',
              maxLines: 4),
          const SizedBox(height: 24),
          LoadingButton(
            onPressed: _save,
            isLoading: _saving,
            label: 'Enregistrer',
          ),
        ],
      ),
    );
  }
}
