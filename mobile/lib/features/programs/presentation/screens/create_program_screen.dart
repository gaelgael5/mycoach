import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/program.dart';
import '../providers/programs_providers.dart';

const _levels = {'beginner': 'Débutant', 'intermediate': 'Intermédiaire', 'advanced': 'Avancé'};
const _goals = {
  'general_fitness': 'Forme générale',
  'muscle_gain': 'Prise de masse',
  'weight_loss': 'Perte de poids',
  'endurance': 'Endurance',
  'flexibility': 'Souplesse',
  'strength': 'Force',
  'rehabilitation': 'Réhabilitation',
};

class CreateProgramScreen extends ConsumerStatefulWidget {
  const CreateProgramScreen({super.key});

  @override
  ConsumerState<CreateProgramScreen> createState() => _CreateProgramScreenState();
}

class _CreateProgramScreenState extends ConsumerState<CreateProgramScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  int _weeks = 4;
  String _level = 'beginner';
  String _goal = 'general_fitness';
  final List<_SessionDraft> _sessions = [];
  bool _saving = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  void _addSession() {
    setState(() {
      _sessions.add(_SessionDraft(
        name: 'Séance ${_sessions.length + 1}',
        dayOfWeek: (_sessions.length % 7) + 1,
      ));
    });
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final program = Program(
        id: '',
        name: _nameCtrl.text.trim(),
        description: _descCtrl.text.trim().isEmpty ? null : _descCtrl.text.trim(),
        durationWeeks: _weeks,
        level: _level,
        goal: _goal,
        sessions: _sessions.map((s) => PlannedSession(
          sessionName: s.name,
          dayOfWeek: s.dayOfWeek,
          exercises: [],
        )).toList(),
        createdAt: DateTime.now(),
      );
      final repo = ref.read(programsRepositoryProvider);
      await repo.createProgram(program);
      ref.invalidate(programsProvider);
      if (mounted) context.pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur: $e'), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nouveau programme'),
        actions: [
          TextButton(
            onPressed: _saving ? null : _save,
            child: _saving
                ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Créer', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Name
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(labelText: 'Nom du programme *', border: OutlineInputBorder(), prefixIcon: Icon(Icons.fitness_center)),
              validator: (v) => v == null || v.trim().isEmpty ? 'Requis' : null,
            ),
            const SizedBox(height: 16),

            // Description
            TextFormField(
              controller: _descCtrl,
              decoration: const InputDecoration(labelText: 'Description', border: OutlineInputBorder()),
              maxLines: 3,
            ),
            const SizedBox(height: 16),

            // Duration
            Row(
              children: [
                const Icon(Icons.calendar_today, size: 18, color: AppColors.textSecondary),
                const SizedBox(width: 8),
                const Text('Durée :'),
                const SizedBox(width: 12),
                DropdownButton<int>(
                  value: _weeks,
                  items: List.generate(12, (i) => DropdownMenuItem(value: i + 1, child: Text('${i + 1} semaines'))),
                  onChanged: (v) => setState(() => _weeks = v!),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Level
            Text('Niveau', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _levels.entries.map((e) => ChoiceChip(
                label: Text(e.value),
                selected: _level == e.key,
                onSelected: (_) => setState(() => _level = e.key),
              )).toList(),
            ),
            const SizedBox(height: 16),

            // Goal
            Text('Objectif', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: _goals.entries.map((e) => ChoiceChip(
                label: Text(e.value),
                selected: _goal == e.key,
                onSelected: (_) => setState(() => _goal = e.key),
              )).toList(),
            ),
            const SizedBox(height: 24),

            // Sessions
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Séances (${_sessions.length})', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                TextButton.icon(onPressed: _addSession, icon: const Icon(Icons.add, size: 18), label: const Text('Ajouter')),
              ],
            ),
            const SizedBox(height: 8),

            if (_sessions.isEmpty)
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.outline, style: BorderStyle.solid),
                ),
                child: Column(
                  children: [
                    const Icon(Icons.event_note_outlined, size: 32, color: AppColors.outline),
                    const SizedBox(height: 8),
                    Text('Aucune séance', style: TextStyle(color: AppColors.textSecondary)),
                    const SizedBox(height: 4),
                    Text('Ajoutez des séances à votre programme', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
                  ],
                ),
              ),

            ..._sessions.asMap().entries.map((entry) {
              final i = entry.key;
              final s = entry.value;
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: AppColors.surfaceVariant)),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: AppColors.primaryContainer,
                    child: Text('${i + 1}', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
                  ),
                  title: Text(s.name),
                  subtitle: Text(PlannedSession.dayNames[s.dayOfWeek - 1]),
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: AppColors.error, size: 20),
                    onPressed: () => setState(() => _sessions.removeAt(i)),
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

class _SessionDraft {
  String name;
  int dayOfWeek;
  _SessionDraft({required this.name, required this.dayOfWeek});
}
