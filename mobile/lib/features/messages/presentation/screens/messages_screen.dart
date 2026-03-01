import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/empty_state.dart';
import '../../../../shared/widgets/shimmer_list.dart';
import '../providers/messages_providers.dart';
import 'chat_screen.dart';

class MessagesScreen extends ConsumerWidget {
  const MessagesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final convsAsync = ref.watch(conversationsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Messages')),
      body: RefreshIndicator(
        onRefresh: () => ref.read(conversationsProvider.notifier).refresh(),
        child: convsAsync.when(
          loading: () => const ShimmerList(),
          error: (e, _) => Center(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.error_outline, size: 48, color: AppColors.error),
              const SizedBox(height: 12),
              Text('Erreur: $e'),
              const SizedBox(height: 12),
              ElevatedButton(
                onPressed: () => ref.read(conversationsProvider.notifier).refresh(),
                child: const Text('Réessayer'),
              ),
            ]),
          ),
          data: (convs) => convs.isEmpty
              ? ListView(children: const [
                  SizedBox(height: 100),
                  EmptyState(
                    icon: Icons.chat_bubble_outline,
                    title: 'Pas encore de conversations',
                    subtitle: 'Vos échanges avec vos clients apparaîtront ici',
                  ),
                ])
              : ListView.separated(
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  itemCount: convs.length,
                  separatorBuilder: (_, __) => const Divider(height: 1, indent: 72),
                  itemBuilder: (context, index) {
                    final conv = convs[index];
                    final initials = conv.clientName
                        .split(' ')
                        .take(2)
                        .map((w) => w.isNotEmpty ? w[0].toUpperCase() : '')
                        .join();
                    return ListTile(
                      leading: Hero(
                        tag: 'avatar_${conv.clientId}',
                        child: CircleAvatar(
                          backgroundColor: AppColors.primary,
                          child: Text(initials,
                              style: const TextStyle(
                                  color: Colors.white, fontWeight: FontWeight.bold)),
                        ),
                      ),
                      title: Text(conv.clientName,
                          style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: conv.lastMessage != null
                          ? Text(conv.lastMessage!,
                              maxLines: 1, overflow: TextOverflow.ellipsis)
                          : null,
                      trailing: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          if (conv.lastMessageAt != null)
                            Text(
                              _formatTime(conv.lastMessageAt!),
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(color: AppColors.textSecondary),
                            ),
                          if (conv.unreadCount > 0) ...[
                            const SizedBox(height: 4),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppColors.error,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text('${conv.unreadCount}',
                                  style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold)),
                            ),
                          ],
                        ],
                      ),
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => ChatScreen(
                            conversationId: conv.id,
                            clientName: conv.clientName,
                            clientId: conv.clientId,
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inMinutes < 1) return "À l'instant";
    if (diff.inHours < 1) return 'Il y a ${diff.inMinutes}min';
    if (diff.inDays < 1) return DateFormat.Hm().format(dt);
    if (diff.inDays < 7) return DateFormat.E('fr').format(dt);
    return DateFormat.MMMd('fr').format(dt);
  }
}
