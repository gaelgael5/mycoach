import 'package:equatable/equatable.dart';

/// Statuts possibles d'une séance (machine d'état §24).
enum BookingStatus {
  pendingCoachValidation,
  confirmed,
  done,
  rejected,
  autoRejected,
  cancelledByClient,
  cancelledLateByClient,
  cancelledByCoach,
  cancelledByCoachLate,
  noShowClient;

  static BookingStatus fromString(String s) => switch (s) {
    'pending_coach_validation'  => BookingStatus.pendingCoachValidation,
    'confirmed'                 => BookingStatus.confirmed,
    'done'                      => BookingStatus.done,
    'rejected'                  => BookingStatus.rejected,
    'auto_rejected'             => BookingStatus.autoRejected,
    'cancelled_by_client'       => BookingStatus.cancelledByClient,
    'cancelled_late_by_client'  => BookingStatus.cancelledLateByClient,
    'cancelled_by_coach'        => BookingStatus.cancelledByCoach,
    'cancelled_by_coach_late'   => BookingStatus.cancelledByCoachLate,
    'no_show_client'            => BookingStatus.noShowClient,
    _                           => BookingStatus.pendingCoachValidation,
  };

  String get value => switch (this) {
    BookingStatus.pendingCoachValidation  => 'pending_coach_validation',
    BookingStatus.confirmed               => 'confirmed',
    BookingStatus.done                    => 'done',
    BookingStatus.rejected                => 'rejected',
    BookingStatus.autoRejected            => 'auto_rejected',
    BookingStatus.cancelledByClient       => 'cancelled_by_client',
    BookingStatus.cancelledLateByClient   => 'cancelled_late_by_client',
    BookingStatus.cancelledByCoach        => 'cancelled_by_coach',
    BookingStatus.cancelledByCoachLate    => 'cancelled_by_coach_late',
    BookingStatus.noShowClient            => 'no_show_client',
  };

  bool get isFuture => this == BookingStatus.pendingCoachValidation
      || this == BookingStatus.confirmed;

  bool get isCancelled =>
      this == BookingStatus.cancelledByClient ||
      this == BookingStatus.cancelledLateByClient ||
      this == BookingStatus.cancelledByCoach ||
      this == BookingStatus.cancelledByCoachLate;
}

/// Type de séance.
enum BookingType {
  discovery,
  individual,
  group;

  static BookingType fromString(String s) => switch (s) {
    'discovery'  => BookingType.discovery,
    'group'      => BookingType.group,
    _            => BookingType.individual,
  };

  String get value => name;
}

/// Statut d'un créneau de disponibilité (vue calendrier client).
enum SlotStatus {
  available,    // 🟢 Libre
  lastPlace,    // 🟠 Dernière place
  full,         // 🔴 Complet (→ waitlist)
  booked,       // ⬛ Indisponible (autre client ou congé coach)
  mine,         // 🟡 Votre séance (pending ou confirmed)
  noCredits,    // 🔒 Pas de crédit
}

/// Une réservation / séance.
class Booking extends Equatable {
  const Booking({
    required this.id,
    required this.coachId,
    required this.coachName,
    required this.clientId,
    required this.startAt,
    required this.durationMin,
    required this.status,
    required this.type,
    this.gymId,
    this.gymName,
    this.disciplineSlug,
    this.clientMessage,
    this.coachNotes,
    this.priceCents,
    this.currency = 'EUR',
  });

  final String id;
  final String coachId;
  final String coachName;
  final String clientId;
  final DateTime startAt;
  final int durationMin;
  final BookingStatus status;
  final BookingType type;
  final String? gymId;
  final String? gymName;
  final String? disciplineSlug;
  final String? clientMessage;
  final String? coachNotes;

  /// Montant en centimes (null = à déterminer / gratuit pour discovery).
  final int? priceCents;
  final String currency;

  DateTime get endAt => startAt.add(Duration(minutes: durationMin));

