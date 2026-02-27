import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../providers/booking_providers.dart';

class WaitlistScreen extends ConsumerWidget {
  const WaitlistScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final waitlistAsync = ref.watch(myWaitlistProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.waitlistTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: waitlistAsync.when(
        loading: () => const Center(
            child: CircularProgressIndicator(color: AppColors.accent)),
        error: (e, _) => Center(
          child: Text(l10n.errorGeneric,
              style: AppTextStyles.body1(AppColors.red)),
        ),
        data: (entries) {
          if (entries.isEmpty) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.hourglass_empty,
                      color: AppColors.grey5, size: 48),
                  const SizedBox(height: 16),
                  Text(l10n.waitlistTitle,
                      style: AppTextStyles.body1(AppColors.grey3)),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () => ref.refresh(myWaitlistProvider.future),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: entries.length,
              itemBuilder: (ctx, i) {
                final entry = entries[i];
                final dateFmt = DateFormat('d MMM yyyy HH:mm', 'fr_FR');
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
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              entry.coachName,
                              style:
                                  AppTextStyles.body1(AppColors.white),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              dateFmt.format(
                                  entry.slotStartAt.toLocal()),
                              style: AppTextStyles.caption(
                                  AppColors.grey3),
                            ),
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.yellow.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(
                                    AppRadius.pill),
                              ),
                              child: Text(
                                'Position #${entry.position}',
                                style: AppTextStyles.caption(
                                    AppColors.yellow),
                              ),
                            ),
                          ],
                        ),
                      ),
                      TextButton(
                        onPressed: () =>
                            _leaveWaitlist(context, ref, entry.id),
                        child: Text(
                          l10n.waitlistLeave,
                          style:
                              AppTextStyles.label(AppColors.red),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }

  Future<void> _leaveWaitlist(
      BuildContext context, WidgetRef ref, String entryId) async {
    await ref
        .read(bookingActionProvider.notifier)
        .leaveWaitlist(entryId);
    ref.invalidate(myWaitlistProvider);
  }
}
