import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/booking.dart';
import '../../../../shared/models/program.dart';
import '../../data/booking_repository.dart';

// ── Repository ────────────────────────────────────────────────────────────────

final bookingRepositoryProvider = Provider<BookingRepository>((ref) {
  return BookingRepository(ref.watch(dioProvider));
});

// ── My Bookings ───────────────────────────────────────────────────────────────

/// Filtre actif pour la liste des réservations : "upcoming" | "past" | "cancelled"
final bookingFilterProvider =
    StateProvider.autoDispose<String>((ref) => 'upcoming');

final myBookingsProvider =
    FutureProvider.autoDispose<List<Booking>>((ref) async {
  final filter = ref.watch(bookingFilterProvider);
  final repo = ref.watch(bookingRepositoryProvider);

  String? statusFilter;
  switch (filter) {
    case 'upcoming':
      statusFilter = 'upcoming';
    case 'past':
      statusFilter = 'past';
    case 'cancelled':
      statusFilter = 'cancelled';
    default:
      statusFilter = null;
  }

  final result = await repo.getMyBookings(status: statusFilter);
  return result.bookings;
});

// ── Waitlist ──────────────────────────────────────────────────────────────────

final myWaitlistProvider =
    FutureProvider.autoDispose<List<WaitlistEntry>>((ref) async {
  final repo = ref.watch(bookingRepositoryProvider);
  return repo.getMyWaitlist();
});

// ── Agenda ────────────────────────────────────────────────────────────────────

final agendaWeekProvider =
    StateProvider.autoDispose<DateTime>((ref) => DateTime.now());

final agendaEventsProvider =
    FutureProvider.autoDispose<List<AgendaEvent>>((ref) async {
  final week = ref.watch(agendaWeekProvider);
  final repo = ref.watch(bookingRepositoryProvider);
  final start = week.subtract(Duration(days: week.weekday - 1));
  final end = start.add(const Duration(days: 6));
  return repo.getAgenda(start: start, end: end);
});

// ── Action Notifier ───────────────────────────────────────────────────────────

class BookingActionNotifier extends StateNotifier<AsyncValue<void>> {
  BookingActionNotifier(this._repo) : super(const AsyncValue.data(null));

  final BookingRepository _repo;

  Future<Booking?> createBooking({
    required String slotId,
    required String bookingType,
    String? notes,
  }) async {
    state = const AsyncValue.loading();
    try {
      final booking = await _repo.createBooking(
        slotId: slotId,
        bookingType: bookingType,
        notes: notes,
      );
      state = const AsyncValue.data(null);
      return booking;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return null;
    }
  }

  Future<bool> cancelBooking(String id) async {
    state = const AsyncValue.loading();
    try {
      await _repo.cancelBooking(id);
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  Future<bool> leaveWaitlist(String entryId) async {
    state = const AsyncValue.loading();
    try {
      await _repo.leaveWaitlist(entryId);
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  void reset() => state = const AsyncValue.data(null);
}

final bookingActionProvider =
    StateNotifierProvider.autoDispose<BookingActionNotifier, AsyncValue<void>>(
  (ref) => BookingActionNotifier(ref.watch(bookingRepositoryProvider)),
);
