import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/program.dart';
import '../providers/programs_providers.dart';

const _levelLabels = {'beginner': 'Débutant', 'intermediate': 'Intermédiaire', 'advanced': 'Avancé'};
const _goalLabels = {
  'general_fitness': 'Forme générale', 'muscle_gain': 'Prise de masse',
  'weight_loss': 'Perte de poids', 'endurance': 'Endurance',
  'flexibility': 'Souplesse', 'strength': 'Force', 'rehabilitation': 'Réhabilitation',
};

class ProgramDetailScreen extends ConsumerWidget {
  final String programId;
  const ProgramDetailScreen({super.key, required this.programId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(programDetailProvider(programId));

    return detailAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(appBar: AppBar(), body: Center(child: Text('Erreur: $e'))),
      data: (program) => Scaffold(
        body: CustomScrollView(
          slivers: [
            SliverAppBar(
              expandedHeight: 160,
              pinned: true,
              backgroundColor: AppColors.primary,
              iconTheme: const IconThemeData(color: Colors.white),
              actions: [
                PopupMenuButton<String>(
                  icon: const Icon(Icons.more_vert),
                  onSelected: (v) async {
                    final repo = ref.read(programsRepositoryProvider);
                    if (v == 'duplicate') {
                      await repo.duplicateProgram(program.id);
                      ref.invalidate(programsProvider);
                    } else if (v == 'archive') {
                      await repo.archiveProgram(program.id);
                      ref.invalidate(programsProvider);
                      if (context.mounted) Navigator.pop(context);
                    }
                  },
                  itemBuilder: (_) => [
                    const PopupMenuItem(value: 'duplicate', child: Text('Dupliquer')),
                    const PopupMenuItem(value: 'archive', child: Text('Archiver', style: TextStyle(color: AppColors.error))),
                  ],
                ),
              ],
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: const BoxDecoration(
                    gradient: LinearGradient(colors: [Color(0xFF2563EB), Color(0xFF1D4ED8)], begin: Alignment.topCenter, end: Alignment.bottomCenter),
                  ),
                  child: SafeArea(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(program.name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white)),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            _HeaderChip(Icons.timer_outlined, '${program.durationWeeks} sem.'),
                            const SizedBox(width: 12),
                            _HeaderChip(Icons.signal_cellular_alt, _levelLabels[program.level] ?? program.level),
                            const SizedBox(width: 12),
                            _HeaderChip(Icons.flag_outlined, _goalLabels[program.goal] ?? program.goal),
                          ],
                        ),
                        const SizedBox(height: 16),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  if (program.description != null && program.description!.isNotEmpty) ...[
                    Text(program.description!, style: TextStyle(color: AppColors.textSecondary)),
                    const SizedBox(height: 16),
                  ],

                  if (program.isAiGenerated)
                    Container(
                      margin: const EdgeInsets.only(bottom: 16),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF0F9FF),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFBAE6FD)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.auto_awesome, size: 18, color: Color(0xFF0284C7)),
                          const SizedBox(width: 8),
                          const Expanded(child: Text('Programme généré par IA', style: TextStyle(color: Color(0xFF0284C7), fontWeight: FontWeight.w500))),
                        ],
                      ),
                    ),

                  // Sessions
                  Text('Séances (${program.sessions.length})', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),

                  if (program.sessions.isEmpty)
                    Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          children: [
                            Icon(Icons.event_note_outlined, size: 48, color: AppColors.outline),
                            const SizedBox(height: 8),
                            Text('Aucune séance', style: TextStyle(color: AppColors.textSecondary)),
                          ],
                        ),
                      ),
                    ),

                  ...program.sessions.map((session) => _SessionCard(session: session)),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HeaderChip extends StatelessWidget {
  final IconData icon;
  final String label;
  const _HeaderChip(this.icon, this.label);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.white.withValues(alpha: 0.8)),
          const SizedBox(width: 4),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.white.withValues(alpha: 0.9))),
        ],
      ),
    );
  }
}

class _SessionCard extends StatelessWidget {
  final PlannedSession session;
  const _SessionCard({required this.session});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: AppColors.surfaceVariant)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: AppColors.primaryContainer, borderRadius: BorderRadius.circular(8)),
                  child: Text(session.dayName, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.primary)),
                ),
                const SizedBox(width: 12),
                Expanded(child: Text(session.sessionName, style: const TextStyle(fontWeight: FontWeight.w600))),
                if (session.estimatedDurationMin != null)
                  Text('${session.estimatedDurationMin} min', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
              ],
            ),
            if (session.exercises.isNotEmpty) ...[
              const Divider(height: 20),
              ...session.exercises.map((ex) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 3),
                    child: Row(
                      children: [
                        const Icon(Icons.circle, size: 6, color: AppColors.secondary),
                        const SizedBox(width: 8),
                        Expanded(child: Text(ex.exerciseName ?? ex.exerciseTypeId, style: const TextStyle(fontSize: 14))),
                        Text(ex.summary, style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                      ],
                    ),
                  )),
            ] else
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text('Aucun exercice', style: TextStyle(fontSize: 13, color: AppColors.outline, fontStyle: FontStyle.italic)),
              ),
          ],
        ),
      ),
    );
  }
}
