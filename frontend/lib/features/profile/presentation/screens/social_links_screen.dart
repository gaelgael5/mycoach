import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/social_links_providers.dart';
import '../widgets/add_social_link_sheet.dart';
import '../widgets/social_link_tile.dart';

/// Écran de gestion des liens sociaux.
class SocialLinksScreen extends ConsumerWidget {
  const SocialLinksScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;
    final linksAsync = ref.watch(socialLinksNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.socialLinksTitle),
      ),
      body: linksAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) => Center(
          child: Text(l.errorGeneric,
              style: AppTextStyles.body1(AppColors.grey3)),
        ),
        data: (links) {
          final count = links.length;
          return Column(
            children: [
              // Compteur
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: 20, vertical: 10),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      l.socialLinksMax(count),
                      style: AppTextStyles.caption(AppColors.grey3),
                    ),
                    if (count < 20)
                      TextButton.icon(
                        onPressed: () => _showAddSheet(context),
                        icon: const Icon(Icons.add, size: 16),
                        label: Text(l.socialLinksAdd),
                      ),
                  ],
                ),
              ),
              Expanded(
                child: links.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.link_off,
                                color: AppColors.grey5, size: 48),
                            const SizedBox(height: 12),
                            Text(
                              l.socialLinksAdd,
                              style: AppTextStyles.body1(AppColors.grey3),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(20),
                        itemCount: links.length,
                        itemBuilder: (context, index) {
                          final link = links[index];
                          return SocialLinkTile(
                            link: link,
                            onDelete: () => ref
                                .read(socialLinksNotifierProvider.notifier)
                                .deleteLink(link.id),
                          );
                        },
                      ),
              ),
            ],
          );
        },
      ),
      floatingActionButton: linksAsync.valueOrNull != null &&
              (linksAsync.valueOrNull?.length ?? 0) < 20
          ? FloatingActionButton(
              onPressed: () => _showAddSheet(context),
              backgroundColor: AppColors.accent,
              child: const Icon(Icons.add, color: AppColors.white),
            )
          : null,
    );
  }

  void _showAddSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => const AddSocialLinkSheet(),
    );
  }
}
