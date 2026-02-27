// ignore_for_file: prefer_const_constructors
import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach/shared/models/user.dart';
import 'package:mycoach/shared/models/gym.dart';
import 'package:mycoach/shared/models/booking.dart';
import 'package:mycoach/shared/models/workout.dart';
import 'package:mycoach/shared/models/social_link.dart';

void main() {
  // ── User ──────────────────────────────────────────────────────────────────
  group('User', () {
    final json = {
      'id': 'uuid-123',
      'email': 'marie@example.com',
      'role': 'client',
      'first_name': 'Marie',
      'last_name': 'Dupont',
      'phone': null,
      'phone_verified_at': null,
      'gender': 'female',
      'birth_year': 1990,
      'avatar_url': null,
      'resolved_avatar_url': '/static/avatars/default_female.svg',
      'locale': 'fr-FR',
      'timezone': 'Europe/Paris',
      'country': 'FR',
      'is_active': true,
      'created_at': '2026-02-27T10:00:00Z',
    };

    test('fromJson parses correctly', () {
      final user = User.fromJson(json);
      expect(user.id, 'uuid-123');
      expect(user.email, 'marie@example.com');
      expect(user.role, UserRole.client);
      expect(user.firstName, 'Marie');
      expect(user.lastName, 'Dupont');
      expect(user.gender, Gender.female);
      expect(user.birthYear, 1990);
      expect(user.locale, 'fr-FR');
      expect(user.country, 'FR');
      expect(user.isActive, true);
      expect(user.isPhoneVerified, false);
      expect(user.fullName, 'Marie Dupont');
    });

    test('coach role detection', () {
      final coach = User.fromJson({...json, 'role': 'coach', 'id': 'c1'});
      expect(coach.role.isCoach, true);
      expect(coach.role.isAdmin, false);
    });

    test('admin role has all access', () {
      final admin = User.fromJson({...json, 'role': 'admin', 'id': 'a1'});
      expect(admin.role.isCoach, true);
      expect(admin.role.isAdmin, true);
    });

    test('unknown role defaults to client', () {
      expect(UserRole.fromString('unknown'), UserRole.client);
      expect(UserRole.fromString(''), UserRole.client);
    });

    test('toJson roundtrip', () {
      final user = User.fromJson(json);
      final back = User.fromJson(user.toJson());
      expect(back, user);
    });

    test('copyWith updates only specified fields', () {
      final user = User.fromJson(json);
      final updated = user.copyWith(firstName: 'Sophie');
      expect(updated.firstName, 'Sophie');
      expect(updated.lastName, 'Dupont'); // inchangé
      expect(updated.email, user.email);
    });
  });

  // ── Gender ────────────────────────────────────────────────────────────────
  group('Gender', () {
    test('parses all values', () {
      expect(Gender.fromString('male'),   Gender.male);
      expect(Gender.fromString('female'), Gender.female);
      expect(Gender.fromString('other'),  Gender.other);
      expect(Gender.fromString(null),     null);
      expect(Gender.fromString('unknown'),null);
    });

    test('value roundtrip', () {
      for (final g in Gender.values) {
        expect(Gender.fromString(g.value), g);
      }
    });
  });

  // ── Gym ───────────────────────────────────────────────────────────────────
  group('Gym', () {
    final gymJson = {
      'id': 'gym-1',
      'name': 'Fitness Park Bondy',
      'brand': 'fitness_park',
      'address': '12 rue de la République',
      'city': 'Bondy',
      'postal_code': '93140',
      'country': 'FR',
      'coaches_count': 8,
      'is_favorite': true,
    };

    test('fromJson parses correctly', () {
      final gym = Gym.fromJson(gymJson);
      expect(gym.id, 'gym-1');
      expect(gym.brandLabel, 'Fitness Park');
      expect(gym.isFavorite, true);
      expect(gym.coachesCount, 8);
      expect(gym.shortAddress, '12 rue de la République, 93140 Bondy');
    });

    test('unknown brand returns slug as-is', () {
      final gym = Gym.fromJson({...gymJson, 'brand': 'custom_brand', 'id': 'g2'});
      expect(gym.brandLabel, 'custom_brand');
    });

    test('copyWith toggles favorite', () {
      final gym = Gym.fromJson(gymJson);
      final toggled = gym.copyWith(isFavorite: false);
      expect(toggled.isFavorite, false);
      expect(toggled.name, gym.name); // inchangé
    });

    test('all known brands have human labels', () {
      const brands = ['fitness_park','basic_fit','cmg','neoness','keep_cool',
        'orange_bleue','cercle','episod','magic_form'];
      for (final brand in brands) {
        final gym = Gym.fromJson({...gymJson, 'brand': brand, 'id': brand});
        expect(gym.brandLabel, isNot(equals(brand)),
            reason: '$brand should have a human label');
      }
    });
  });

  // ── BookingStatus ─────────────────────────────────────────────────────────
  group('BookingStatus', () {
    test('fromString parses all statuses', () {
      const pairs = {
        'pending_coach_validation': BookingStatus.pendingCoachValidation,
        'confirmed':                BookingStatus.confirmed,
        'done':                     BookingStatus.done,
        'rejected':                 BookingStatus.rejected,
        'auto_rejected':            BookingStatus.autoRejected,
        'cancelled_by_client':      BookingStatus.cancelledByClient,
        'cancelled_late_by_client': BookingStatus.cancelledLateByClient,
        'cancelled_by_coach':       BookingStatus.cancelledByCoach,
        'cancelled_by_coach_late':  BookingStatus.cancelledByCoachLate,
        'no_show_client':           BookingStatus.noShowClient,
      };
      pairs.forEach((k, v) => expect(BookingStatus.fromString(k), v));
    });

    test('isFuture is true for pending and confirmed only', () {
      expect(BookingStatus.pendingCoachValidation.isFuture, true);
      expect(BookingStatus.confirmed.isFuture, true);
      expect(BookingStatus.done.isFuture, false);
      expect(BookingStatus.cancelledByClient.isFuture, false);
    });

    test('isCancelled covers all cancel statuses', () {
      expect(BookingStatus.cancelledByClient.isCancelled, true);
      expect(BookingStatus.cancelledByCoach.isCancelled, true);
      expect(BookingStatus.confirmed.isCancelled, false);
    });
  });

  // ── ExerciseSet ───────────────────────────────────────────────────────────
  group('ExerciseSet', () {
    test('volume = reps × weightKg', () {
      const s = ExerciseSet(setNumber: 1, reps: 10, weightKg: 80);
      expect(s.volume, 800.0);
    });

    test('fromJson / toJson roundtrip', () {
      final json = {'set_number': 2, 'reps': 12, 'weight_kg': 60.0, 'is_done': true, 'is_pr': false};
      final s = ExerciseSet.fromJson(json);
      expect(s.reps, 12);
      expect(s.weightKg, 60.0);
      expect(s.isDone, true);
      expect(s.isPr, false);
      final back = ExerciseSet.fromJson(s.toJson());
      expect(back, s);
    });

    test('copyWith only changes specified fields', () {
      const s = ExerciseSet(setNumber: 1, reps: 10, weightKg: 80);
      final updated = s.copyWith(reps: 12);
      expect(updated.reps, 12);
      expect(updated.weightKg, 80.0);
    });
  });

  // ── WorkoutExercise ───────────────────────────────────────────────────────
  group('WorkoutExercise', () {
    test('totalVolume sums all sets', () {
      const ex = WorkoutExercise(
        id: 'e1',
        name: 'Développé couché',
        sets: [
          ExerciseSet(setNumber: 1, reps: 10, weightKg: 80),
          ExerciseSet(setNumber: 2, reps: 10, weightKg: 82.5),
          ExerciseSet(setNumber: 3, reps: 8, weightKg: 85),
        ],
      );
      expect(ex.totalVolume, 800.0 + 825.0 + 680.0);
    });

    test('bestSet returns highest weight', () {
      const ex = WorkoutExercise(
        id: 'e2',
        name: 'Squat',
        sets: [
          ExerciseSet(setNumber: 1, reps: 5, weightKg: 100),
          ExerciseSet(setNumber: 2, reps: 5, weightKg: 120),
          ExerciseSet(setNumber: 3, reps: 3, weightKg: 110),
        ],
      );
      expect(ex.bestSet?.weightKg, 120.0);
    });

    test('completedSets counts done sets', () {
      const ex = WorkoutExercise(
        id: 'e3',
        name: 'Tirage',
        sets: [
          ExerciseSet(setNumber: 1, reps: 12, weightKg: 60, isDone: true),
          ExerciseSet(setNumber: 2, reps: 12, weightKg: 60, isDone: true),
          ExerciseSet(setNumber: 3, reps: 10, weightKg: 60, isDone: false),
        ],
      );
      expect(ex.completedSets, 2);
    });
  });

  // ── WorkoutFeeling ────────────────────────────────────────────────────────
  group('WorkoutFeeling', () {
    test('fromInt returns correct feeling', () {
      expect(WorkoutFeeling.fromInt(1), WorkoutFeeling.exhausted);
      expect(WorkoutFeeling.fromInt(5), WorkoutFeeling.fire);
      expect(WorkoutFeeling.fromInt(null), null);
      expect(WorkoutFeeling.fromInt(99), null);
    });

    test('all feelings have emojis', () {
      for (final f in WorkoutFeeling.values) {
        expect(f.emoji, isNotEmpty);
      }
    });
  });

  // ── SocialLink ────────────────────────────────────────────────────────────
  group('SocialLink', () {
    test('isCustom when platform is null', () {
      const link = SocialLink(id: '1', platform: null, url: 'https://example.com', label: 'Mon site');
      expect(link.isCustom, true);
      expect(link.displayLabel, 'Mon site');
    });

    test('displayLabel uses platform when no label', () {
      const link = SocialLink(id: '2', platform: 'instagram', url: 'https://instagram.com/x');
      expect(link.displayLabel, 'instagram');
    });

    test('fromJson / toJson roundtrip', () {
      final json = {
        'id': 'sl-1',
        'platform': 'youtube',
        'url': 'https://youtube.com/@coach',
        'label': null,
        'position': 0,
        'visibility': 'public',
      };
      final link = SocialLink.fromJson(json);
      expect(link.platform, 'youtube');
      expect(link.visibility, LinkVisibility.public);
    });

    test('coaches_only visibility parsed correctly', () {
      const s = SocialLink(id: '3', platform: 'linkedin',
          url: 'https://linkedin.com/in/x', visibility: LinkVisibility.coachesOnly);
      expect(s.visibility.value, 'coaches_only');
    });
  });

  // ── AvailabilitySlot ──────────────────────────────────────────────────────
  group('AvailabilitySlot', () {
    test('available slot is tappable', () {
      final slot = AvailabilitySlot.fromJson({
        'start_at': '2026-03-05T09:00:00Z',
        'duration_min': 60,
        'status': 'available',
      });
      expect(slot.isTappable, true);
      expect(slot.isWaitlist, false);
    });

    test('full slot triggers waitlist', () {
      final slot = AvailabilitySlot.fromJson({
        'start_at': '2026-03-05T10:00:00Z',
        'duration_min': 60,
        'status': 'full',
      });
      expect(slot.isTappable, false);
      expect(slot.isWaitlist, true);
    });

    test('mine slot has pending status', () {
      final slot = AvailabilitySlot.fromJson({
        'start_at': '2026-03-05T11:00:00Z',
        'duration_min': 60,
        'status': 'mine',
        'booking_id': 'bk-123',
        'booking_status': 'pending_coach_validation',
      });
      expect(slot.status, SlotStatus.mine);
      expect(slot.bookingStatus, BookingStatus.pendingCoachValidation);
    });

    test('endAt = startAt + durationMin', () {
      final slot = AvailabilitySlot.fromJson({
        'start_at': '2026-03-05T09:00:00Z',
        'duration_min': 60,
        'status': 'available',
      });
      expect(slot.endAt.difference(slot.startAt).inMinutes, 60);
    });
  });
}
