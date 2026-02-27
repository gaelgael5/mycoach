import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/program.dart';
import '../providers/booking_providers.dart';

class ClientAgendaScreen extends ConsumerWidget {
  const ClientAgendaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final week = ref.watch(agendaWeekProvider);
    final eventsAsync = ref.watch(agendaEventsProvider);

    // Week start (Monday)
    final weekStart = week.subtract(Duration(days: week.weekday - 1));

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.agendaTitle),
        backgroundColor: AppColors.bgDark,
        actions: [
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: () {
              ref.read(agendaWeekProvider.notifier).state =
                  week.subtract(const Duration(days: 7));
            },
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: () {
              ref.read(agendaWeekProvider.notifier).state =
                  week.add(const Duration(days: 7));
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Week header
          _WeekHeader(weekStart: weekStart),
          const Divider(color: AppColors.grey7, height: 1),
          // Events
          Expanded(
            child: eventsAsync.when(
              loading: () => const Center(
                  child: CircularProgressIndicator(
                      color: AppColors.accent)),
              error: (e, _) => Center(
                child: Text(l10n.errorGeneric,
                    style: AppTextStyles.body1(AppColors.red)),
              ),
              data: (events) {
                if (events.isEmpty) {
                  return Center(
                    child: Text(l10n.agendaTitle,
                        style: AppTextStyles.body1(AppColors.grey3)),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () =>
                      ref.refresh(agendaEventsProvider.future),
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      for (var i = 0; i < 7; i++) ...[
                        _DaySection(
                          date: weekStart.add(Duration(days: i)),
                          events: events
                              .where((e) =>
                                  e.startAt.toLocal().year ==
                                      weekStart
                                          .add(Duration(days: i))
                                          .year &&
                                  e.startAt.toLocal().month ==
                                      weekStart
                                          .add(Duration(days: i))
                                          .month &&
                                  e.startAt.toLocal().day ==
                                      weekStart
                                          .add(Duration(days: i))
                                          .day)
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _WeekHeader extends StatelessWidget {
  const _WeekHeader({required this.weekStart});
  final DateTime weekStart;

  @override
  Widget build(BuildContext context) {
    final dayFmt = DateFormat('EEE\nd', 'fr_FR');
    return Row(
      children: List.generate(7, (i) {
        final day = weekStart.add(Duration(days: i));
        final isToday = day.year == DateTime.now().year &&
            day.month == DateTime.now().month &&
            day.day == DateTime.now().day;
        return Expanded(
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                    color: isToday ? AppColors.accent : Colors.transparent,
                    width: 2),
              ),
            ),
            child: Text(
              dayFmt.format(day),
              style: AppTextStyles.caption(
                  isToday ? AppColors.accent : AppColors.grey3),
              textAlign: TextAlign.center,
            ),
          ),
        );
      }),
    );
  }
}

class _DaySection extends StatelessWidget {
  const _DaySection({required this.date, required this.events});
  final DateTime date;
  final List<AgendaEvent> events;

  @override
  Widget build(BuildContext context) {
    if (events.isEmpty) return const SizedBox.shrink();
    final dayFmt = DateFormat('EEEE d MMMM', 'fr_FR');
    final timeFmt = DateFormat('HH:mm');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Text(
            dayFmt.format(date),
            style: AppTextStyles.label(AppColors.grey3),
          ),
        ),
        for (final event in events)
          Container(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: event.isConfirmed
                  ? AppColors.greenSurface
                  : AppColors.yellowSurface,
              borderRadius: BorderRadius.circular(AppRadius.input),
              border: Border.all(
                  color: event.isConfirmed
                      ? AppColors.green
                      : AppColors.yellow),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        event.title,
                        style: AppTextStyles.body1(AppColors.white),
                      ),
                      if (event.coachName != null)
                        Text(
                          event.coachName!,
                          style: AppTextStyles.caption(AppColors.grey3),
                        ),
                    ],
                  ),
                ),
                Text(
                  timeFmt.format(event.startAt.toLocal()),
                  style: AppTextStyles.label(
                      event.isConfirmed
                          ? AppColors.green
                          : AppColors.yellow),
                ),
              ],
            ),
          ),
        const Divider(color: AppColors.grey7),
      ],
    );
  }
}
