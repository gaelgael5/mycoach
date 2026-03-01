import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/program.dart';
import '../../../../shared/models/tracking.dart';
import '../../../programs/presentation/providers/programs_providers.dart';
import '../providers/tracking_providers.dart';

class ClientProgramScreen extends ConsumerStatefulWidget {
  final String programId;
  const ClientProgramScreen({super.key, required this.programId});

  @override
  ConsumerState<ClientProgramScreen> createState() => _ClientProgramScreenState();
}

class _ClientProgramScreenState extends ConsumerState<ClientProgramScreen> {
  final Map<String, TextEditingController> _weightControllers = {};

  @override
  void dispose() {
    for (final c in _weightControllers.values) c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final programAsync = ref.watch(programDetailProvider(widget.programId));
    final today = DateTime.now().weekday; // 1=Mon

    return Scaffold(
      appBar: AppBar(title: const Text('Mon programme')),
      body: programAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (program) {
          final todaySessions = program.sessions.where((s) => s.dayOfWeek == today).toList();
          if (todaySessions.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.weekend_outlined, size: 64, color: AppColors.secondary.withValues(alpha: 0.4)),
                  const SizedBox(height: 12),
                  const Text('Pas de séance aujourd\'hui 🎉'),
                  Text('Profitez de votre repos !', style: TextStyle(color: AppColors.textSecondary)),
                ],
              ),
            );
          }
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Text('Séances du jour', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              for (final session in todaySessions) _buildSessionCard(context, session),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSessionCard(BuildContext context, Session session) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(session.title, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            const Divider(height: 24),
            for (final ex in session.exercises) _buildExerciseRow(ex),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: () => _completeSession(session),
                icon: const Icon(Icons.check_circle_outline),
                label: const Text('Marquer comme faite'),
                style: FilledButton.styleFrom(backgroundColor: AppColors.secondary),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExerciseRow(Exercise ex) {
    _weightControllers.putIfAbsent(ex.id, () => TextEditingController(text: ex.weightKg.toString()));
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(ex.name, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text('${ex.sets}×${ex.reps}', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
              ],
            ),
          ),
          SizedBox(
            width: 80,
            child: TextField(
              controller: _weightControllers[ex.id],
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                suffixText: 'kg',
                isDense: true,
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 8, vertical: 8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _completeSession(Session session) async {
    final logs = session.exercises.map((ex) => ExerciseLog(
          exerciseId: ex.id,
          actualWeightKg: double.tryParse(_weightControllers[ex.id]?.text ?? '') ?? ex.weightKg,
          actualReps: ex.reps,
          actualSets: ex.sets,
        ).toJson()).toList();

    try {
      await ref.read(trackingRepositoryProvider).completeSession(session.id, logs);
      ref.invalidate(trackingProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Séance validée ✅'), backgroundColor: AppColors.secondary),
        );
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
    }
  }
}