  bool get isDiscovery => type == BookingType.discovery;

  factory Booking.fromJson(Map<String, dynamic> json) => Booking(
    id:             json['id'] as String,
    coachId:        json['coach_id'] as String,
    coachName:      json['coach_name'] as String? ?? '',
    clientId:       json['client_id'] as String,
    startAt:        DateTime.parse(json['start_at'] as String),
    durationMin:    json['duration_min'] as int,
    status:         BookingStatus.fromString(json['status'] as String),
    type:           BookingType.fromString(json['type'] as String? ?? 'individual'),
    gymId:          json['gym_id'] as String?,
    gymName:        json['gym_name'] as String?,
    disciplineSlug: json['discipline_slug'] as String?,
    clientMessage:  json['client_message'] as String?,
    coachNotes:     json['coach_notes'] as String?,
    priceCents:     json['price_cents'] as int?,
    currency:       json['currency'] as String? ?? 'EUR',
  );

  Map<String, dynamic> toJson() => {
    'id':              id,
    'coach_id':        coachId,
    'coach_name':      coachName,
    'client_id':       clientId,
    'start_at':        startAt.toUtc().toIso8601String(),
    'duration_min':    durationMin,
    'status':          status.value,
    'type':            type.value,
    if (gymId != null)          'gym_id':         gymId,
    if (gymName != null)        'gym_name':        gymName,
    if (disciplineSlug != null) 'discipline_slug': disciplineSlug,
    if (clientMessage != null)  'client_message':  clientMessage,
    if (priceCents != null)     'price_cents':     priceCents,
    'currency':        currency,
  };

  @override
  List<Object?> get props => [id, coachId, clientId, startAt, status, type];
}

/// Créneau de disponibilité retourné par `GET /coaches/{id}/availability`.
class AvailabilitySlot extends Equatable {
  const AvailabilitySlot({
    required this.startAt,
    required this.durationMin,
    required this.status,
    this.bookingId,
    this.bookingStatus,
    this.remainingSpots,
    this.totalSpots,
  });

  final DateTime startAt;
  final int durationMin;
  final SlotStatus status;

  /// ID de la réservation existante (si status = mine).
  final String? bookingId;

  /// Statut de la réservation si `status == mine`.
  final BookingStatus? bookingStatus;

  final int? remainingSpots;
  final int? totalSpots;

  DateTime get endAt => startAt.add(Duration(minutes: durationMin));

  /// `true` si le slot est réservable (clic possible).
  bool get isTappable =>
      status == SlotStatus.available || status == SlotStatus.lastPlace;

  /// `true` si redirige vers la liste d'attente.
  bool get isWaitlist => status == SlotStatus.full;

  factory AvailabilitySlot.fromJson(Map<String, dynamic> json) {
    final statusStr = json['status'] as String? ?? 'available';
    SlotStatus slotStatus;
    switch (statusStr) {
      case 'available':   slotStatus = SlotStatus.available; break;
      case 'last_place':  slotStatus = SlotStatus.lastPlace; break;
      case 'full':        slotStatus = SlotStatus.full; break;
      case 'booked':      slotStatus = SlotStatus.booked; break;
      case 'mine':        slotStatus = SlotStatus.mine; break;
      case 'no_credits':  slotStatus = SlotStatus.noCredits; break;
      default:            slotStatus = SlotStatus.booked;
    }
    return AvailabilitySlot(
      startAt:       DateTime.parse(json['start_at'] as String),
      durationMin:   json['duration_min'] as int,
      status:        slotStatus,
      bookingId:     json['booking_id'] as String?,
      bookingStatus: json['booking_status'] != null
          ? BookingStatus.fromString(json['booking_status'] as String)
          : null,
      remainingSpots:json['remaining_spots'] as int?,
      totalSpots:    json['total_spots'] as int?,
    );
  }

  @override
  List<Object?> get props => [startAt, durationMin, status, bookingId];
}
