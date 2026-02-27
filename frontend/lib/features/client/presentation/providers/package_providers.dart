import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/package.dart';
import '../../../../shared/models/payment.dart';
import '../../data/package_repository.dart';

// ── Repository ────────────────────────────────────────────────────────────────

final packageRepositoryProvider = Provider<PackageRepository>((ref) {
  return PackageRepository(ref.watch(dioProvider));
});

// ── Data ──────────────────────────────────────────────────────────────────────

final availablePackagesProvider =
    FutureProvider.autoDispose<List<Package>>((ref) async {
  final repo = ref.watch(packageRepositoryProvider);
  return repo.getAvailablePackages();
});

final myPackageBalanceProvider =
    FutureProvider.autoDispose<MyPackageBalance>((ref) async {
  final repo = ref.watch(packageRepositoryProvider);
  return repo.getMyBalance();
});

final paymentHistoryProvider =
    FutureProvider.autoDispose<List<Payment>>((ref) async {
  final repo = ref.watch(packageRepositoryProvider);
  final result = await repo.getPaymentHistory();
  return result.payments;
});

// ── Action Notifier ───────────────────────────────────────────────────────────

class PackageActionNotifier extends StateNotifier<AsyncValue<void>> {
  PackageActionNotifier(this._repo) : super(const AsyncValue.data(null));

  final PackageRepository _repo;

  Future<bool> purchasePackage({
    required String packageId,
    String paymentMethod = 'stripe',
  }) async {
    state = const AsyncValue.loading();
    try {
      await _repo.purchasePackage(
        packageId: packageId,
        paymentMethod: paymentMethod,
      );
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

final packageActionProvider =
    StateNotifierProvider.autoDispose<PackageActionNotifier, AsyncValue<void>>(
  (ref) => PackageActionNotifier(ref.watch(packageRepositoryProvider)),
);
