import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/program.dart';
import '../providers/performance_providers.dart';

class MyProgramScreen extends ConsumerWidget {
  const MyProgramScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final programAsync = ref.watch(assignedProgramProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.programTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: programAsync.when(
        loading: () => const Center(
            child: CircularProgressIndicator(color: AppColors.accent)),
        error: (e, _) => Center(
          child: Text(l10n.errorGeneric,
              style: AppTextStyles.body1(AppColors.red)),
        ),
        data: (program) {
          if (program == null) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.fitness_center,
                      color: AppColors.grey5, size: 64),
                  const SizedBox(height: 16),
                  Text(
                    l10n.programEmpty,
                    style: AppTextStyles.body1(AppColors.grey3),
                  ),
                ],
              ),
            );
          }
          return _ProgramContent(program: program);
        },
      ),
    );
  }
}

class _ProgramContent extends StatefulWidget {
  const _ProgramContent({required this.program});
  final Program program;

  @override
  State<_ProgramContent> createState() => _ProgramContentState();
}

class _ProgramContentState extends State<_ProgramContent>
    with TickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: widget.program.days.isEmpty ? 1 : widget.program.days.length,
      vsync: this,
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final days = widget.program.days;

    return Column(
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.program.name,
                style: AppTextStyles.headline3(AppColors.white),
              ),
              if (widget.program.description != null) ...[
                const SizedBox(height: 4),
                Text(
                  widget.program.description!,
                  style: AppTextStyles.body2(AppColors.grey3),
                ),
              ],
            ],
          ),
        ),
        // Day tabs
        if (days.isNotEmpty) ...[
          TabBar(
            controller: _tabController,
            isScrollable: true,
            labelColor: AppColors.accent,
            unselectedLabelColor: AppColors.grey3,
            indicatorColor: AppColors.accent,
            tabAlignment: TabAlignment.start,
            tabs: days
                .map(
                  (day) => Tab(
                    text: l10n.programDay(day.dayNumber),
                  ),
                )
                .toList(),
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: days
                  .map((day) => _DayView(day: day))
                  .toList(),
            ),
          ),
        ] else
          Expanded(
            child: Center(
              child: Text(
                l10n.programEmpty,
                style: AppTextStyles.body1(AppColors.grey3),
              ),
            ),
          ),
      ],
    );
  }
}

class _DayView extends StatelessWidget {
  const _DayView({required this.day});
  final ProgramDay day;

  @override
  Widget build(BuildContext context) {
    final exercises = day.exercises;
    if (exercises.isEmpty) {
      return Center(
        child: Text(
          context.l10n.programEmpty,
          style: AppTextStyles.body1(AppColors.grey3),
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: exercises.length,
      itemBuilder: (ctx, i) {
        final ex = exercises[i];
        final parts = <String>[];
        if (ex.sets != null) parts.add('${ex.sets} sets');
        if (ex.reps != null) parts.add('${ex.reps} reps');
        if (ex.weight != null) {
          parts.add('${ex.weight!.toStringAsFixed(1)} kg');
        }

        return Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.bgCard,
            borderRadius: BorderRadius.circular(AppRadius.card),
            border: Border.all(color: AppColors.grey7),
          ),
          child: Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: AppColors.accent.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(AppRadius.input),
                ),
                child: Center(
                  child: Text(
                    '${i + 1}',
                    style: AppTextStyles.label(AppColors.accent),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      ex.exerciseName,
                      style: AppTextStyles.body1(AppColors.white),
                    ),
                    if (parts.isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        parts.join(' × '),
                        style: AppTextStyles.caption(AppColors.accent),
                      ),
                    ],
                    if (ex.restSeconds != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        'Repos: ${ex.restSeconds}s',
                        style: AppTextStyles.caption(AppColors.grey3),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
