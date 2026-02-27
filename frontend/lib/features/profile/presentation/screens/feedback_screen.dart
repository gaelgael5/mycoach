import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../shared/models/feedback_item.dart';
import '../providers/feedback_providers.dart';

/// Écran de feedback (suggestions et bug reports).
class FeedbackScreen extends ConsumerStatefulWidget {
  const FeedbackScreen({super.key});

  @override
  ConsumerState<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends ConsumerState<FeedbackScreen> {
  final _formKey      = GlobalKey<FormState>();
  final _titleCtrl    = TextEditingController();
  final _descCtrl     = TextEditingController();
  bool _isLoading     = false;
  bool _justSent      = false;

  @override
  void dispose() {
    _titleCtrl.dispose();
    _descCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l    = context.l10n;
    final type = ref.watch(feedbackTypeSelectedProvider);
    final feedbacksAsync = ref.watch(feedbackNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.feedbackTitle),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ─ Segmented control ──────────────────────────────────────────
            Container(
              decoration: BoxDecoration(
                color: AppColors.bgCard,
                borderRadius: BorderRadius.circular(AppRadius.input),
                border: Border.all(color: AppColors.grey7),
              ),
              child: Row(
                children: [
                  _TypeButton(
                    label:    l.feedbackTypeSuggestion,
                    selected: type == 'suggestion',
                    onTap:    () => ref
                        .read(feedbackTypeSelectedProvider.notifier)
                        .state = 'suggestion',
                  ),
                  _TypeButton(
                    label:    l.feedbackTypeBug,
                    selected: type == 'bug_report',
                    onTap:    () => ref
                        .read(feedbackTypeSelectedProvider.notifier)
                        .state = 'bug_report',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // ─ Formulaire ─────────────────────────────────────────────────
            if (_justSent)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: AppColors.green.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(AppRadius.card),
                  border: Border.all(
                      color: AppColors.green.withOpacity(0.4)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle,
                        color: AppColors.green, size: 18),
                    const SizedBox(width: 8),
                    Text(l.feedbackSent,
                        style: AppTextStyles.body2(AppColors.green)),
                  ],
                ),
              ),
            Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(l.feedbackTitleField,
                      style: AppTextStyles.label(AppColors.grey3)),
                  const SizedBox(height: 6),
                  TextFormField(
                    controller: _titleCtrl,
                    style: AppTextStyles.body1(AppColors.white),
                    maxLength: 100,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l.validationRequired
                        : null,
                  ),
                  const SizedBox(height: 12),
                  Text(l.feedbackDescription,
                      style: AppTextStyles.label(AppColors.grey3)),
                  const SizedBox(height: 6),
                  TextFormField(
                    controller: _descCtrl,
                    style: AppTextStyles.body1(AppColors.white),
                    maxLength: 1000,
                    maxLines: 5,
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? l.validationRequired
                        : null,
                  ),
                  const SizedBox(height: 20),
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
                          : Text(l.feedbackSend),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // ─ Historique ─────────────────────────────────────────────────
            Text(l.feedbackHistory, style: AppTextStyles.label(AppColors.grey3)),
            const SizedBox(height: 8),
            feedbacksAsync.when(
              loading: () => const LinearProgressIndicator(
                color: AppColors.accent,
              ),
              error: (_, __) => const SizedBox.shrink(),
              data: (items) => items.isEmpty
                  ? Text(
                      l.healthParamsEmpty,
                      style: AppTextStyles.body2(AppColors.grey3),
                    )
                  : Column(
                      children: items
                          .map((item) => _FeedbackItemTile(item: item))
                          .toList(),
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
      final type = ref.read(feedbackTypeSelectedProvider);
      await ref.read(feedbackNotifierProvider.notifier).send(
        type:        type,
        title:       _titleCtrl.text.trim(),
        description: _descCtrl.text.trim(),
      );
      _titleCtrl.clear();
      _descCtrl.clear();
      setState(() => _justSent = true);
      await Future.delayed(const Duration(seconds: 3));
      if (mounted) setState(() => _justSent = false);
    } catch (_) {
      // Erreur gérée par le notifier
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

class _TypeButton extends StatelessWidget {
  const _TypeButton({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: selected ? AppColors.accent : Colors.transparent,
            borderRadius: BorderRadius.circular(AppRadius.input),
          ),
          child: Center(
            child: Text(
              label,
              style: AppTextStyles.body2(
                selected ? AppColors.white : AppColors.grey3,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FeedbackItemTile extends StatelessWidget {
  const _FeedbackItemTile({required this.item});

  final FeedbackItem item;

  @override
  Widget build(BuildContext context) {
    final l    = context.l10n;
    final fmt  = DateFormat('dd/MM/yyyy');
    final statusLabel = switch (item.status) {
      FeedbackStatus.pending  => l.feedbackStatusPending,
      FeedbackStatus.inReview => l.feedbackStatusReview,
      FeedbackStatus.done     => l.feedbackStatusDone,
    };
    final statusColor = switch (item.status) {
      FeedbackStatus.pending  => AppColors.yellow,
      FeedbackStatus.inReview => AppColors.blue,
      FeedbackStatus.done     => AppColors.green,
    };

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  item.title,
                  style: AppTextStyles.body1(AppColors.white),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
                child: Text(
                  statusLabel,
                  style: AppTextStyles.caption(statusColor),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            item.description,
            style: AppTextStyles.caption(AppColors.grey3),
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            fmt.format(item.createdAt),
            style: AppTextStyles.caption(AppColors.grey5),
          ),
        ],
      ),
    );
  }
}
