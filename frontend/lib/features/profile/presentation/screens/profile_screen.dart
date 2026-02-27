import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../features/auth/presentation/providers/auth_providers.dart';
import '../../../../shared/models/user.dart';
import '../../../../shared/widgets/avatar_widget.dart';
import '../providers/profile_providers.dart';

/// Écran principal du profil utilisateur.
class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;
    final profileAsync = ref.watch(profileNotifierProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        title: Text(l.profileTitle),
      ),
      body: profileAsync.when(
        loading: () => const Center(
          child: CircularProgressIndicator(color: AppColors.accent),
        ),
        error: (e, _) => _ErrorView(message: e.toString(), onRetry: () {
          ref.read(profileNotifierProvider.notifier).load();
        }),
        data: (user) => user == null
            ? const SizedBox.shrink()
            : _ProfileBody(user: user),
      ),
    );
  }
}

class _ProfileBody extends ConsumerWidget {
  const _ProfileBody({required this.user});

  final User user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ─ En-tête avatar + nom ─────────────────────────────────────────
          _ProfileHeader(user: user),
          const SizedBox(height: 24),

          // ─ Informations personnelles ────────────────────────────────────
          _InfoCard(user: user),
          const SizedBox(height: 24),

          // ─ Accès rapide ─────────────────────────────────────────────────
          Text(l.profileSettings, style: AppTextStyles.label(AppColors.grey3)),
          const SizedBox(height: 8),
          _QuickAccessList(),
          const SizedBox(height: 24),

          // ─ Bouton déconnexion ───────────────────────────────────────────
          _LogoutButton(),
        ],
      ),
    );
  }
}

class _ProfileHeader extends ConsumerStatefulWidget {
  const _ProfileHeader({required this.user});

  final User user;

  @override
  ConsumerState<_ProfileHeader> createState() => _ProfileHeaderState();
}

