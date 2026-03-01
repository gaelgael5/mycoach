import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../core/api/api_client.dart';
import '../../../core/config/app_config.dart';
import '../../../core/storage/secure_storage.dart';
import '../../../shared/models/conversation.dart';
import '../../../shared/models/message.dart';

class MessagesRepository {
  final ApiClient _api;
  final SecureStorageService _storage;

  MessagesRepository(this._api, this._storage);

  Future<List<Conversation>> getConversations() async {
    final response = await _api.dio.get('/conversations');
    final list = response.data as List;
    return list.map((e) => Conversation.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<List<ChatMessage>> getMessages(String conversationId) async {
    final response = await _api.dio.get('/conversations/$conversationId/messages');
    final list = response.data as List;
    return list.map((e) => ChatMessage.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<WebSocketChannel> connectWebSocket(String conversationId) async {
    final token = await _storage.getToken();
    final baseUrl = AppConfig.apiBaseUrl;
    final wsUrl = baseUrl
        .replaceFirst('http://', 'ws://')
        .replaceFirst('https://', 'wss://')
        .replaceFirst('/api/v1', '');
    final uri = Uri.parse('$wsUrl/api/v1/ws/$conversationId?token=$token');
    return WebSocketChannel.connect(uri);
  }

  Future<ChatMessage> sendMessage(String conversationId, String content) async {
    final response = await _api.dio.post(
      '/conversations/$conversationId/messages',
      data: {'content': content},
    );
    return ChatMessage.fromJson(response.data as Map<String, dynamic>);
  }
}
