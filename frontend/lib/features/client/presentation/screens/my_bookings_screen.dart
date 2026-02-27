import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../providers/booking_providers.dart';
import '../widgets/booking_tile.dart';

class MyBookingsScreen extends ConsumerWidget {
  const MyBookingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final filter = ref.watch(bookingFilterProvider);
    final bookingsAsync = ref.watch(myBookingsProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.myBookingsTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: Column(
        children: [
          // Filter tabs
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  _Tab(
                    label: l10n.myBookingsUpcoming,
                    selected: filter == 'upcoming',
                    onTap: () => ref
                        .read(bookingFilterProvider.notifier)
                        .state = 'upcoming',
                  ),
                  const SizedBox(width: 8),
                  _Tab(
                    label: l10n.myBookingsPast,
                    selected: filter == 'past',
                    onTap: () => ref
                        .read(bookingFilterProvider.notifier)
                        .state = 'past',
                  ),
                  const SizedBox(width: 8),
                  _Tab(
                    label: l10n.myBookingsCancelled,
                    selected: filter == 'cancelled',
                    onTap: () => ref
                        .read(bookingFilterProvider.notifier)
                        .state = 'cancelled',
                  ),
                ],
              ),
            ),
          ),
          const Divider(color: AppColors.grey7, height: 1),
          // List
          Expanded(
            child: bookingsAsync.when(
              loading: () => const Center(
                  child: CircularProgressIndicator(
                      color: AppColors.accent)),
              error: (e, _) => Center(
                child: Text(l10n.errorGeneric,
                    style: AppTextStyles.body1(AppColors.red)),
              ),
              data: (bookings) {
                if (bookings.isEmpty) {
                  return Center(
                    child: Text(
                      l10n.myBookingsTitle,
                      style: AppTextStyles.body1(AppColors.grey3),
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () =>
                      ref.refresh(myBookingsProvider.future),
                  child: ListView.builder(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: bookings.length,
                    itemBuilder: (ctx, i) {
                      final booking = bookings[i];
                      return BookingTile(
                        booking: booking,
                        onCancel: booking.status.isFuture
                            ? () => _showCancelDialog(
                                context, ref, booking.id)
                            : null,
                      );
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

  Future<void> _showCancelDialog(
      BuildContext context, WidgetRef ref, String bookingId) async {
    final l10n = context.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.bgCard,
        title: Text(l10n.bookingCancel,
            style: AppTextStyles.headline4(AppColors.white)),
        content: Text(l10n.bookingCancelConfirm,
            style: AppTextStyles.body1(AppColors.grey3)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.btnCancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.red),
            child: Text(l10n.bookingCancel),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref
          .read(bookingActionProvider.notifier)
          .cancelBooking(bookingId);
      ref.invalidate(myBookingsProvider);
    }
  }
}

class _Tab extends StatelessWidget {
  const _Tab({
    required this.label,
    required this.selected,
    required this.onTap,
  });
  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.accent.withOpacity(0.15)
              : AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          border: Border.all(
              color: selected ? AppColors.accent : AppColors.grey7),
        ),
        child: Text(
          label,
          style: AppTextStyles.label(
              selected ? AppColors.accent : AppColors.grey3),
        ),
      ),
    );
  }
}
