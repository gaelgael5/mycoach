import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/package.dart';
import '../providers/package_providers.dart';
import '../widgets/package_card.dart';

class PackagesScreen extends ConsumerWidget {
  const PackagesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = context.l10n;
    final balanceAsync = ref.watch(myPackageBalanceProvider);
    final packagesAsync = ref.watch(availablePackagesProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.packagesTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(myPackageBalanceProvider);
          ref.invalidate(availablePackagesProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Balance card
              balanceAsync.when(
                loading: () => const Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(
                      color: AppColors.accent),
                ),
                error: (_, __) => const SizedBox.shrink(),
                data: (balance) => _BalanceCard(balance: balance),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 8),
                child: Text(
                  l10n.packagesTitle,
                  style: AppTextStyles.headline4(AppColors.white),
                ),
              ),
              // Available packages
              packagesAsync.when(
                loading: () => const Center(
                    child: CircularProgressIndicator(
                        color: AppColors.accent)),
                error: (e, _) => Padding(
                  padding: const EdgeInsets.all(16),
                  child: Text(l10n.errorGeneric,
                      style: AppTextStyles.body1(AppColors.red)),
                ),
                data: (packages) {
                  if (packages.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(20),
                      child: Text(l10n.packagesTitle,
                          style: AppTextStyles.body1(AppColors.grey3)),
                    );
                  }
                  return Column(
                    children: packages
                        .map(
                          (p) => PackageCard(
                            package: p,
                            onBuy: () =>
                                _showBuyDialog(context, ref, p.id, p.name,
                                    p.priceEur),
                          ),
                        )
                        .toList(),
                  );
                },
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _showBuyDialog(
    BuildContext context,
    WidgetRef ref,
    String packageId,
    String packageName,
    double priceEur,
  ) async {
    final l10n = context.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.bgCard,
        title: Text(l10n.packagesTitle,
            style: AppTextStyles.headline4(AppColors.white)),
        content: Text(
          l10n.packagesBuyConfirm(packageName, priceEur.toStringAsFixed(2)),
          style: AppTextStyles.body1(AppColors.grey3),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(l10n.btnCancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(l10n.packagesBuy),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref
          .read(packageActionProvider.notifier)
          .purchasePackage(packageId: packageId);
      ref.invalidate(myPackageBalanceProvider);
    }
  }
}

class _BalanceCard extends StatelessWidget {
  const _BalanceCard({required this.balance});
  final MyPackageBalance balance;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppGradients.accentButton,
        borderRadius: BorderRadius.circular(AppRadius.card),
        boxShadow: AppShadows.accent,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            l10n.packagesBalance(balance.sessionsRemaining),
            style: AppTextStyles.headline3(AppColors.white),
          ),
          if (balance.expiresAt != null) ...[
            const SizedBox(height: 4),
            Text(
              l10n.packagesExpires(
                  DateFormat('d MMM yyyy', 'fr_FR')
                      .format(balance.expiresAt!.toLocal())),
              style: AppTextStyles.body2(AppColors.white.withOpacity(0.8)),
            ),
          ],
        ],
      ),
    );
  }
}
