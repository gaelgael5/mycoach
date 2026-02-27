import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../shared/models/slot.dart';
import '../providers/coach_search_providers.dart';
import '../widgets/slot_grid.dart';

class BookingCalendarScreen extends ConsumerWidget {
  const BookingCalendarScreen({super.key, required this.coachId});

  final String coachId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final selectedDate = ref.watch(selectedDateProvider);
    final slotsAsync = ref.watch(
      slotAvailabilityProvider(
          CoachDateKey(coachId, selectedDate)),
    );

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.bookingCalTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: Column(
        children: [
          // Week horizontal date picker
          _WeekDatePicker(
            selectedDate: selectedDate,
            onDateSelected: (d) {
              ref.read(selectedDateProvider.notifier).state = d;
            },
          ),
          const Divider(color: AppColors.grey7, height: 1),
          // Slots
          Expanded(
            child: slotsAsync.when(
              loading: () => const Center(
                  child: CircularProgressIndicator(
                      color: AppColors.accent)),
              error: (e, _) => Center(
                child: Text(l10n.errorGeneric,
                    style: AppTextStyles.body1(AppColors.red)),
              ),
              data: (slots) {
                if (slots.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.calendar_today,
                            color: AppColors.grey5, size: 48),
                        const SizedBox(height: 16),
                        Text(
                          l10n.bookingSlotAvailable,
                          style: AppTextStyles.body1(AppColors.grey3),
                        ),
                      ],
                    ),
                  );
                }
                return SingleChildScrollView(
                  child: SlotGrid(
                    slots: slots,
                    onSlotTap: (slot) {
                      if (slot.isAvailable) {
                        context.go(
                          '${AppRoutes.coachSearch}/$coachId/book/confirm',
                          extra: slot,
                        );
                      }
                    },
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

class _WeekDatePicker extends StatelessWidget {
  const _WeekDatePicker({
    required this.selectedDate,
    required this.onDateSelected,
  });

  final DateTime selectedDate;
  final ValueChanged<DateTime> onDateSelected;

  @override
  Widget build(BuildContext context) {
    final dayFmt = DateFormat('EEE', 'fr_FR');
    final dayNumFmt = DateFormat('d');

    // Show 7 days starting from today
    final today = DateTime.now();
    final days = List.generate(14, (i) => today.add(Duration(days: i)));

    return SizedBox(
      height: 80,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        itemCount: days.length,
        itemBuilder: (ctx, i) {
          final day = days[i];
          final isSelected = day.year == selectedDate.year &&
              day.month == selectedDate.month &&
              day.day == selectedDate.day;

          return GestureDetector(
            onTap: () => onDateSelected(day),
            child: Container(
              width: 52,
              margin: const EdgeInsets.only(right: 8),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.accent
                    : AppColors.bgCard,
                borderRadius: BorderRadius.circular(AppRadius.input),
                border: Border.all(
                    color: isSelected
                        ? AppColors.accent
                        : AppColors.grey7),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    dayFmt.format(day),
                    style: AppTextStyles.caption(isSelected
                        ? AppColors.white
                        : AppColors.grey3),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    dayNumFmt.format(day),
                    style: AppTextStyles.label(isSelected
                        ? AppColors.white
                        : AppColors.white),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
