import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../shared/models/tracking.dart';
import '../providers/tracking_providers.dart';

class MetricsScreen extends ConsumerStatefulWidget {
  const MetricsScreen({super.key});

  @override
  ConsumerState<MetricsScreen> createState() => _MetricsScreenState();
}

class _MetricsScreenState extends ConsumerState<MetricsScreen> {
  final _weightCtrl = TextEditingController();
  final _waistCtrl = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  bool _saving = false;

  @override
  void dispose() {
    _weightCtrl.dispose();
    _waistCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_weightCtrl.text.isEmpty) return;
    setState(() => _saving = true);
    try {
      final metric = Metric(
        weightKg: double.parse(_weightCtrl.text),
        waistCm: _waistCtrl.text.isNotEmpty ? double.parse(_waistCtrl.text) : null,
        date: _selectedDate,
      );
      await ref.read(trackingRepositoryProvider).addMetric(metric.toJson());
      ref.invalidate(metricsProvider);
      _weightCtrl.clear();
      _waistCtrl.clear();
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Métrique enregistrée ✅'), backgroundColor: AppColors.secondary));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final metricsAsync = ref.watch(metricsProvider);
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(title: const Text('Saisie métriques')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: 0,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Nouvelle mesure', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    InkWell(
                      onTap: () async {
                        final d = await showDatePicker(context: context, initialDate: _selectedDate, firstDate: DateTime(2020), lastDate: DateTime.now());
                        if (d != null) setState(() => _selectedDate = d);
                      },
                      child: InputDecorator(
                        decoration: const InputDecoration(labelText: 'Date', border: OutlineInputBorder(), suffixIcon: Icon(Icons.calendar_today)),
                        child: Text(dateFormat.format(_selectedDate)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(children: [
                      Expanded(child: TextField(controller: _weightCtrl, decoration: const InputDecoration(labelText: 'Poids (kg)', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
                      const SizedBox(width: 12),
                      Expanded(child: TextField(controller: _waistCtrl, decoration: const InputDecoration(labelText: 'Tour de taille (cm)', border: OutlineInputBorder()), keyboardType: TextInputType.number)),
                    ]),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: _saving ? null : _save,
                        child: _saving ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Enregistrer'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('Historique', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            metricsAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Erreur: $e'),
              data: (metrics) => metrics.isEmpty
                  ? const Padding(padding: EdgeInsets.all(32), child: Center(child: Text('Aucune métrique enregistrée')))
                  : Column(
                      children: metrics.map((m) => ListTile(
                            leading: const CircleAvatar(backgroundColor: AppColors.primary, child: Icon(Icons.monitor_weight_outlined, color: Colors.white, size: 20)),
                            title: Text('${m.weightKg} kg${m.waistCm != null ? ' · ${m.waistCm} cm' : ''}'),
                            subtitle: Text(dateFormat.format(m.date)),
                          )).toList(),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
