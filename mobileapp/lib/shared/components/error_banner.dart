import 'package:flutter/material.dart';
import '../../core/network/app_error.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import 'app_button.dart';

/// Inline error banner shown within a screen when a data load fails.
///
/// Handles three distinct visual tiers:
/// - [AppErrorType.schemaMismatch] — developer-visible contract drift message,
///   no retry (updating the app is the resolution).
/// - [AppErrorType.conflict] — calm, expected business-rule state.
/// - All others — standard retryable or terminal error.
class ErrorBanner extends StatelessWidget {
  const ErrorBanner({
    required this.message,
    this.errorType,
    this.isRetryable = false,
    this.onRetry,
    super.key,
  });

  /// Convenience constructor from an [AppError].
  factory ErrorBanner.fromError(AppError error, {VoidCallback? onRetry}) {
    return ErrorBanner(
      message: error.userMessage,
      errorType: error.type,
      isRetryable: error.isRetryable,
      onRetry: onRetry,
    );
  }

  final String message;
  final AppErrorType? errorType;
  final bool isRetryable;
  final VoidCallback? onRetry;

  bool get _isSchemaMismatch => errorType == AppErrorType.schemaMismatch;
  bool get _isConflict => errorType == AppErrorType.conflict;

  Color _borderColor() {
    if (_isSchemaMismatch) return AppColors.infoBlue.withValues(alpha: 0.3);
    if (_isConflict) return AppColors.warningAmber.withValues(alpha: 0.3);
    return AppColors.destructive.withValues(alpha: 0.25);
  }

  Color _bgColor() {
    if (_isSchemaMismatch) return AppColors.infoBlue.withValues(alpha: 0.07);
    if (_isConflict) return AppColors.warningAmber.withValues(alpha: 0.08);
    return AppColors.destructive.withValues(alpha: 0.08);
  }

  Color _iconColor() {
    if (_isSchemaMismatch) return AppColors.infoBlue;
    if (_isConflict) return AppColors.warningAmber;
    return AppColors.destructive;
  }

  IconData _icon() {
    if (_isSchemaMismatch) return Icons.system_update_outlined;
    if (_isConflict) return Icons.info_outline;
    return Icons.error_outline;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.lg),
      decoration: BoxDecoration(
        color: _bgColor(),
        borderRadius: BorderRadius.circular(AppSpacing.sm),
        border: Border.all(color: _borderColor()),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(_icon(), color: _iconColor(), size: 20),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: _iconColor(),
                  ),
            ),
          ),
          if (isRetryable && onRetry != null && !_isSchemaMismatch) ...[
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
