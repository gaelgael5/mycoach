import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:sms_autofill/sms_autofill.dart';
import '../../../../core/api/api_exception.dart';
import '../../../../core/extensions/context_ext.dart';
import '../../../../core/router/router.dart';
import '../../../../core/theme/app_theme.dart';
import '../providers/auth_providers.dart';
import '../widgets/auth_form_widgets.dart';
import '../widgets/gradient_button.dart';

/// Écran OTP SMS — 6 cases style PIN avec auto-remplissage SMS.
/// Flow post-inscription coach : OtpSmsScreen → EmailVerificationScreen
class OtpSmsScreen extends ConsumerStatefulWidget {
  const OtpSmsScreen({super.key});

  @override
  ConsumerState<OtpSmsScreen> createState() => _OtpSmsScreenState();
}

class _OtpSmsScreenState extends ConsumerState<OtpSmsScreen> with CodeAutoFill {
  static const _codeLength = 6;
  static const _cooldownSeconds = 60;

  final List<TextEditingController> _controllers =
      List.generate(_codeLength, (_) => TextEditingController());
  final List<FocusNode> _focusNodes =
      List.generate(_codeLength, (_) => FocusNode());

  bool _isVerifying = false;
  bool _isResending = false;
  String? _errorMessage;
  bool _autoFilled = false;

  int _cooldown = 0;
  Timer? _cooldownTimer;

  @override
  void initState() {
    super.initState();
    listenForCode();
  }

  @override
  void codeUpdated() {
    final smsCode = this.code ?? '';
    if (smsCode.length == _codeLength) {
      _fillCode(smsCode);
      if (mounted) setState(() => _autoFilled = true);
    }
  }

  void _fillCode(String c) {
    final chars = c.toLowerCase().split('');
    for (var i = 0; i < _codeLength && i < chars.length; i++) {
      _controllers[i].text = chars[i];
    }
    if (mounted) _focusNodes[_codeLength - 1].requestFocus();
  }

  String get _currentCode => _controllers.map((c) => c.text).join();

  String get _phone {
    final user = ref.read(authStateProvider).valueOrNull;
    return user?.phone ?? '';
  }

  Future<void> _verify() async {
    final code = _currentCode;
    if (code.length < _codeLength) return;
    setState(() {
      _isVerifying = true;
      _errorMessage = null;
      _autoFilled = false;
    });
    try {
      final ok =
          await ref.read(authServiceProvider).confirmPhoneVerification(code);
      if (mounted) {
        if (ok) {
          context.go(AppRoutes.verifyEmail);
        } else {
          setState(() => _errorMessage = context.l10n.otpInvalid(3));
        }
      }
    } catch (e) {
      if (mounted) {
        final errCode = extractApiErrorCode(e);
        setState(() {
          _errorMessage = switch (errCode) {
            ApiErrorCode.invalidOtp => context.l10n.otpInvalid(3),
            ApiErrorCode.otpMaxAttempts => context.l10n.otpMaxAttempts,
            _ => context.l10n.errorGeneric,
          };
        });
      }
    } finally {
      if (mounted) setState(() => _isVerifying = false);
    }
  }

  Future<void> _resend() async {
    setState(() {
      _isResending = true;
      _errorMessage = null;
    });
    try {
      await ref.read(authServiceProvider).requestPhoneVerification();
      if (mounted) {
        _startCooldown();
        for (final c in _controllers) c.clear();
        _focusNodes[0].requestFocus();
      }
    } catch (_) {
      if (mounted) setState(() => _errorMessage = context.l10n.errorGeneric);
    } finally {
      if (mounted) setState(() => _isResending = false);
    }
  }

