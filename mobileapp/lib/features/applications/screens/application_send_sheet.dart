import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/network/connectivity_service.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_text_field.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/offline_banner.dart';
import '../../auth/providers/session_provider.dart';
import '../data/application_models.dart';
import '../providers/applications_provider.dart';

/// Bottom sheet to confirm and send a job application.
/// Requires an approved variant ID (passed as extra or constructor param).
/// This is a network-mandatory action — no offline fallback.
class ApplicationSendSheet extends ConsumerStatefulWidget {
  const ApplicationSendSheet({
    required this.jobId,
    required this.variantId,
    this.jobTitle,
    this.companyName,
    super.key,
  });

  final String jobId;
  final String variantId;
  final String? jobTitle;
  final String? companyName;

  @override
  ConsumerState<ApplicationSendSheet> createState() =>
      _ApplicationSendSheetState();
}

class _ApplicationSendSheetState extends ConsumerState<ApplicationSendSheet> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameCtrl;
  late TextEditingController _emailCtrl;
  late TextEditingController _phoneCtrl;
  late TextEditingController _summaryCtrl;

  @override
  void initState() {
    super.initState();
    final session = ref.read(sessionProvider);
    final user = session.user;
    _nameCtrl = TextEditingController(
      text: '${user?.firstName ?? ''} ${user?.lastName ?? ''}'.trim(),
    );
    _emailCtrl = TextEditingController(text: user?.email ?? '');
    _phoneCtrl = TextEditingController(text: user?.phone ?? '');
    _summaryCtrl = TextEditingController();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _summaryCtrl.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    if (!_formKey.currentState!.validate()) return;

    final session = ref.read(sessionProvider);
    final userId = session.user?.userId;
    if (userId == null) return;

    final success = await ref
        .read(sendApplicationProvider.notifier)
        .send(
          SendApplicationRequest(
            userId: userId,
            jobId: widget.jobId,
            variantId: widget.variantId,
            userName: _nameCtrl.text.trim(),
            userEmail: _emailCtrl.text.trim(),
            userPhone: _phoneCtrl.text.trim().isEmpty
                ? null
                : _phoneCtrl.text.trim(),
            userSummary: _summaryCtrl.text.trim().isEmpty
                ? null
                : _summaryCtrl.text.trim(),
          ),
        );

    if (success && mounted) {
      Navigator.of(context).pop();
      context.go('/applications');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Application sent successfully!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final sendState = ref.watch(sendApplicationProvider);
    final connectivity = ref.watch(connectivityStreamProvider);
    final online = connectivity.whenOrNull(data: isOnline) ?? true;
    final theme = Theme.of(context);

    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppSpacing.xl2),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Drag handle
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: theme.colorScheme.outlineVariant,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.xl2),
                Text('Send Application', style: theme.textTheme.headlineSmall),
                if (widget.jobTitle != null || widget.companyName != null) ...[
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    [widget.jobTitle, widget.companyName]
                        .whereType<String>()
                        .join(' · '),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
                const SizedBox(height: AppSpacing.xl2),
                AppTextField(
                  controller: _nameCtrl,
                  label: 'Your Name',
                  hint: 'Full name as it appears on your resume',
                  validator: (v) =>
                      (v == null || v.trim().isEmpty) ? 'Required' : null,
                ),
                const SizedBox(height: AppSpacing.lg),
                AppTextField(
                  controller: _emailCtrl,
                  label: 'Your Email',
                  hint: 'you@example.com',
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) {
                    if (v == null || v.trim().isEmpty) return 'Required';
                    if (!v.contains('@')) return 'Enter a valid email';
                    return null;
                  },
                ),
                const SizedBox(height: AppSpacing.lg),
                AppTextField(
                  controller: _phoneCtrl,
                  label: 'Phone (optional)',
                  hint: '+91 98765 43210',
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: AppSpacing.lg),
                AppTextField(
                  controller: _summaryCtrl,
                  label: 'Brief Note (optional)',
                  hint: 'One line to personalise your application',
                  keyboardType: TextInputType.multiline,
                  maxLines: 3,
                ),
                if (sendState.errorMessage != null) ...[
                  const SizedBox(height: AppSpacing.md),
                  ErrorBanner(message: sendState.errorMessage!),
                ],
                if (!online) ...[
                  const SizedBox(height: AppSpacing.md),
                  const OfflineActionBanner(),
                ],
                const SizedBox(height: AppSpacing.xl2),
                AppButton(
                  label: 'Send Application',
                  onPressed: (!online || sendState.isSending) ? null : _send,
                  isLoading: sendState.isSending,
                  icon: Icons.send_outlined,
                ),
                const SizedBox(height: AppSpacing.sm),
                AppButton(
                  label: 'Cancel',
                  onPressed: sendState.isSending
                      ? null
                      : () => Navigator.of(context).pop(),
                  variant: AppButtonVariant.text,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
