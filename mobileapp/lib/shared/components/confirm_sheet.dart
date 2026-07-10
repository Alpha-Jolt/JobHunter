import 'package:flutter/material.dart';
import '../../core/theme/app_spacing.dart';
import 'app_button.dart';

/// Bottom sheet wrapper for confirmation actions.
/// States: default, loading, error.
/// Used for ApprovalConfirmSheet, ApplicationSendSheet, LogoutConfirmSheet.
class ConfirmSheet extends StatelessWidget {
  const ConfirmSheet({
    required this.title,
    required this.body,
    required this.confirmLabel,
    required this.onConfirm,
    this.cancelLabel = 'Cancel',
    this.onCancel,
    this.isLoading = false,
    this.isDestructive = false,
    this.errorMessage,
    super.key,
  });

  final String title;
  final Widget body;
  final String confirmLabel;
  final VoidCallback? onConfirm;
  final String cancelLabel;
  final VoidCallback? onCancel;
  final bool isLoading;
  final bool isDestructive;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return SafeArea(
      child: Padding(
        padding: EdgeInsets.only(
          left: AppSpacing.lg,
          right: AppSpacing.lg,
          top: AppSpacing.xl2,
          bottom: AppSpacing.xl2 +
              MediaQuery.of(context).viewInsets.bottom,
        ),
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
                  color: colorScheme.outlineVariant,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xl2),
            Text(title, style: theme.textTheme.headlineSmall),
            const SizedBox(height: AppSpacing.lg),
            body,
            if (errorMessage != null) ...[
              const SizedBox(height: AppSpacing.md),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppSpacing.md),
                decoration: BoxDecoration(
                  color: colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  errorMessage!,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onErrorContainer,
                  ),
                ),
              ),
            ],
            const SizedBox(height: AppSpacing.xl2),
            AppButton(
              label: confirmLabel,
              onPressed: isLoading ? null : onConfirm,
              isLoading: isLoading,
              variant: isDestructive
                  ? AppButtonVariant.destructive
                  : AppButtonVariant.primary,
            ),
            const SizedBox(height: AppSpacing.sm),
            AppButton(
              label: cancelLabel,
              onPressed: isLoading ? null : (onCancel ?? () => Navigator.of(context).pop()),
              variant: AppButtonVariant.text,
            ),
          ],
        ),
      ),
    );
  }
}
