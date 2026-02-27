import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../shared/models/slot.dart';
import '../providers/booking_providers.dart';
import '../providers/coach_search_providers.dart';

class BookingConfirmScreen extends ConsumerStatefulWidget {
  const BookingConfirmScreen({
    super.key,
    required this.coachId,
    required this.slot,
  });

  final String coachId;
  final Slot slot;

  @override
  ConsumerState<BookingConfirmScreen> createState() =>
      _BookingConfirmScreenState();
}

class _BookingConfirmScreenState
    extends ConsumerState<BookingConfirmScreen> {
  String _bookingType = 'standard';
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    final actionState = ref.watch(bookingActionProvider);
    final profileAsync = ref.watch(coachProfileProvider(widget.coachId));
    final dateFmt = DateFormat('EEE d MMM yyyy', 'fr_FR');
    final timeFmt = DateFormat('HH:mm');
    final startLocal = widget.slot.startAt.toLocal();
    final endLocal = widget.slot.endAt.toLocal();

    final coachName = profileAsync.valueOrNull?.fullName ?? '';

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(l10n.bookingConfirmTitle),
        backgroundColor: AppColors.bgDark,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Summary card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.bgCard,
                borderRadius: BorderRadius.circular(AppRadius.card),
                border: Border.all(color: AppColors.grey7),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _Row(label: l10n.bookingConfirmCoach, value: coachName),
                  const SizedBox(height: 8),
                  _Row(
                    label: l10n.bookingConfirmDate,
                    value: dateFmt.format(startLocal),
                  ),
                  const SizedBox(height: 8),
                  _Row(
                    label: l10n.bookingConfirmTime,
                    value:
                        '${timeFmt.format(startLocal)} → ${timeFmt.format(endLocal)}',
                  ),
                  if (widget.slot.priceCents != null) ...[
                    const SizedBox(height: 8),
                    _Row(
                      label: l10n.bookingConfirmRate,
                      value:
                          '${(widget.slot.priceCents! / 100).toStringAsFixed(2)}€',
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 20),
            // Booking type
            Text(l10n.bookingConfirmTitle,
                style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _TypeButton(
                    label: l10n.bookingConfirmStandard,
                    selected: _bookingType == 'standard',
                    onTap: () =>
                        setState(() => _bookingType = 'standard'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _TypeButton(
                    label: l10n.bookingConfirmDiscovery,
                    selected: _bookingType == 'discovery',
                    onTap: () =>
                        setState(() => _bookingType = 'discovery'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            // Notes
            TextField(
              controller: _notesController,
              style: AppTextStyles.body1(AppColors.white),
              maxLines: 3,
              decoration: InputDecoration(
                hintText: l10n.bookingConfirmMessagePlaceholder,
                labelText: l10n.labelOptional,
              ),
            ),
            const SizedBox(height: 24),
            // Error (no credits)
            if (actionState is AsyncError) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(AppRadius.card),
                  border: Border.all(color: AppColors.red),
                ),
                child: Column(
                  children: [
                    Text(l10n.bookingNoCredits,
                        style: AppTextStyles.body1(AppColors.red)),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () =>
                          context.go(AppRoutes.packages),
                      child: Text(l10n.bookingNoCreditsAction),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],
            // Confirm button
            ElevatedButton(
              onPressed: actionState is AsyncLoading
                  ? null
                  : () => _confirm(context, ref),
              child: actionState is AsyncLoading
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(
                          color: AppColors.white, strokeWidth: 2),
                    )
                  : Text(l10n.bookingConfirmButton),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _confirm(BuildContext context, WidgetRef ref) async {
    final booking = await ref.read(bookingActionProvider.notifier).createBooking(
          slotId: widget.slot.id,
          bookingType: _bookingType,
          notes: _notesController.text.trim(),
        );
    if (!mounted) return;
    if (booking != null) {
      context.go(AppRoutes.clientAgenda);
    }
  }
}

class _Row extends StatelessWidget {
  const _Row({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 80,
          child: Text(label, style: AppTextStyles.caption(AppColors.grey3)),
        ),
        Expanded(
          child: Text(value, style: AppTextStyles.body1(AppColors.white)),
        ),
      ],
    );
  }
}

class _TypeButton extends StatelessWidget {
  const _TypeButton({
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
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.accent.withOpacity(0.15)
              : AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.input),
          border: Border.all(
              color: selected ? AppColors.accent : AppColors.grey7,
              width: selected ? 1.5 : 1),
        ),
        child: Center(
          child: Text(
            label,
            style: AppTextStyles.label(
                selected ? AppColors.accent : AppColors.grey3),
          ),
        ),
      ),
    );
  }
}
