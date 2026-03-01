import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/mycoach_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../providers/programs_providers.dart';

class CreateProgramScreen extends ConsumerStatefulWidget {
  const CreateProgramScreen({super.key});

  @override
  ConsumerState<CreateProgramScreen> createState() => _CreateProgramScreenState();
}

class _CreateProgramScreenState extends ConsumerState<CreateProgramScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  int _durationWeeks = 4;
  bool _loading = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _loading = true);
    try {
      await ref.read(programsRepositoryProvider).createProgram({
        'name': _nameCtrl.text.trim(),
        'description': _descCtrl.text.trim(),
        'duration_weeks': _durationWeeks,
      });
      ref.invalidate(programsProvider);
      if (mounted) context.pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nouveau programme')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              MyCoachTextField(
                controller: _nameCtrl,
                label: 'Nom du programme',
                hint: 'Ex: Prise de masse 12 semaines',
                validator: (v) => v == null || v.isEmpty ? 'Requis' : null,
              ),
              const SizedBox(height: 16),
              MyCoachTextField(
                controller: _descCtrl,
                label: 'Description',
                hint: 'Objectifs, notes...',
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              Text('Durée (semaines)', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              Row(
                children: [
                  IconButton.filled(
                    onPressed: _durationWeeks > 1 ? () => setState(() => _durationWeeks--) : null,
                    icon: const Icon(Icons.remove),
                    style: IconButton.styleFrom(backgroundColor: AppColors.primary.withValues(alpha: 0.1)),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Text('$_durationWeeks', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                  ),
                  IconButton.filled(
                    onPressed: _durationWeeks < 52 ? () => setState(() => _durationWeeks++) : null,
                    icon: const Icon(Icons.add),
                    style: IconButton.styleFrom(backgroundColor: AppColors.primary.withValues(alpha: 0.1)),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              LoadingButton(
                onPressed: _save,
                isLoading: _loading,
                label: 'Créer le programme',
              ),
            ],
          ),
        ),
      ),
    );
  }
}
