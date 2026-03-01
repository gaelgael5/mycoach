import 'package:equatable/equatable.dart';

class ChatMessage extends Equatable {
  final String id;
  final String conversationId;
  final String senderId;
  final String senderRole;
  final String content;
  final DateTime createdAt;

  const ChatMessage({
    required this.id,
    required this.conversationId,
    required this.senderId,
    required this.senderRole,
    required this.content,
    required this.createdAt,
  });

  bool get isCoach => senderRole == 'coach';

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: json['id'] as String,
        conversationId: json['conversation_id'] as String,
        senderId: json['sender_id'] as String,
        senderRole: json['sender_role'] as String,
        content: json['content'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'conversation_id': conversationId,
        'sender_id': senderId,
        'sender_role': senderRole,
        'content': content,
        'created_at': createdAt.toIso8601String(),
      };

  @override
  List<Object?> get props => [id, conversationId, senderId, senderRole, content, createdAt];
}
