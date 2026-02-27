import 'package:dio/dio.dart';
import '../../../shared/models/booking.dart';
import '../../../shared/models/program.dart';

class BookingRepository {
  const BookingRepository(this._dio);

  final Dio _dio;

  Future<Booking> createBooking({
    required String slotId,
    required String bookingType,
    String? notes,
  }) async {
    final body = <String, dynamic>{
      'slot_id': slotId,
      'booking_type': bookingType,
      if (notes != null && notes.isNotEmpty) 'notes': notes,
    };
    final resp = await _dio.post<Map<String, dynamic>>(
      '/bookings',
      data: body,
    );
    return Booking.fromJson(resp.data!);
  }

  Future<({List<Booking> bookings, int total, int page})> getMyBookings({
    String? status,
    int page = 1,
    int limit = 20,
  }) async {
    final params = <String, dynamic>{'page': page, 'limit': limit};
    if (status != null && status.isNotEmpty) params['status'] = status;

    final resp = await _dio.get<Map<String, dynamic>>(
      '/bookings/me',
      queryParameters: params,
    );
    final data = resp.data!;
    final bookings = (data['bookings'] as List<dynamic>)
        .map((e) => Booking.fromJson(e as Map<String, dynamic>))
        .toList();
    return (
      bookings: bookings,
      total: data['total'] as int? ?? bookings.length,
      page: data['page'] as int? ?? page,
    );
  }

  Future<Booking> getBooking(String id) async {
    final resp = await _dio.get<Map<String, dynamic>>('/bookings/$id');
    return Booking.fromJson(resp.data!);
  }

  Future<void> cancelBooking(String id) async {
    await _dio.delete('/bookings/$id');
  }

  Future<WaitlistEntry> joinWaitlist(String bookingId) async {
    final resp = await _dio.post<Map<String, dynamic>>(
      '/bookings/$bookingId/waitlist',
    );
    return WaitlistEntry.fromJson(resp.data!);
  }

  Future<List<WaitlistEntry>> getMyWaitlist() async {
    final resp = await _dio.get<List<dynamic>>('/bookings/waitlist/me');
    return (resp.data ?? [])
        .map((e) => WaitlistEntry.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> leaveWaitlist(String entryId) async {
    await _dio.delete('/bookings/waitlist/$entryId');
  }

  Future<List<AgendaEvent>> getAgenda({
    required DateTime start,
    required DateTime end,
  }) async {
    final fmt = (DateTime d) =>
        '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
    final resp = await _dio.get<Map<String, dynamic>>(
      '/agenda/me',
      queryParameters: {
        'start': fmt(start),
        'end': fmt(end),
      },
    );
    final data = resp.data!;
    return (data['events'] as List<dynamic>)
        .map((e) => AgendaEvent.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
