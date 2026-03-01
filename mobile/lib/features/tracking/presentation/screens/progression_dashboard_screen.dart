import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/tracking.dart';
import '../providers/tracking_providers.dart';

class ProgressionDashboardScreen extends ConsumerWidget {
  const ProgressionDashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metricsAsync = ref.watch(metricsProvider);
    final completionsAsync = ref.watch(trackingProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Progression')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Poids (30 derniers jours)', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            SizedBox(
              height: 220,
              child: metricsAsync.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(child: Text('$e')),
                data: (metrics) => metrics.isEmpty
                    ? const Center(child: Text('Pas de données'))
                    : _WeightChart(metrics: metrics),
              ),
            ),
            const SizedBox(height: 32),
            Text('Séances complétées (7 derniers jours)', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            SizedBox(
              height: 200,
              child: completionsAsync.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Center(child: Text('$e')),
                data: (completions) => _CompletionBarChart(completions: completions),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _WeightChart extends StatelessWidget {
  final List<Metric> metrics;
  const _WeightChart({required this.metrics});

  @override
  Widget build(BuildContext context) {
    final sorted = [...metrics]..sort((a, b) => a.date.compareTo(b.date));
    final spots = sorted.asMap().entries.map((e) => FlSpot(e.key.toDouble(), e.value.weightKg)).toList();
    final minY = sorted.map((m) => m.weightKg).reduce((a, b) => a < b ? a : b) - 2;
    final maxY = sorted.map((m) => m.weightKg).reduce((a, b) => a > b ? a : b) + 2;

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(8, 16, 16, 8),
        child: LineChart(
          LineChartData(
            minY: minY,
            maxY: maxY,
            gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: 2),
            titlesData: FlTitlesData(
              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              bottomTitles: AxisTitles(sideTitles: SideTitles(
                showTitles: true,
                interval: (sorted.length / 5).ceilToDouble().clamp(1, 100),
                getTitlesWidget: (val, _) {
                  final i = val.toInt();
                  if (i < 0 || i >= sorted.length) return const SizedBox.shrink();
                  return Text(DateFormat('dd/MM').format(sorted[i].date), style: const TextStyle(fontSize: 10));
                },
              )),
              leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, interval: 2, getTitlesWidget: (v, _) => Text('${v.toInt()}', style: const TextStyle(fontSize: 10)))),
            ),
            borderData: FlBorderData(show: false),
            lineBarsData: [
              LineChartBarData(
                spots: spots,
                isCurved: true,
                color: AppColors.primary,
                barWidth: 3,
                dotData: FlDotData(show: spots.length < 15),
                belowBarData: BarAreaData(show: true, color: AppColors.primary.withValues(alpha: 0.1)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _CompletionBarChart extends StatelessWidget {
  final List<SessionCompletion> completions;
  const _CompletionBarChart({required this.completions});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final last7 = List.generate(7, (i) => now.subtract(Duration(days: 6 - i)));
    final dayNames = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];

    final counts = last7.map((day) {
      return completions.where((c) =>
          c.completedAt.year == day.year && c.completedAt.month == day.month && c.completedAt.day == day.day).length.toDouble();
    }).toList();

    final maxY = (counts.isEmpty ? 1.0 : counts.reduce((a, b) => a > b ? a : b)).clamp(1, 100).toDouble() + 1;

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(8, 16, 16, 8),
        child: BarChart(
          BarChartData(
            maxY: maxY,
            gridData: FlGridData(show: true, drawVerticalLine: false),
            titlesData: FlTitlesData(
              topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
              bottomTitles: AxisTitles(sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (val, _) {
                  final i = val.toInt();
                  if (i < 0 || i >= 7) return const SizedBox.shrink();
                  return Text(dayNames[last7[i].weekday - 1], style: const TextStyle(fontSize: 12));
                },
              )),
              leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 28, interval: 1, getTitlesWidget: (v, _) => Text('${v.toInt()}', style: const TextStyle(fontSize: 10)))),
            ),
            borderData: FlBorderData(show: false),
            barGroups: List.generate(7, (i) => BarChartGroupData(
              x: i,
              barRods: [
                BarChartRodData(
                  toY: counts[i],
                  color: AppColors.secondary,
                  width: 20,
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
                ),
              ],
            )),
          ),
        ),
      ),
    );
  }
}