  void _startCooldown() {
    setState(() => _cooldown = _cooldownSeconds);
    _cooldownTimer?.cancel();
    _cooldownTimer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (_cooldown <= 1) {
        t.cancel();
        if (mounted) setState(() => _cooldown = 0);
      } else {
        if (mounted) setState(() => _cooldown--);
      }
    });
  }

  void _onPinChanged(int index, String value) {
    if (value.isNotEmpty && index < _codeLength - 1) {
      _focusNodes[index + 1].requestFocus();
    }
  }

  void _onBackspace(int index) {
    if (_controllers[index].text.isEmpty && index > 0) {
      _controllers[index - 1].clear();
      _focusNodes[index - 1].requestFocus();
    }
  }

  @override
  void dispose() {
    cancel();
    _cooldownTimer?.cancel();
    for (final c in _controllers) c.dispose();
    for (final f in _focusNodes) f.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isComplete = _currentCode.length == _codeLength;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        backgroundColor: AppColors.bgDark,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: AppColors.grey1),
          onPressed: () => context.go(AppRoutes.registerCoach),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 24),
              Center(
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppColors.accent.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.sms_outlined,
                    color: AppColors.accent,
                    size: 36,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                context.l10n.otpTitle,
                style: AppTextStyles.headline2(AppColors.white),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
              if (_phone.isNotEmpty)
                Text(
                  context.l10n.otpSubtitle(_phone),
                  style: AppTextStyles.body1(AppColors.grey3),
                  textAlign: TextAlign.center,
                ),
              const SizedBox(height: 40),

              // Auto-fill feedback
              if (_autoFilled) ...[
                Text(
                  context.l10n.otpAutoFilled,
                  style: AppTextStyles.body2(AppColors.green),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
              ],

              // PIN boxes
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: List.generate(
                  _codeLength,
                  (i) => _PinBox(
                    controller: _controllers[i],
                    focusNode: _focusNodes[i],
                    onChanged: (v) => _onPinChanged(i, v),
                    onBackspace: () => _onBackspace(i),
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Error
              if (_errorMessage != null) ...[
                AuthErrorBanner(message: _errorMessage!),
                const SizedBox(height: 16),
              ],

              // Verify
              GradientButton(
                label: context.l10n.otpVerifyButton,
                onPressed: (isComplete && !_isVerifying) ? _verify : null,
                isLoading: _isVerifying,
              ),
              const SizedBox(height: 16),

              // Resend
              Center(
                child: _cooldown > 0
                    ? Text(
                        context.l10n.otpResendCooldown(_cooldown),
                        style: AppTextStyles.body2(AppColors.grey5),
                      )
                    : TextButton(
                        onPressed: _isResending ? null : _resend,
                        child: Text(context.l10n.otpResend),
                      ),
              ),

              // Change number
              Center(
                child: TextButton(
                  onPressed: () => context.go(AppRoutes.registerCoach),
                  child: Text(
                    context.l10n.otpWrongNumber,
                    style: AppTextStyles.body2(AppColors.grey5),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── PIN Box ────────────────────────────────────────────────────────────────────

class _PinBox extends StatelessWidget {
  const _PinBox({
    required this.controller,
    required this.focusNode,
    required this.onChanged,
    required this.onBackspace,
  });

  final TextEditingController controller;
  final FocusNode focusNode;
  final ValueChanged<String> onChanged;
  final VoidCallback onBackspace;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 46,
      height: 56,
      child: RawKeyboardListener(
        focusNode: FocusNode(),
        onKey: (event) {
          if (event is RawKeyDownEvent &&
              event.logicalKey == LogicalKeyboardKey.backspace &&
              controller.text.isEmpty) {
            onBackspace();
          }
        },
        child: TextFormField(
          controller: controller,
          focusNode: focusNode,
          maxLength: 1,
          keyboardType: TextInputType.visiblePassword,
          textAlign: TextAlign.center,
          style: AppTextStyles.headline3(AppColors.white),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'[0-9a-z]')),
          ],
          decoration: InputDecoration(
            counterText: '',
            contentPadding: EdgeInsets.zero,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppRadius.input),
              borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppRadius.input),
              borderSide: BorderSide(color: AppColors.grey7, width: 1.5),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppRadius.input),
              borderSide: BorderSide(color: AppColors.accent, width: 2),
            ),
            filled: true,
            fillColor: AppColors.bgInput,
          ),
          onChanged: (v) {
            if (v.length > 1) {
              controller.text = v[v.length - 1];
              controller.selection = TextSelection.fromPosition(
                TextPosition(offset: controller.text.length),
              );
            }
            onChanged(controller.text);
          },
        ),
      ),
    );
  }
}
