import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../providers/package_providers.dart';

class PaymentHistoryScreen extends ConsumerWidget {
  const PaymentHistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final paymentsAsync = ref.watch(paymentHistoryProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.paymentsTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: paymentsAsync.when(
        loading: () => const Center(
            child: CircularProgressIndicator(color: AppColors.accent)),
        error: (e, _) => Center(
          child: Text(l10n.errorGeneric,
              style: AppTextStyles.body1(AppColors.red)),
        ),
        data: (payments) {
          if (payments.isEmpty) {
            return Center(
              child: Text(l10n.paymentsTitle,
                  style: AppTextStyles.body1(AppColors.grey3)),
            );
          }
          final dateFmt = DateFormat('d MMM yyyy', 'fr_FR');
          return RefreshIndicator(
            onRefresh: () =>
                ref.refresh(paymentHistoryProvider.future),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: payments.length,
              separatorBuilder: (_, __) =>
                  const SizedBox(height: 8),
              itemBuilder: (ctx, i) {
                final p = payments[i];
                final (statusLabel, statusColor) =
                    _statusStyle(context, p.status);
                return Container(
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
                            if (p.description != null)
                              Text(
                                p.description!,
                                style: AppTextStyles.body1(AppColors.white),
                              ),
                            const SizedBox(height: 4),
                            Text(
                              dateFmt.format(p.createdAt.toLocal()),
                              style:
                                  AppTextStyles.caption(AppColors.grey3),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            '${p.amountEur.toStringAsFixed(2)}€',
                            style:
                                AppTextStyles.headline4(AppColors.white),
                          ),
                          const SizedBox(height: 4),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: statusColor.withOpacity(0.15),
                              borderRadius:
                                  BorderRadius.circular(AppRadius.pill),
                            ),
                            child: Text(
                              statusLabel,
                              style: AppTextStyles.caption(statusColor),
                            ),
                          ),
                        ],
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

  (String, Color) _statusStyle(BuildContext context, String status) {
    final l10n = context.l10n;
    switch (status) {
      case 'pending':
        return (l10n.paymentStatusPending, AppColors.yellow);
      case 'completed':
        return (l10n.paymentStatusCompleted, AppColors.green);
      case 'failed':
        return (l10n.paymentStatusFailed, AppColors.red);
      case 'refunded':
        return (l10n.paymentStatusRefunded, AppColors.grey3);
      default:
        return (status, AppColors.grey3);
    }
  }
}
