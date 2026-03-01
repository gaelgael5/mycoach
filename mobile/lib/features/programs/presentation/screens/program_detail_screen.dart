import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/program.dart';
import '../../../../features/clients/presentation/providers/clients_providers.dart';
import '../../../../shared/models/client.dart';
import '../providers/programs_providers.dart';

class ProgramDetailScreen extends ConsumerWidget {
  final String programId;
  const ProgramDetailScreen({super.key, required this.programId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(programDetailProvider(programId));

    return detailAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(appBar: AppBar(), body: Center(child: Text('Erreur: $e'))),
      data: (program) => _ProgramDetailBody(program: program),
    );
  }
}

class _ProgramDetailBody extends ConsumerWidget {
  final Program program;
  const _ProgramDetailBody({required this.program});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionsByDay = <int, List<Session>>{};
    for (final s in program.sessions) {
      sessionsByDay.putIfAbsent(s.dayOfWeek, () => []).add(s);
    }
    final sortedDays = sessionsByDay.keys.toList()..sort();

    return Scaffold(
      appBar: AppBar(
        title: Text(program.name),
        actions: [
          IconButton(
            icon: const Icon(Icons.people_alt_outlined),
            tooltip: 'Assigner des clients',
            onPressed: () => _showAssignDialog(context, ref),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddSessionSheet(context, ref),
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.onPrimary,
        child: const Icon(Icons.add),
      ),
      body: program.sessions.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.event_note_outlined, size: 64, color: AppColors.primary.withValues(alpha: 0.3)),
                  const SizedBox(height: 12),
                  const Text('Aucune séance'),
                  const SizedBox(height: 4),
                  Text('Ajoutez une séance avec le bouton +', style: TextStyle(color: AppColors.textSecondary)),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (program.description != null && program.description!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16),
                    child: Text(program.description!, style: TextStyle(color: AppColors.textSecondary)),
                  ),
                Text('${program.durationWeeks} semaines · ${program.assignedClientIds.length} clients',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
                const SizedBox(height: 16),
                for (final day in sortedDays) ...[
                  Text(Session.dayNames[day - 1],
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.primary)),
                  const SizedBox(height: 8),
                  for (final session in sessionsByDay[day]!) _SessionCard(session: session, programId: program.id),
                  const SizedBox(height: 16),
                ],
              ],
            ),
    );
  }

  void _showAddSessionSheet(BuildContext context, WidgetRef ref) {
    final titleCtrl = TextEditingController();
    int selectedDay = 1;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => Padding(
          padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Nouvelle séance', style: Theme.of(ctx).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              TextField(controller: titleCtrl, decoration: const InputDecoration(labelText: 'Titre de la séance', border: OutlineInputBorder())),
              const SizedBox(height: 16),
              DropdownButtonFormField<int>(
                value: selectedDay,
                decoration: const InputDecoration(labelText: 'Jour', border: OutlineInputBorder()),
                items: List.generate(7, (i) => DropdownMenuItem(value: i + 1, child: Text(Session.dayNames[i]))),
                onChanged: (v) => setSheetState(() => selectedDay = v!),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: () async {
                  if (titleCtrl.text.trim().isEmpty) return;
                  await ref.read(programsRepositoryProvider).addSession(program.id, {
                    'title': titleCtrl.text.trim(),
                    'day_of_week': selectedDay,
                  });
                  ref.invalidate(programDetailProvider(program.id));
                  if (ctx.mounted) Navigator.pop(ctx);
                },
                child: const Text('Ajouter'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAssignDialog(BuildContext context, WidgetRef ref) {
    final clientsAsync = ref.read(clientsListProvider);
    clientsAsync.when(
      loading: () {},
      error: (_, __) => ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur chargement clients'))),
      data: (clients) {
        final selected = Set<String>.from(program.assignedClientIds);
        showDialog(
          context: context,
          builder: (ctx) => StatefulBuilder(
            builder: (ctx, setDialogState) => AlertDialog(
              title: const Text('Assigner des clients'),
              content: SizedBox(
                width: double.maxFinite,
                child: ListView(
                  shrinkWrap: true,
                  children: clients.map((c) => CheckboxListTile(
                        title: Text(c.fullName),
                        subtitle: Text(c.email),
                        value: selected.contains(c.id),
                        onChanged: (v) => setDialogState(() {
                          if (v == true) selected.add(c.id); else selected.remove(c.id);
                        }),
                      )).toList(),
                ),
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Annuler')),
                FilledButton(
                  onPressed: () async {
                    await ref.read(programsRepositoryProvider).assignClients(program.id, selected.toList());
                    ref.invalidate(programDetailProvider(program.id));
                    if (ctx.mounted) Navigator.pop(ctx);
                  },
                  child: const Text('Assigner'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SessionCard extends ConsumerWidget {
  final Session session;
  final String programId;
  const _SessionCard({required this.session, required this.programId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 0,
      color: AppColors.surface,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(session.title, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600))),
                IconButton(
                  icon: const Icon(Icons.add_circle_outline, size: 20),
                  tooltip: 'Ajouter exercice',
                  onPressed: () => _showAddExerciseSheet(context, ref),
                ),
              ],
            ),
            if (session.exercises.isNotEmpty) ...[
              const Divider(height: 16),
              ...session.exercises.map((ex) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      children: [
                        const Icon(Icons.circle, size: 6, color: AppColors.secondary),
                        const SizedBox(width: 8),
                        Expanded(child: Text(ex.name)),
                        Text(ex.summary, style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                      ],
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }

  void _showAddExerciseSheet(BuildContext context, WidgetRef ref) {
    final nameCtrl = TextEditingController();
    final setsCtrl = TextEditingController(text: '3');
    final repsCtrl = TextEditingController(text: '10');
    final weightCtrl = TextEditingController(text: '20');
    final restCtrl = TextEditingController(text: '60');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Nouvel exercice', style: Theme.of(ctx).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Nom de l\'exercice', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: TextField(controller: setsCtrl, decoration: const InputDecoration(labelText: 'Séries', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
              const SizedBox(width: 12),
              Expanded(child: TextField(controller: repsCtrl, decoration: const InputDecoration(labelText: 'Reps', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
            ]),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: TextField(controller: weightCtrl, decoration: const InputDecoration(labelText: 'Charge (kg)', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
              const SizedBox(width: 12),
              Expanded(child: TextField(controller: restCtrl, decoration: const InputDecoration(labelText: 'Repos (s)', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
            ]),
            const SizedBox(height: 24),
            FilledButton(
              onPressed: () async {
                if (nameCtrl.text.trim().isEmpty) return;
                await ref.read(programsRepositoryProvider).addExercise(session.id, {
                  'name': nameCtrl.text.trim(),
                  'sets': int.tryParse(setsCtrl.text) ?? 3,
                  'reps': int.tryParse(repsCtrl.text) ?? 10,
                  'weight_kg': double.tryParse(weightCtrl.text) ?? 0,
                  'rest_seconds': int.tryParse(restCtrl.text) ?? 60,
                });
                ref.invalidate(programDetailProvider(programId));
                if (ctx.mounted) Navigator.pop(ctx);
              },
              child: const Text('Ajouter'),
            ),
          ],
        ),
      ),
    );
  }
}
