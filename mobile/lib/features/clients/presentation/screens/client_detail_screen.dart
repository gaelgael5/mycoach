import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../providers/clients_providers.dart';

class ClientDetailScreen extends ConsumerWidget {
  final String clientId;

  const ClientDetailScreen({super.key, required this.clientId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final clientAsync = ref.watch(clientDetailProvider(clientId));

    return Scaffold(
      appBar: AppBar(title: const Text('Fiche Client')),
      body: clientAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        data: (client) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              CircleAvatar(
                radius: 48,
                backgroundColor: AppColors.primary,
                child: Text(client.initials, style: const TextStyle(fontSize: 32, color: Colors.white, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 16),
              Text(client.fullName, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 24),
              _InfoTile(icon: Icons.email_outlined, label: 'Email', value: client.email),
              if (client.phone != null) _InfoTile(icon: Icons.phone_outlined, label: 'Téléphone', value: client.phone!),
              if (client.objectives != null) _InfoTile(icon: Icons.flag_outlined, label: 'Objectifs', value: client.objectives!),
              if (client.notes != null) _InfoTile(icon: Icons.notes_outlined, label: 'Notes', value: client.notes!),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () => context.push('/clients/${client.id}/program'),
                icon: const Icon(Icons.fitness_center),
                label: const Text('Voir programme'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoTile({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: AppColors.primary, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: Theme.of(context).textTheme.labelMedium?.copyWith(color: AppColors.textSecondary)),
                const SizedBox(height: 4),
                Text(value, style: Theme.of(context).textTheme.bodyLarge),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
