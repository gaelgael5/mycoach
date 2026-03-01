import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/widgets/shimmer_list.dart';
import '../../../auth/presentation/providers/auth_providers.dart';
import '../providers/profile_providers.dart';
import '../../data/profile_repository.dart';
import 'edit_profile_screen.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon Profil'),
        actions: [
          if (profileAsync.hasValue)
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: () => Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) => EditProfileScreen(profile: profileAsync.value!),
                ),
              ),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(profileProvider.notifier).refresh(),
        child: profileAsync.when(
          loading: () => const ShimmerList(itemCount: 4),
          error: (e, _) => ListView(children: [
            const SizedBox(height: 100),
            Center(child: Text('Erreur: $e')),
            const SizedBox(height: 12),
            Center(
              child: ElevatedButton(
                onPressed: () => ref.read(profileProvider.notifier).refresh(),
                child: const Text('Réessayer'),
              ),
            ),
          ]),
          data: (profile) => ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Center(
                child: CircleAvatar(
                  radius: 56,
                  backgroundColor: AppColors.primary,
                  child: Text(
                    '${profile.firstName.isNotEmpty ? profile.firstName[0] : ''}${profile.lastName.isNotEmpty ? profile.lastName[0] : ''}',
                    style: const TextStyle(
                        fontSize: 36,
                        color: Colors.white,
                        fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Center(
                child: Text(profile.fullName,
                    style: Theme.of(context)
                        .textTheme
                        .headlineSmall
                        ?.copyWith(fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 24),
              _InfoTile(icon: Icons.email_outlined, label: 'Email', value: profile.email),
              _InfoTile(
                  icon: Icons.phone_outlined,
                  label: 'Téléphone',
                  value: profile.phone ?? 'Non renseigné'),
              if (profile.specialties.isNotEmpty)
                _InfoTile(
                    icon: Icons.fitness_center,
                    label: 'Spécialités',
                    value: profile.specialties.join(', ')),
              if (profile.bio != null && profile.bio!.isNotEmpty)
                _InfoTile(icon: Icons.info_outline, label: 'Bio', value: profile.bio!),
              const SizedBox(height: 24),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.star_outline, color: AppColors.primary),
                          const SizedBox(width: 8),
                          Text('Mon plan : ${profile.plan}',
                              style: const TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 16)),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('${profile.clientCount}/${profile.maxClients} clients'),
                          Text(
                            '${((profile.clientCount / profile.maxClients) * 100).round()}%',
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, color: AppColors.primary),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: LinearProgressIndicator(
                          value: profile.clientCount / profile.maxClients,
                          minHeight: 10,
                          backgroundColor: AppColors.border,
                          color: profile.clientCount >= profile.maxClients
                              ? AppColors.error
                              : AppColors.secondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              OutlinedButton.icon(
                onPressed: () {
                  ref.read(authStateProvider.notifier).logout();
                  context.go('/login');
                },
                icon: const Icon(Icons.logout, color: AppColors.error),
                label: const Text('Se déconnecter',
                    style: TextStyle(color: AppColors.error)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: AppColors.error),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
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
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, color: AppColors.textSecondary, size: 22),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: TextStyle(
                        fontSize: 12, color: AppColors.textSecondary)),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(fontSize: 15)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
