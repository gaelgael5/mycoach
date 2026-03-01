import 'package:flutter/material.dart';
import '../../../../core/theme/app_colors.dart';

class MessagesScreen extends StatelessWidget {
  const MessagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Messages')),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.chat_bubble_outline, size: 80, color: AppColors.primary.withValues(alpha: 0.3)),
            const SizedBox(height: 16),
            Text('Messagerie à venir', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: AppColors.textSecondary)),
          ],
        ),
      ),
    );
  }
}
