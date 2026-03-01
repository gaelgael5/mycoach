import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/theme/app_colors.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Bienvenue sur MyCoach 👋', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Votre espace coach', style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: AppColors.textSecondary)),
            const SizedBox(height: 32),
            _QuickAction(
              icon: Icons.fitness_center,
              label: 'Programmes',
              subtitle: 'Gérer les programmes d\'entraînement',
              color: AppColors.primary,
              onTap: () => context.go('/programs'),
            ),
            const SizedBox(height: 12),
            _QuickAction(
              icon: Icons.monitor_weight_outlined,
              label: 'Saisie métriques',
              subtitle: 'Poids, tour de taille',
              color: AppColors.secondary,
              onTap: () => context.push('/tracking/metrics'),
            ),
            const SizedBox(height: 12),
            _QuickAction(
              icon: Icons.trending_up,
              label: 'Progression',
              subtitle: 'Graphes et statistiques',
              color: const Color(0xFF8B5CF6),
              onTap: () => context.push('/tracking/progression'),
            ),
          ],
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _QuickAction({required this.icon, required this.label, required this.subtitle, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48, height: 48,
                decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
                child: Icon(icon, color: color),
              ),
              const SizedBox(width: 16),
              Expanded(child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                  Text(subtitle, style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                ],
              )),
              Icon(Icons.chevron_right, color: AppColors.textSecondary),
            ],
          ),
        ),
      ),
    );
  }
}
