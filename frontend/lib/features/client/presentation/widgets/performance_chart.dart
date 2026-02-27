import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/performance_session.dart';

/// Graphique de progression des performances fl_chart.
class PerformanceChart extends StatelessWidget {
  const PerformanceChart({
    super.key,
    required this.sessions,
    required this.exerciseSlug,
  });

  final List<PerformanceSession> sessions;
  final String exerciseSlug;

  @override
  Widget build(BuildContext context) {
    final spots = _buildSpots();
    if (spots.isEmpty) {
      return SizedBox(
        height: 160,
        child: Center(
          child: Text(
            'Pas de données',
            style: AppTextStyles.body2(AppColors.grey3),
          ),
        ),
      );
    }
    return SizedBox(
      height: 160,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (_) => const FlLine(
              color: AppColors.grey7,
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 36,
                getTitlesWidget: (v, _) => Text(
                  v.toStringAsFixed(0),
                  style: AppTextStyles.caption(AppColors.grey5),
                ),
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: spots.length > 5
                    ? (spots.length / 4).ceilToDouble()
                    : 1,
                getTitlesWidget: (v, _) {
                  final idx = v.toInt();
                  if (idx < 0 || idx >= _chartSessions.length) {
                    return const SizedBox.shrink();
                  }
                  return Text(
                    DateFormat('dd/MM').format(_chartSessions[idx].date),
                    style: AppTextStyles.caption(AppColors.grey5),
                  );
                },
              ),
            ),
            topTitles: const AxisTitles(
                sideTitles: SideTitles(showTitles: false)),
            rightTitles: const AxisTitles(
                sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: AppColors.accent,
              barWidth: 2.5,
              belowBarData: BarAreaData(
                show: true,
                color: AppColors.accent.withOpacity(0.1),
              ),
              dotData: const FlDotData(show: true),
            ),
          ],
        ),
      ),
    );
  }

  List<PerformanceSession> get _chartSessions => sessions
      .where((s) => s.sets.any((e) => e.exerciseSlug == exerciseSlug))
      .toList();

  List<FlSpot> _buildSpots() {
    final relevant = _chartSessions;
    final spots = <FlSpot>[];
    for (var i = 0; i < relevant.length; i++) {
      final session = relevant[i];
      final relevantSets = session.sets
          .where((s) => s.exerciseSlug == exerciseSlug)
          .toList();
      if (relevantSets.isEmpty) continue;
      final maxWeight = relevantSets
          .map((s) => s.weight ?? 0.0)
          .reduce((a, b) => a > b ? a : b);
      spots.add(FlSpot(i.toDouble(), maxWeight));
    }
    return spots;
  }
}
