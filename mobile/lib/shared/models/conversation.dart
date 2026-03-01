import 'package:equatable/equatable.dart';

class Conversation extends Equatable {
  final String id;
  final String clientId;
  final String clientName;
  final String? clientAvatar;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int unreadCount;

  const Conversation({
    required this.id,
    required this.clientId,
    required this.clientName,
    this.clientAvatar,
    this.lastMessage,
    this.lastMessageAt,
    this.unreadCount = 0,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) => Conversation(
        id: json['id'] as String,
        clientId: json['client_id'] as String,
        clientName: json['client_name'] as String,
        clientAvatar: json['client_avatar'] as String?,
        lastMessage: json['last_message'] as String?,
        lastMessageAt: json['last_message_at'] != null
            ? DateTime.parse(json['last_message_at'] as String)
            : null,
        unreadCount: (json['unread_count'] as num?)?.toInt() ?? 0,
      );

  @override
  List<Object?> get props =>
      [id, clientId, clientName, clientAvatar, lastMessage, lastMessageAt, unreadCount];
}
