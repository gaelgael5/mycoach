import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/booking.dart';

/// Item de réservation dans la liste.
class BookingTile extends StatelessWidget {
  const BookingTile({
    super.key,
    required this.booking,
    this.onCancel,
  });

  final Booking booking;
  final VoidCallback? onCancel;

  @override
  Widget build(BuildContext context) {
    final dateFmt = DateFormat('EEE d MMM', 'fr_FR');
    final timeFmt = DateFormat('HH:mm', 'fr_FR');
    final l10n = context.l10n;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7, width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            // Date block
            Container(
              width: 52,
              padding: const EdgeInsets.symmetric(vertical: 8),
              decoration: BoxDecoration(
                color: AppColors.bgInput,
                borderRadius: BorderRadius.circular(AppRadius.input),
              ),
              child: Column(
                children: [
                  Text(
                    timeFmt.format(booking.startAt.toLocal()),
                    style: AppTextStyles.label(AppColors.accent),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    dateFmt.format(booking.startAt.toLocal()),
                    style: AppTextStyles.caption(AppColors.grey3),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    booking.coachName,
                    style: AppTextStyles.body1(AppColors.white),
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  _StatusChip(status: booking.status),
                ],
              ),
            ),
            if (onCancel != null && booking.status.isFuture)
              TextButton(
                onPressed: onCancel,
                child: Text(l10n.bookingCancel),
              ),
          ],
        ),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.status});
  final BookingStatus status;

  @override
  Widget build(BuildContext context) {
    final (label, color) = _getStyle(context);
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(AppRadius.pill),
      ),
      child: Text(
        label,
        style: AppTextStyles.caption(color),
      ),
    );
  }

  (String, Color) _getStyle(BuildContext context) {
    switch (status) {
      case BookingStatus.confirmed:
        return ('Confirmée', AppColors.green);
      case BookingStatus.pendingCoachValidation:
        return ('En attente', AppColors.yellow);
      case BookingStatus.done:
        return ('Terminée', AppColors.grey3);
      case BookingStatus.cancelledByClient:
      case BookingStatus.cancelledLateByClient:
        return ('Annulée', AppColors.red);
      case BookingStatus.cancelledByCoach:
      case BookingStatus.cancelledByCoachLate:
        return ('Annulée (coach)', AppColors.red);
      case BookingStatus.rejected:
      case BookingStatus.autoRejected:
        return ('Refusée', AppColors.red);
      case BookingStatus.noShowClient:
        return ('Absent', AppColors.red);
    }
  }
}
