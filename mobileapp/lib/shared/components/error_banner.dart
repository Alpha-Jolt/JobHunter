import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import 'app_button.dart';

/// Inline error banner shown within a screen when a data load fails.
/// [isRetryable] controls whether a Retry button is shown.
class ErrorBanner extends StatelessWidget {
  const ErrorBanner({
    required this.message,
    this.isRetryable = false,
    this.onRetry,
    super.key,
  });

  final String message;
  final bool isRetryable;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: AppColors.destructive.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(AppSpacing.sm),
        border: Border.all(
          color: AppColors.destructive.withValues(alpha: 0.25),
        ),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline,
              color: AppColors.destructive, size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.destructive,
                  ),
            ),
          ),
          if (isRetryable && onRetry != null) ...[
            const SizedBox(width: AppSpacing.sm),
            AppButton(
              label: 'Retry',
              onPressed: onRetry,
              variant: AppButtonVariant.text,
              fullWidth: false,
            ),
          ],
        ],
      ),
    );
  }
}