class _ProfileHeaderState extends ConsumerState<_ProfileHeader> {
  @override
  Widget build(BuildContext context) {
    final l = context.l10n;
    final user = widget.user;

    return Row(
      children: [
        AvatarWidget(
          avatarUrl: user.resolvedAvatarUrl,
          gender: user.gender,
          size: 80,
          editable: true,
          onEditTap: _pickImage,
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                user.fullName,
                style: AppTextStyles.headline3(AppColors.white),
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 3,
                ),
                decoration: BoxDecoration(
                  color: AppColors.accentGlow,
                  borderRadius: BorderRadius.circular(AppRadius.pill),
                ),
                child: Text(
                  user.role.value.toUpperCase(),
                  style: AppTextStyles.caption(AppColors.accent),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                user.email,
                style: AppTextStyles.caption(AppColors.grey3),
              ),
            ],
          ),
        ),
        IconButton(
          icon: const Icon(Icons.edit_outlined, color: AppColors.grey3),
          onPressed: () => _showEditSheet(context),
          tooltip: l.profileEdit,
        ),
      ],
    );
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final xFile = await picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 80,
    );
    if (xFile == null) return;
    await ref
        .read(profileNotifierProvider.notifier)
        .uploadAvatar(File(xFile.path));
  }

  void _showEditSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgCard,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => _EditProfileSheet(user: widget.user),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.user});

  final User user;

  @override
  Widget build(BuildContext context) {
    final l = context.l10n;

    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7),
      ),
      child: Column(
        children: [
          _InfoRow(label: l.labelFirstName, value: user.firstName),
          _divider(),
          _InfoRow(label: l.labelLastName, value: user.lastName),
          _divider(),
          _InfoRow(label: l.labelEmail, value: user.email),
          if (user.phone != null) ...[
            _divider(),
            _InfoRow(label: l.labelPhone, value: user.phone!),
          ],
          if (user.birthYear != null) ...[
            _divider(),
            _InfoRow(
              label: l.labelBirthYear,
              value: user.birthYear.toString(),
            ),
          ],
          if (user.gender != null) ...[
            _divider(),
            _InfoRow(
              label: l.labelGender,
              value: _genderLabel(context, user.gender!),
            ),
          ],
        ],
      ),
    );
  }

  Widget _divider() => Divider(
    height: 1,
    thickness: 1,
    color: AppColors.grey7,
    indent: 16,
    endIndent: 16,
  );

  String _genderLabel(BuildContext context, Gender gender) {
    final l = context.l10n;
    switch (gender) {
      case Gender.male:   return l.genderMale;
      case Gender.female: return l.genderFemale;
      case Gender.other:  return l.genderOther;
    }
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      child: Row(
        children: [
          Text(label, style: AppTextStyles.label(AppColors.grey3)),
          const Spacer(),
          Text(
            value,
            style: AppTextStyles.body2(AppColors.white),
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

class _QuickAccessList extends StatelessWidget {
  const _QuickAccessList();

  @override
  Widget build(BuildContext context) {
    final l = context.l10n;
    final items = [
      _QuickItem(
        icon: Icons.link,
        label: l.profileSocialLinks,
        onTap: () => context.push(AppRoutes.profileSocialLinks),
      ),
      _QuickItem(
        icon: Icons.monitor_heart_outlined,
        label: l.profileHealthParams,
        onTap: () => context.push(AppRoutes.profileHealthParams),
      ),
      _QuickItem(
        icon: Icons.share_outlined,
        label: l.profileHealthSharing,
        onTap: () => context.push(AppRoutes.profileHealthSharing),
      ),
      _QuickItem(
        icon: Icons.shield_outlined,
        label: l.profilePrivacy,
        onTap: () => context.push(AppRoutes.profilePrivacy),
      ),
      _QuickItem(
        icon: Icons.notifications_outlined,
        label: l.profileNotifications,
        onTap: () => context.push(AppRoutes.profileNotifications),
      ),
      _QuickItem(
        icon: Icons.feedback_outlined,
        label: l.profileFeedback,
        onTap: () => context.push(AppRoutes.profileFeedback),
      ),
    ];

    return Container(
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(AppRadius.card),
        border: Border.all(color: AppColors.grey7),
      ),
      child: Column(
        children: items.asMap().entries.map((e) {
          final isLast = e.key == items.length - 1;
          return Column(
            children: [
              e.value,
              if (!isLast)
                Divider(
                  height: 1,
                  thickness: 1,
                  color: AppColors.grey7,
                  indent: 52,
                ),
            ],
          );
        }).toList(),
      ),
    );
  }
}

class _QuickItem extends StatelessWidget {
  const _QuickItem({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppRadius.card),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Icon(icon, color: AppColors.grey3, size: 20),
            const SizedBox(width: 12),
            Text(label, style: AppTextStyles.body1(AppColors.white)),
            const Spacer(),
            const Icon(
              Icons.chevron_right,
              color: AppColors.grey5,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}

class _LogoutButton extends ConsumerWidget {
  const _LogoutButton();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l = context.l10n;
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        onPressed: () => _confirmLogout(context, ref),
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.red,
          side: const BorderSide(color: AppColors.red),
        ),
        child: Text(l.profileLogout),
      ),
    );
  }

  Future<void> _confirmLogout(BuildContext context, WidgetRef ref) async {
    final l = context.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: AppColors.bgCard,
        title: Text(l.profileLogout, style: AppTextStyles.headline4(AppColors.white)),
        content: Text(
          l.profileLogoutConfirm,
          style: AppTextStyles.body1(AppColors.grey3),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(l.btnCancel),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: AppColors.red),
            child: Text(l.profileLogout),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ref.read(authStateProvider.notifier).logout();
    }
  }
}

// ── Formulaire d'édition ─────────────────────────────────────────────────────

class _EditProfileSheet extends ConsumerStatefulWidget {
  const _EditProfileSheet({required this.user});

  final User user;

  @override
  ConsumerState<_EditProfileSheet> createState() => _EditProfileSheetState();
}

