import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';

/// Shown at the top of a screen when the device is offline
/// and the content being displayed is stale cached data.
class OfflineBanner extends StatelessWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: AppColors.warningAmber.withValues(alpha: 0.12),
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.sm,
      ),
      child: Row(
        children: [
          const Icon(
            Icons.wifi_off_outlined,
            size: 16,
            color: AppColors.warningAmber,
          ),
          const SizedBox(width: AppSpacing.sm),
          Text(
            'Showing cached data — pull to refresh when back online.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.warningAmber,
                  fontWeight: FontWeight.w500,
                ),
          ),
        ],
      ),
    );
  }
}

/// Shown when the user tries to perform a network-mandatory action
/// (approve, send application) while offline.
class OfflineActionBanner extends StatelessWidget {
  const OfflineActionBanner({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.warningAmber.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(8),
        border:
            Border.all(color: AppColors.warningAmber.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.wifi_off_outlined,
              size: 16, color: AppColors.warningAmber),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              'This action requires an internet connection.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.warningAmber,
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
