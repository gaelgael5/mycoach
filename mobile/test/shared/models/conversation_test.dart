import 'package:flutter_test/flutter_test.dart';
import 'package:mycoach_mobile/shared/models/conversation.dart';

void main() {
  group('Conversation', () {
    test('fromJson full', () {
      final c = Conversation.fromJson({
        'id': 'conv1', 'client_id': 'c1', 'client_name': 'Jean',
        'client_avatar': 'http://img.png', 'last_message': 'Hello',
        'last_message_at': '2025-06-01T12:00:00Z', 'unread_count': 3,
      });
      expect(c.clientName, 'Jean');
      expect(c.unreadCount, 3);
      expect(c.lastMessageAt, isNotNull);
    });

    test('fromJson defaults', () {
      final c = Conversation.fromJson({
        'id': 'conv2', 'client_id': 'c2', 'client_name': 'Marie',
      });
      expect(c.unreadCount, 0);
      expect(c.lastMessage, isNull);
      expect(c.lastMessageAt, isNull);
      expect(c.clientAvatar, isNull);
    });
  });
}
