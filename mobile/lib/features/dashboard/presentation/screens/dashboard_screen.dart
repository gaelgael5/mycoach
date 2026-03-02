import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../features/clients/presentation/providers/clients_providers.dart';
import '../../../../features/programs/presentation/providers/programs_providers.dart';
import '../../../../features/profile/presentation/providers/profile_providers.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);
    final clientsAsync = ref.watch(clientsListProvider);
    final programsAsync = ref.watch(programsProvider);

    final firstName = profileAsync.whenOrNull(data: (p) => p.firstName) ?? '';
    final clientCount = clientsAsync.whenOrNull(data: (c) => c.length) ?? 0;
    final programCount = programsAsync.whenOrNull(data: (p) => p.length) ?? 0;

    final now = DateTime.now();
    final days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];
    final months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
    final dateStr = '${days[now.weekday - 1]} ${now.day} ${months[now.month - 1]} ${now.year}';

    return Scaffold(
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: () async {
          ref.invalidate(profileProvider);
          ref.invalidate(clientsListProvider);
          ref.invalidate(programsProvider);
        },
        child: ListView(
          padding: EdgeInsets.only(
            top: MediaQuery.of(context).padding.top + 16,
            left: 16,
            right: 16,
            bottom: 100,
          ),
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Bonjour, $firstName 👋', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    Text(dateStr, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
                  ],
                ),
                CircleAvatar(
                  radius: 22,
                  backgroundColor: AppColors.primaryContainer,
                  child: Text(
                    firstName.isNotEmpty ? firstName[0].toUpperCase() : '?',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(color: AppColors.primary),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Stats rapides
            Row(
              children: [
                _StatCard(icon: Icons.people, value: '$clientCount', label: 'Clients', color: AppColors.primary),
                const SizedBox(width: 12),
                _StatCard(icon: Icons.fitness_center, value: '$programCount', label: 'Programmes', color: AppColors.secondary),
                const SizedBox(width: 12),
                _StatCard(icon: Icons.chat_bubble, value: '0', label: 'Messages', color: const Color(0xFFF59E0B)),
              ],
            ),

            const SizedBox(height: 24),

            // Quick actions
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Actions rapides', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              ],
            ),
            const SizedBox(height: 12),

            _ActionCard(
              icon: Icons.person_add,
              label: 'Ajouter un client',
              color: AppColors.primary,
              onTap: () => context.go('/clients'),
            ),
            const SizedBox(height: 8),
            _ActionCard(
              icon: Icons.fitness_center,
              label: 'Créer un programme',
              color: AppColors.secondary,
              onTap: () => context.go('/programs'),
            ),
            const SizedBox(height: 8),
            _ActionCard(
              icon: Icons.trending_up,
              label: 'Voir la progression',
              color: const Color(0xFF8B5CF6),
              onTap: () => context.push('/tracking/progression'),
            ),
            const SizedBox(height: 8),
            _ActionCard(
              icon: Icons.monitor_weight_outlined,
              label: 'Saisie métriques',
              color: const Color(0xFFF59E0B),
              onTap: () => context.push('/tracking/metrics'),
            ),

            const SizedBox(height: 24),

            // Clients récents
            if (clientsAsync.hasValue && clientsAsync.value!.isNotEmpty) ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Clients récents', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                  TextButton(onPressed: () => context.go('/clients'), child: Text('Voir tout', style: TextStyle(color: AppColors.primary))),
                ],
              ),
              const SizedBox(height: 8),
              ...clientsAsync.value!.take(3).map((c) => Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppColors.surfaceVariant),
                    ),
                    child: InkWell(
                      onTap: () => context.go('/clients/${c.id}'),
                      child: Row(
                        children: [
                          CircleAvatar(
                            radius: 20,
                            backgroundColor: AppColors.primaryContainer,
                            child: Text(c.firstName[0].toUpperCase(), style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600)),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(c.fullName, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w500)),
                          ),
                          const Icon(Icons.chevron_right, size: 20, color: AppColors.outline),
                        ],
                      ),
                    ),
                  )),
            ],
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatCard({required this.icon, required this.value, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.surfaceVariant),
        ),
        child: Column(
          children: [
            Icon(icon, size: 20, color: color),
            const SizedBox(height: 8),
            Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            Text(label, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionCard({required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 0,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Container(
                width: 40, height: 40,
                decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(child: Text(label, style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w500))),
              Icon(Icons.chevron_right, color: AppColors.textSecondary, size: 20),
            ],
          ),
        ),
      ),
    );
  }
}
