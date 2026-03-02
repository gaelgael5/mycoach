import 'package:share_plus/share_plus.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/config/app_config.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/empty_state.dart';
import '../../../../shared/widgets/shimmer_list.dart';
import '../../../../shared/models/client.dart';
import '../providers/clients_providers.dart';

class ClientsListScreen extends ConsumerStatefulWidget {
  const ClientsListScreen({super.key});

  @override
  ConsumerState<ClientsListScreen> createState() => _ClientsListScreenState();
}

class _ClientsListScreenState extends ConsumerState<ClientsListScreen> {
  final _searchCtrl = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  List<Client> _filterClients(List<Client> clients) {
    if (_searchQuery.isEmpty) return clients;
    final q = _searchQuery.toLowerCase();
    return clients.where((c) =>
        c.fullName.toLowerCase().contains(q) ||
        c.email.toLowerCase().contains(q)).toList();
  }

  @override
  Widget build(BuildContext context) {
    final clientsAsync = ref.watch(clientsListProvider);

    return Scaffold(
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showInviteSheet(context, ref),
        icon: const Icon(Icons.person_add),
        label: const Text('Inviter'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      appBar: AppBar(
        title: Row(
          children: [
            const Text('Clients'),
            const SizedBox(width: 8),
            clientsAsync.whenOrNull(
                  data: (clients) {
                    final count = clients.length;
                    final max = AppConfig.maxFreeClients;
                    Color bg, fg;
                    if (count >= max) {
                      bg = AppColors.errorContainer;
                      fg = AppColors.error;
                    } else if (count >= max - 2) {
                      bg = AppColors.warningContainer;
                      fg = const Color(0xFF92400E);
                    } else {
                      bg = AppColors.primaryContainer;
                      fg = AppColors.primary;
                    }
                    return Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(999)),
                      child: Text('$count/$max', style: TextStyle(color: fg, fontWeight: FontWeight.w600, fontSize: 12)),
                    );
                  },
                ) ??
                const SizedBox.shrink(),
          ],
        ),
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
            Center(child: TextButton(onPressed: () => ref.invalidate(clientsListProvider), child: const Text('Réessayer'))),
          ]),
          data: (clients) {
            final filtered = _filterClients(clients);
            return Column(
              children: [
                // Search bar
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                  child: TextField(
                    controller: _searchCtrl,
                    onChanged: (v) => setState(() => _searchQuery = v),
                    decoration: InputDecoration(
                      hintText: 'Rechercher un client...',
                      hintStyle: TextStyle(color: AppColors.textSecondary),
                      prefixIcon: const Icon(Icons.search, size: 20, color: AppColors.textSecondary),
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(icon: const Icon(Icons.close, size: 18), onPressed: () {
                              _searchCtrl.clear();
                              setState(() => _searchQuery = '');
                            })
                          : null,
                      filled: true,
                      fillColor: AppColors.surfaceVariant,
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                      contentPadding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),

                // List
                Expanded(
                  child: clients.isEmpty
                      ? ListView(children: const [
                          SizedBox(height: 80),
                          EmptyState(
                            icon: Icons.people_outline,
                            title: 'Pas encore de clients',
                            subtitle: 'Ajoutez votre premier client pour commencer',
                          ),
                        ])
                      : filtered.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.search_off, size: 48, color: AppColors.outline),
                                  const SizedBox(height: 12),
                                  Text('Aucun résultat pour « $_searchQuery »', style: TextStyle(color: AppColors.textSecondary)),
                                ],
                              ),
                            )
                          : ListView.separated(
                              padding: const EdgeInsets.symmetric(horizontal: 16),
                              itemCount: filtered.length,
                              separatorBuilder: (_, __) => const SizedBox(height: 8),
                              itemBuilder: (context, index) {
                                final client = filtered[index];
                                return Card(
                                  elevation: 0,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    side: BorderSide(color: AppColors.surfaceVariant),
                                  ),
                                  child: ListTile(
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                                    leading: Hero(
                                      tag: 'client_avatar_${client.id}',
                                      child: CircleAvatar(
                                        radius: 24,
                                        backgroundColor: AppColors.primaryContainer,
                                        child: Text(client.initials, style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600)),
                                      ),
                                    ),
                                    title: Text(client.fullName, style: const TextStyle(fontWeight: FontWeight.w600)),
                                    subtitle: Text(client.email, style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                                    trailing: const Icon(Icons.chevron_right, size: 20, color: AppColors.outline),
                                    onTap: () => context.push('/clients/${client.id}'),
                                  ),
                                );
                              },
                            ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }

  void _showInviteSheet(BuildContext context, WidgetRef ref) {
    final labelCtrl = TextEditingController(text: 'Lien d\'invitation');
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: EdgeInsets.fromLTRB(24, 24, 24, MediaQuery.of(ctx).viewInsets.bottom + 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Inviter un client', style: Theme.of(ctx).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Créez un lien d\'invitation que votre client utilisera pour rejoindre votre espace.', style: TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 16),
            TextField(controller: labelCtrl, decoration: const InputDecoration(labelText: 'Nom du lien (optionnel)', border: OutlineInputBorder())),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () async {
                try {
                  final repo = ref.read(clientsRepositoryProvider);
                  final token = await repo.createEnrollmentToken(label: labelCtrl.text.trim().isEmpty ? null : labelCtrl.text.trim());
                  if (ctx.mounted) Navigator.pop(ctx);
                  await SharePlus.instance.share(ShareParams(
                    text: 'Rejoignez-moi sur MyCoach ! ${token.enrollmentLink}',
                  ));
                } catch (e) {
                  if (ctx.mounted) {
                    ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text('Erreur: \$e'), backgroundColor: AppColors.error));
                  }
                }
              },
              icon: const Icon(Icons.link),
              label: const Text('Créer et partager le lien'),
            ),
          ],
        ),
      ),
    );
  }

}
