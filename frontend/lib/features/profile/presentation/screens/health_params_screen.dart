import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/health_log.dart';
import '../../../../shared/models/health_parameter.dart';
import '../providers/health_providers.dart';
import '../widgets/health_chart_widget.dart';

/// Écran des paramètres de santé.
class HealthParamsScreen extends ConsumerWidget {
  const HealthParamsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;
    final paramsAsync = ref.watch(healthParametersProvider);
    final logsAsync  = ref.watch(healthLogsNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.healthParamsTitle),
      ),
      body: paramsAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) => Center(
          child: Text(l.errorGeneric,
              style: AppTextStyles.body1(AppColors.grey3)),
        ),
        data: (params) {
          if (params.isEmpty) {
            return Center(
              child: Text(l.healthParamsEmpty,
                  style: AppTextStyles.body1(AppColors.grey3)),
            );
          }
          final logsMap = logsAsync.valueOrNull ?? {};
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: params.length,
            itemBuilder: (context, i) {
              final param = params[i];
              final logs  = logsMap[param.slug] ?? [];
              return _HealthParamCard(
                parameter: param,
                logs:      logs,
              );
            },
          );
        },
      ),
    );
  }
}

class _HealthParamCard extends ConsumerWidget {
  const _HealthParamCard({required this.parameter, required this.logs});

  final HealthParameter parameter;
  final List<HealthLog> logs;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;
    final locale = Localizations.localeOf(context).languageCode;
    final label  = parameter.labelFor(locale);
    final last   = logs.isNotEmpty ? logs.first : null;
    final fmt    = DateFormat('dd/MM/yyyy');

    return GestureDetector(
      onTap: () => _showDetail(context, ref),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.card),
          border: Border.all(color: AppColors.grey7),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(label, style: AppTextStyles.body1(AppColors.white)),
                // Bouton + pour ajouter une mesure
                GestureDetector(
                  onTap: () => _showAddLog(context, ref),
                  child: Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      color: AppColors.accent.withOpacity(0.2),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.add,
                        color: AppColors.accent, size: 18),
                  ),
                ),
              ],
            ),
            if (last != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  Text(
                    '${last.value} ${last.unit}',
                    style: AppTextStyles.headline4(AppColors.accent),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    fmt.format(last.measuredAt),
                    style: AppTextStyles.caption(AppColors.grey3),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (logs.length > 1)
                HealthChartWidget(logs: logs, compact: true),
            ] else
              Text(
                l.healthParamsEmpty,
                style: AppTextStyles.caption(AppColors.grey3),
              ),
          ],
        ),
      ),
    );
  }

  void _showDetail(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => _HealthDetailSheet(parameter: parameter, logs: logs),
    );
  }

  void _showAddLog(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => _AddLogSheet(parameter: parameter),
    );
  }
}

class _HealthDetailSheet extends ConsumerWidget {
  const _HealthDetailSheet({required this.parameter, required this.logs});

  final HealthParameter parameter;
  final List<HealthLog> logs;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l      = context.l10n;
    final locale = Localizations.localeOf(context).languageCode;
    final label  = parameter.labelFor(locale);
    final fmt    = DateFormat('dd/MM/yyyy HH:mm');

    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      maxChildSize: 0.95,
      minChildSize: 0.4,
      expand: false,
      builder: (_, controller) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: AppTextStyles.headline3(AppColors.white)),
            const SizedBox(height: 16),
            if (logs.length > 1) ...[
              HealthChartWidget(logs: logs),
              const SizedBox(height: 16),
            ],
            Text(l.healthParamsTitle,
                style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            Expanded(
              child: logs.isEmpty
                  ? Center(
                      child: Text(l.healthParamsEmpty,
                          style: AppTextStyles.body1(AppColors.grey3)))
                  : ListView.builder(
                      controller: controller,
                      itemCount: logs.length,
                      itemBuilder: (_, i) {
                        final log = logs[i];
                        return ListTile(
                          title: Text(
                            '${log.value} ${log.unit}',
                            style: AppTextStyles.body1(AppColors.white),
                          ),
                          subtitle: Text(
                            fmt.format(log.measuredAt),
                            style: AppTextStyles.caption(AppColors.grey3),
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline,
                                color: AppColors.red, size: 18),
                            onPressed: () {
                              ref
                                  .read(healthLogsNotifierProvider.notifier)
                                  .deleteLog(log.id);
                              Navigator.of(context).pop();
                            },
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AddLogSheet extends ConsumerStatefulWidget {
  const _AddLogSheet({required this.parameter});

  final HealthParameter parameter;

  @override
  ConsumerState<_AddLogSheet> createState() => _AddLogSheetState();
}

class _AddLogSheetState extends ConsumerState<_AddLogSheet> {
  final _valueCtrl = TextEditingController();
  final _formKey   = GlobalKey<FormState>();
  bool _isLoading  = false;

  @override
  void dispose() {
    _valueCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l      = context.l10n;
    final locale = Localizations.localeOf(context).languageCode;
    final label  = widget.parameter.labelFor(locale);

    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(l.healthParamsAdd,
                    style: AppTextStyles.headline4(AppColors.white)),
                IconButton(
                  icon: const Icon(Icons.close, color: AppColors.grey3),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(label, style: AppTextStyles.body1(AppColors.grey3)),
            const SizedBox(height: 8),
            TextFormField(
              controller: _valueCtrl,
              style: AppTextStyles.body1(AppColors.white),
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                suffixText: widget.parameter.unit,
                suffixStyle: AppTextStyles.body1(AppColors.grey3),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return l.validationRequired;
                if (double.tryParse(v.trim()) == null) {
                  return l.validationBirthYearInvalid;
                }
                return null;
              },
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _submit,
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: AppColors.white,
                        ),
                      )
                    : Text(l.btnSave),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      await ref.read(healthLogsNotifierProvider.notifier).addLog(
        parameterId: widget.parameter.id,
        value:       double.parse(_valueCtrl.text.trim()),
      );
      if (mounted) Navigator.of(context).pop();
    } catch (_) {
      // Erreur gérée par le notifier
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}
