import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/program.dart';
import '../../../../shared/widgets/empty_state.dart';
import '../../../../shared/widgets/shimmer_list.dart';
import '../providers/programs_providers.dart';

const _levels = {'beginner': 'Débutant', 'intermediate': 'Intermédiaire', 'advanced': 'Avancé'};


class ProgramsListScreen extends ConsumerWidget {
  const ProgramsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final programsAsync = ref.watch(programsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Programmes')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/programs/create'),
        icon: const Icon(Icons.add),
        label: const Text('Nouveau'),
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(programsProvider),
        child: programsAsync.when(
          loading: () => const ShimmerList(),
          error: (e, _) => ListView(children: [
            const SizedBox(height: 100),
            Center(child: Text('Erreur: $e')),
            const SizedBox(height: 12),
            Center(
              child: ElevatedButton(
                onPressed: () => ref.invalidate(programsProvider),
                child: const Text('Réessayer'),
              ),
            ),
          ]),
          data: (programs) => programs.isEmpty
              ? ListView(children: const [
                  SizedBox(height: 80),
                  EmptyState(
                    icon: Icons.fitness_center_outlined,
                    title: 'Aucun programme',
                    subtitle: "Créez votre premier programme d'entraînement",
                  ),
                ])
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: programs.length,
                  itemBuilder: (context, index) =>
                      _ProgramCard(program: programs[index]),
                ),
        ),
      ),
    );
  }
}

class _ProgramCard extends StatelessWidget {
  final Program program;
  const _ProgramCard({required this.program});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      color: AppColors.surface,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => context.push('/programs/${program.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.fitness_center, color: AppColors.primary),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(program.name,
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    Text(
                      '${program.sessions.length} séances · ${program.durationWeeks} sem. · ${_levels[program.level] ?? program.level}',
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: AppColors.textSecondary),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textSecondary),
            ],
          ),
        ),
      ),
    );
  }
}
