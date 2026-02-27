import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/health_log.dart';

/// Graphique linéaire pour l'historique d'un paramètre de santé.
class HealthChartWidget extends StatelessWidget {
  const HealthChartWidget({
    super.key,
    required this.logs,
    this.compact = false,
    this.lineColor,
  });

  final List<HealthLog> logs;
  final bool compact;
  final Color? lineColor;

  @override
  Widget build(BuildContext context) {
    if (logs.isEmpty) {
      return const SizedBox.shrink();
    }

    // On prend les N derniers logs triés chronologiquement
    final sorted = [...logs]
      ..sort((a, b) => a.measuredAt.compareTo(b.measuredAt));
    final display = compact ? sorted.take(7).toList() : sorted;

    final spots = display.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.value);
    }).toList();

    final values = display.map((l) => l.value).toList();
    final minY = values.reduce((a, b) => a < b ? a : b);
    final maxY = values.reduce((a, b) => a > b ? a : b);
    final padding = (maxY - minY) * 0.2;

    final color = lineColor ?? AppColors.accent;

    return SizedBox(
      height: compact ? 50 : 180,
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: !compact),
          titlesData: FlTitlesData(show: !compact),
          borderData: FlBorderData(show: false),
          minY: (minY - padding).isFinite ? minY - padding : minY - 1,
          maxY: (maxY + padding).isFinite ? maxY + padding : maxY + 1,
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: color,
              barWidth: compact ? 1.5 : 2.5,
              dotData: FlDotData(show: !compact),
              belowBarData: BarAreaData(
                show: true,
                color: color.withOpacity(0.12),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            enabled: !compact,
            touchTooltipData: LineTouchTooltipData(
              tooltipBgColor: AppColors.bgCard,
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  final log = display[spot.spotIndex];
                  return LineTooltipItem(
                    '${log.value} ${log.unit}',
                    AppTextStyles.caption(AppColors.white),
                  );
                }).toList();
              },
            ),
          ),
        ),
      ),
    );
  }
}
