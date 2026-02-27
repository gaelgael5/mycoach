import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../core/theme/app_theme.dart';

const _kNotifBookings  = 'notif_bookings';
const _kNotifMessages  = 'notif_messages';
const _kNotifPromos    = 'notif_promos';

/// Provider des préférences de notifications (clés locales).
final notifPrefsProvider =
    StateNotifierProvider<NotifPrefsNotifier, AsyncValue<Map<String, bool>>>(
  (ref) => NotifPrefsNotifier(ref.watch(flutterSecureStorageProvider)),
);

class NotifPrefsNotifier
    extends StateNotifier<AsyncValue<Map<String, bool>>> {
  NotifPrefsNotifier(this._storage) : super(const AsyncValue.loading()) {
    load();
  }

  final FlutterSecureStorage _storage;

  Future<void> load() async {
    try {
      final bookings = await _storage.read(key: _kNotifBookings);
      final messages = await _storage.read(key: _kNotifMessages);
      final promos   = await _storage.read(key: _kNotifPromos);
      state = AsyncValue.data({
        _kNotifBookings: bookings != 'false',
        _kNotifMessages: messages != 'false',
        _kNotifPromos:   promos   != 'false',
      });
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> toggle(String key, bool value) async {
    await _storage.write(key: key, value: value.toString());
    final current = Map<String, bool>.from(state.valueOrNull ?? {});
    current[key] = value;
    state = AsyncValue.data(current);
  }
}

/// Écran des préférences de notifications.
class NotificationPreferencesScreen extends ConsumerWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l       = context.l10n;
    final prefsAsync = ref.watch(notifPrefsProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.notifTitle),
      ),
      body: prefsAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) => Center(
          child: Text(l.errorGeneric,
              style: AppTextStyles.body1(AppColors.grey3)),
        ),
        data: (prefs) => SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l.notifTitle, style: AppTextStyles.label(AppColors.grey3)),
              const SizedBox(height: 8),
              Container(
                decoration: BoxDecoration(
                  color: AppColors.bgCard,
                  borderRadius: BorderRadius.circular(AppRadius.card),
                  border: Border.all(color: AppColors.grey7),
                ),
                child: Column(
                  children: [
                    _NotifToggle(
                      title:   l.notifBookings,
                      value:   prefs[_kNotifBookings] ?? true,
                      onChanged: (v) => ref
                          .read(notifPrefsProvider.notifier)
                          .toggle(_kNotifBookings, v),
                    ),
                    Divider(height: 1, color: AppColors.grey7),
                    _NotifToggle(
                      title:   l.notifMessages,
                      value:   prefs[_kNotifMessages] ?? true,
                      onChanged: (v) => ref
                          .read(notifPrefsProvider.notifier)
                          .toggle(_kNotifMessages, v),
                    ),
                    Divider(height: 1, color: AppColors.grey7),
                    _NotifToggle(
                      title:   l.notifPromos,
                      value:   prefs[_kNotifPromos] ?? true,
                      onChanged: (v) => ref
                          .read(notifPrefsProvider.notifier)
                          .toggle(_kNotifPromos, v),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Note : la configuration Firebase sera disponible en A6.',
                style: AppTextStyles.caption(AppColors.grey5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NotifToggle extends StatelessWidget {
  const _NotifToggle({
    required this.title,
    required this.value,
    required this.onChanged,
  });

  final String title;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return SwitchListTile(
      value: value,
      onChanged: onChanged,
      activeColor: AppColors.accent,
      title: Text(title, style: AppTextStyles.body1(AppColors.white)),
    );
  }
}
