import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/client.dart';

void main() {
  group('Client', () {
    final json = {
      'id': 'c1',
      'first_name': 'Jean',
      'last_name': 'Dupont',
      'email': 'jean@test.com',
      'phone': '+33600000000',
      'objectives': 'Lose weight',
      'notes': 'Morning sessions',
      'created_at': '2025-01-15T10:00:00Z',
    };

    test('fromJson parses correctly', () {
      final client = Client.fromJson(json);
      expect(client.id, 'c1');
      expect(client.firstName, 'Jean');
      expect(client.lastName, 'Dupont');
      expect(client.email, 'jean@test.com');
      expect(client.phone, '+33600000000');
    });

    test('toJson produces correct map', () {
      final client = Client.fromJson(json);
      final output = client.toJson();
      expect(output['first_name'], 'Jean');
      expect(output['last_name'], 'Dupont');
      expect(output['email'], 'jean@test.com');
    });

    test('fullName and initials', () {
      final client = Client.fromJson(json);
      expect(client.fullName, 'Jean Dupont');
      expect(client.initials, 'JD');
    });

    test('optional fields default to null', () {
      final minimal = {
        'id': 'c2', 'first_name': 'A', 'last_name': 'B',
        'email': 'a@b.com', 'created_at': '2025-01-01T00:00:00Z',
      };
      final client = Client.fromJson(minimal);
      expect(client.phone, isNull);
      expect(client.objectives, isNull);
      expect(client.notes, isNull);
    });
  });
}
