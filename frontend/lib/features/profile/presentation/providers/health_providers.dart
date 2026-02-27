import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../shared/models/health_log.dart';
import '../../../../shared/models/health_parameter.dart';
import '../../domain/profile_service.dart';
import 'profile_providers.dart';

// ── Paramètres de santé ───────────────────────────────────────────────────────

final healthParametersProvider =
    FutureProvider<List<HealthParameter>>((ref) async {
  return ref.watch(profileServiceProvider).getHealthParameters();
});

// ── Logs de santé ─────────────────────────────────────────────────────────────

class HealthLogsNotifier
    extends StateNotifier<AsyncValue<Map<String, List<HealthLog>>>> {
  HealthLogsNotifier(this._service)
      : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;

  Future<void> load() async {
    try {
      final logs = await _service.getHealthLogs();
      final grouped = <String, List<HealthLog>>{};
      for (final log in logs) {
        grouped.putIfAbsent(log.parameterSlug, () => []).add(log);
      }
      state = AsyncValue.data(grouped);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> addLog({
    required String parameterId,
    required double value,
    DateTime? measuredAt,
  }) async {
    try {
      final log = await _service.addHealthLog(
        parameterId: parameterId,
        value:       value,
        measuredAt:  measuredAt,
      );
      final current = Map<String, List<HealthLog>>.from(
        state.valueOrNull ?? {},
      );
      current.putIfAbsent(log.parameterSlug, () => []).insert(0, log);
      state = AsyncValue.data(current);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> deleteLog(String id) async {
    try {
      await _service.deleteHealthLog(id);
      final current = Map<String, List<HealthLog>>.from(
        state.valueOrNull ?? {},
      );
      for (final key in current.keys) {
        current[key] = current[key]!.where((l) => l.id != id).toList();
      }
      state = AsyncValue.data(current);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final healthLogsNotifierProvider =
    StateNotifierProvider<HealthLogsNotifier, AsyncValue<Map<String, List<HealthLog>>>>(
  (ref) => HealthLogsNotifier(ref.watch(profileServiceProvider)),
);

// ── Partage santé ─────────────────────────────────────────────────────────────

class HealthSharingNotifier
    extends StateNotifier<AsyncValue<Map<String, dynamic>>> {
  HealthSharingNotifier(this._service, this._coachId)
      : super(const AsyncValue.loading()) {
    load();
  }

  final ProfileService _service;
  final String _coachId;

  Future<void> load() async {
    try {
      final data = await _service.getHealthSharing(_coachId);
      state = AsyncValue.data(data);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> toggleSharing(String parameterSlug, bool shared) async {
    try {
      final data = await _service.updateHealthSharing(
        coachId:       _coachId,
        parameterSlug: parameterSlug,
        shared:        shared,
      );
      state = AsyncValue.data(data);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

final healthSharingNotifierProvider = StateNotifierProvider.family<
    HealthSharingNotifier,
    AsyncValue<Map<String, dynamic>>,
    String>((ref, coachId) {
  return HealthSharingNotifier(ref.watch(profileServiceProvider), coachId);
});
