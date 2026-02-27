import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../shared/models/slot.dart';

/// Grille des créneaux disponibles pour une date donnée.
class SlotGrid extends StatelessWidget {
  const SlotGrid({
    super.key,
    required this.slots,
    required this.onSlotTap,
  });

  final List<Slot> slots;
  final ValueChanged<Slot> onSlotTap;

  @override
  Widget build(BuildContext context) {
    if (slots.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(
            context.l10n.slotAvailable,
            style: AppTextStyles.body1(AppColors.grey3),
          ),
        ),
      );
    }
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 8,
        crossAxisSpacing: 8,
        childAspectRatio: 2.2,
      ),
      itemCount: slots.length,
      itemBuilder: (ctx, i) => _SlotCell(
        slot: slots[i],
        onTap: () => onSlotTap(slots[i]),
      ),
    );
  }
}

class _SlotCell extends StatelessWidget {
  const _SlotCell({required this.slot, required this.onTap});

  final Slot slot;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final timeFmt = DateFormat('HH:mm');
    final time = timeFmt.format(slot.startAt.toLocal());
    final (bgColor, textColor, canTap) = _style();

    return GestureDetector(
      onTap: canTap ? onTap : null,
      child: Container(
        decoration: BoxDecoration(
          color: bgColor.withOpacity(0.15),
          borderRadius: BorderRadius.circular(AppRadius.input),
          border: Border.all(color: bgColor, width: 1.5),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              time,
              style: AppTextStyles.label(textColor),
            ),
            const SizedBox(height: 2),
            Text(
              _statusLabel(context),
              style: AppTextStyles.caption(textColor.withOpacity(0.7)),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  (Color, Color, bool) _style() {
    switch (slot.status) {
      case 'available':
        return (AppColors.green, AppColors.green, true);
      case 'booked':
      case 'blocked':
        return (AppColors.red, AppColors.red, false);
      case 'mine':
        return (AppColors.yellow, AppColors.yellow, false);
      default:
        return (AppColors.grey5, AppColors.grey3, false);
    }
  }

  String _statusLabel(BuildContext context) {
    final l10n = context.l10n;
    switch (slot.status) {
      case 'available':
        return l10n.slotAvailable;
      case 'booked':
      case 'blocked':
        return l10n.slotBooked;
      case 'mine':
        return l10n.slotMine;
      default:
        return slot.status;
    }
  }
}