class _EditProfileSheetState extends ConsumerState<_EditProfileSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _firstNameCtrl;
  late final TextEditingController _lastNameCtrl;
  late final TextEditingController _phoneCtrl;
  late final TextEditingController _birthYearCtrl;
  String? _selectedGender;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _firstNameCtrl = TextEditingController(text: widget.user.firstName);
    _lastNameCtrl  = TextEditingController(text: widget.user.lastName);
    _phoneCtrl     = TextEditingController(text: widget.user.phone ?? '');
    _birthYearCtrl = TextEditingController(
      text: widget.user.birthYear?.toString() ?? '',
    );
    _selectedGender = widget.user.gender?.value;
  }

  @override
  void dispose() {
    _firstNameCtrl.dispose();
    _lastNameCtrl.dispose();
    _phoneCtrl.dispose();
    _birthYearCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l = context.l10n;
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 24,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(l.profileEdit,
                      style: AppTextStyles.headline4(AppColors.white)),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppColors.grey3),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _buildField(l.labelFirstName, _firstNameCtrl, required: true),
              const SizedBox(height: 12),
              _buildField(l.labelLastName, _lastNameCtrl, required: true),
              const SizedBox(height: 12),
              _buildField(l.labelPhone, _phoneCtrl, keyboardType: TextInputType.phone),
              const SizedBox(height: 12),
              _buildField(l.labelBirthYear, _birthYearCtrl,
                  keyboardType: TextInputType.number),
              const SizedBox(height: 12),
              Text(l.labelGender, style: AppTextStyles.label(AppColors.grey3)),
              const SizedBox(height: 8),
              Row(
                children: [
                  _GenderChip(
                    label: l.genderMale,
                    selected: _selectedGender == 'male',
                    onTap: () => setState(() => _selectedGender = 'male'),
                  ),
                  const SizedBox(width: 8),
                  _GenderChip(
                    label: l.genderFemale,
                    selected: _selectedGender == 'female',
                    onTap: () => setState(() => _selectedGender = 'female'),
                  ),
                  const SizedBox(width: 8),
                  _GenderChip(
                    label: l.genderOther,
                    selected: _selectedGender == 'other',
                    onTap: () => setState(() => _selectedGender = 'other'),
                  ),
                ],
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
      ),
    );
  }

  Widget _buildField(
    String label,
    TextEditingController ctrl, {
    bool required = false,
    TextInputType keyboardType = TextInputType.text,
  }) {
    final l = context.l10n;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTextStyles.label(AppColors.grey3)),
        const SizedBox(height: 6),
        TextFormField(
          controller: ctrl,
          style: AppTextStyles.body1(AppColors.white),
          keyboardType: keyboardType,
          validator: required
              ? (v) => (v == null || v.trim().isEmpty)
                  ? l.validationRequired
                  : null
              : null,
        ),
      ],
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    try {
      await ref.read(profileNotifierProvider.notifier).updateProfile(
        firstName: _firstNameCtrl.text.trim(),
        lastName:  _lastNameCtrl.text.trim(),
        gender:    _selectedGender,
        birthYear: int.tryParse(_birthYearCtrl.text.trim()),
        phone:     _phoneCtrl.text.trim().isEmpty
            ? null
            : _phoneCtrl.text.trim(),
      );
      if (mounted) Navigator.of(context).pop();
    } catch (_) {
      // Erreur gérée par le notifier
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }
}

class _GenderChip extends StatelessWidget {
  const _GenderChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.accent.withOpacity(0.2)
              : AppColors.bgCard,
          borderRadius: BorderRadius.circular(AppRadius.pill),
          border: Border.all(
            color: selected ? AppColors.accent : AppColors.grey7,
          ),
        ),
        child: Text(
          label,
          style: AppTextStyles.caption(
            selected ? AppColors.accent : AppColors.grey3,
          ),
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final l = context.l10n;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, color: AppColors.red, size: 48),
          const SizedBox(height: 12),
          Text(l.errorGeneric, style: AppTextStyles.body1(AppColors.grey3)),
          const SizedBox(height: 12),
          TextButton(
            onPressed: onRetry,
            child: Text(l.btnRetry),
          ),
        ],
      ),
    );
  }
}
