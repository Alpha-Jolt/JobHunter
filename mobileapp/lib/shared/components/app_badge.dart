import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';

enum AppBadgeVariant { info, success, warning, error, neutral }

/// Status badge / pill used on job cards, variant cards, application status.
class AppBadge extends StatelessWidget {
  const AppBadge({
    required this.label,
    this.variant = AppBadgeVariant.neutral,
    this.compact = false,
    super.key,
  });

  final String label;
  final AppBadgeVariant variant;
  final bool compact;

  Color _background() {
    switch (variant) {
      case AppBadgeVariant.success:
        return AppColors.successGreen.withValues(alpha: 0.12);
      case AppBadgeVariant.warning:
        return AppColors.warningAmber.withValues(alpha: 0.12);
      case AppBadgeVariant.error:
        return AppColors.destructive.withValues(alpha: 0.12);
      case AppBadgeVariant.info:
        return AppColors.infoBlue.withValues(alpha: 0.12);
      case AppBadgeVariant.neutral:
        return Colors.grey.withValues(alpha: 0.12);
    }
  }

  Color _foreground() {
    switch (variant) {
      case AppBadgeVariant.success:
        return AppColors.successGreen;
      case AppBadgeVariant.warning:
        return AppColors.warningAmber;
      case AppBadgeVariant.error:
        return AppColors.destructive;
      case AppBadgeVariant.info:
        return AppColors.infoBlue;
      case AppBadgeVariant.neutral:
        return Colors.grey.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 6 : 10,
        vertical: compact ? 2 : 4,
      ),
      decoration: BoxDecoration(
        color: _background(),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: _foreground(),
              fontWeight: FontWeight.w600,
              fontSize: compact ? 10 : 12,
            ),
      ),
    );
  }
}
