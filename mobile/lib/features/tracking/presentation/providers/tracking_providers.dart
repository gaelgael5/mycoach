import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/tracking.dart';
import '../../data/tracking_repository.dart';

final trackingRepositoryProvider = Provider<TrackingRepository>((ref) {
  return TrackingRepository(ref.watch(apiClientProvider));
});

final trackingProvider = FutureProvider<List<SessionCompletion>>((ref) async {
  return ref.watch(trackingRepositoryProvider).getCompletions();
});

final metricsProvider = FutureProvider<List<Metric>>((ref) async {
  return ref.watch(trackingRepositoryProvider).getMetrics();
});
