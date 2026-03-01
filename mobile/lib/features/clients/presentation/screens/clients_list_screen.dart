import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/app_config.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/empty_state.dart';
import '../../../../shared/widgets/shimmer_list.dart';
import '../providers/clients_providers.dart';

class ClientsListScreen extends ConsumerWidget {
  const ClientsListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final clientsAsync = ref.watch(clientsListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes Clients'),
        actions: [
          clientsAsync.whenOrNull(
                data: (clients) => Padding(
                  padding: const EdgeInsets.only(right: 16),
                  child: Chip(
                    label: Text(
                      '${clients.length}/${AppConfig.maxFreeClients}',
                      style: TextStyle(
                        color: clients.length >= AppConfig.maxFreeClients
                            ? AppColors.error
                            : AppColors.secondary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    backgroundColor: (clients.length >= AppConfig.maxFreeClients
                            ? AppColors.error
                            : AppColors.secondary)
                        .withValues(alpha: 0.1),
                  ),
                ),
              ) ??
              const SizedBox.shrink(),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(clientsListProvider),
        child: clientsAsync.when(
          loading: () => const ShimmerList(),
          error: (e, _) => ListView(children: [
            const SizedBox(height: 100),
            const Icon(Icons.error_outline, size: 48, color: AppColors.error),
            const SizedBox(height: 12),
            Center(child: Text('Erreur: $e')),
            const SizedBox(height: 12),
            Center(
              child: ElevatedButton(
                onPressed: () => ref.invalidate(clientsListProvider),
                child: const Text('Réessayer'),
              ),
            ),
          ]),
          data: (clients) => clients.isEmpty
              ? ListView(children: const [
                  SizedBox(height: 80),
                  EmptyState(
                    icon: Icons.people_outline,
                    title: 'Pas encore de clients',
                    subtitle: 'Ajoutez votre premier client pour commencer',
                  ),
                ])
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: clients.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final client = clients[index];
                    return Card(
                      child: ListTile(
                        leading: Hero(
                          tag: 'client_avatar_${client.id}',
                          child: CircleAvatar(
                            backgroundColor: AppColors.primary,
                            child: Text(client.initials,
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold)),
                          ),
                        ),
                        title: Text(client.fullName,
                            style:
                                const TextStyle(fontWeight: FontWeight.w600)),
                        subtitle: Text(client.email),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => context.push('/clients/${client.id}'),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
