import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../../../core/providers/core_providers.dart';
import '../../../../shared/models/conversation.dart';
import '../../../../shared/models/message.dart';
import '../../data/messages_repository.dart';

final messagesRepositoryProvider = Provider<MessagesRepository>((ref) {
  return MessagesRepository(
    ref.watch(apiClientProvider),
    ref.watch(secureStorageProvider),
  );
});

final conversationsProvider =
    AsyncNotifierProvider<ConversationsNotifier, List<Conversation>>(
        ConversationsNotifier.new);

class ConversationsNotifier extends AsyncNotifier<List<Conversation>> {
  @override
  Future<List<Conversation>> build() async {
    return ref.read(messagesRepositoryProvider).getConversations();
  }

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(
        () => ref.read(messagesRepositoryProvider).getConversations());
  }
}

final unreadCountProvider = Provider<int>((ref) {
  final convs = ref.watch(conversationsProvider);
  return convs.whenOrNull(
        data: (list) => list.fold<int>(0, (sum, c) => sum + c.unreadCount),
      ) ??
      0;
});

final chatProvider = StateNotifierProvider.family<ChatNotifier, AsyncValue<List<ChatMessage>>, String>(
  (ref, conversationId) => ChatNotifier(ref, conversationId),
);

class ChatNotifier extends StateNotifier<AsyncValue<List<ChatMessage>>> {
  final Ref _ref;
  final String conversationId;
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;

  ChatNotifier(this._ref, this.conversationId) : super(const AsyncValue.loading()) {
    _init();
  }

  Future<void> _init() async {
    try {
      final repo = _ref.read(messagesRepositoryProvider);
      final messages = await repo.getMessages(conversationId);
      state = AsyncValue.data(messages);
      _connectWs();
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> _connectWs() async {
    try {
      final repo = _ref.read(messagesRepositoryProvider);
      _channel = await repo.connectWebSocket(conversationId);
      _subscription = _channel!.stream.listen(
        (data) {
          try {
            final json = jsonDecode(data as String) as Map<String, dynamic>;
            final msg = ChatMessage.fromJson(json);
            final current = state.valueOrNull ?? [];
            state = AsyncValue.data([...current, msg]);
          } catch (_) {}
        },
        onError: (_) => _reconnect(),
        onDone: () => _reconnect(),
      );
    } catch (_) {
      Future.delayed(const Duration(seconds: 3), _connectWs);
    }
  }

  void _reconnect() {
    _subscription?.cancel();
    _channel?.sink.close();
    Future.delayed(const Duration(seconds: 3), _connectWs);
  }

  Future<void> sendMessage(String content) async {
    try {
      if (_channel != null) {
        _channel!.sink.add(jsonEncode({'content': content}));
      } else {
        final repo = _ref.read(messagesRepositoryProvider);
        final msg = await repo.sendMessage(conversationId, content);
        final current = state.valueOrNull ?? [];
        state = AsyncValue.data([...current, msg]);
      }
    } catch (_) {}
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _channel?.sink.close();
    super.dispose();
  }
}
