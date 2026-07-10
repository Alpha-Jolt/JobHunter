import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';
import 'app_badge.dart';
import 'email_trust_badge.dart';

/// Card displaying a single job listing with status and trust signal.
/// States: default, selected, applied, closed.
class JobCard extends StatelessWidget {
  const JobCard({
    required this.jobId,
    required this.title,
    required this.companyName,
    required this.location,
    required this.status,
    required this.emailTrust,
    this.remoteType,
    this.jobType,
    this.salaryMin,
    this.salaryMax,
    this.isSelected = false,
    this.onTap,
    this.onLongPress,
    super.key,
  });

  final String jobId;
  final String title;
  final String companyName;
  final String location;

  /// Values: raw, reviewed, applied, closed
  final String status;

  /// Values: unknown, verified, low
  final String emailTrust;

  final String? remoteType;
  final String? jobType;
  final int? salaryMin;
  final int? salaryMax;
  final bool isSelected;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;

  bool get _isClosed => status == 'closed';
  bool get _isApplied => status == 'applied';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return AnimatedOpacity(
      duration: const Duration(milliseconds: 150),
      opacity: _isClosed ? 0.55 : 1.0,
      child: Card(
        margin: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.sm,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: isSelected
              ? const BorderSide(color: AppColors.brandOrange, width: 2)
              : BorderSide(color: colorScheme.outlineVariant),
        ),
        color: isSelected
            ? AppColors.brandOrange.withValues(alpha: 0.06)
            : colorScheme.surface,
        child: InkWell(
          onTap: onTap,
          onLongPress: onLongPress,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Title row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: _isClosed
                              ? colorScheme.onSurface.withValues(alpha: 0.5)
                              : colorScheme.onSurface,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    _statusBadge(),
                  ],
                ),
                const SizedBox(height: AppSpacing.xs),
                // Company & location
                Text(
                  '$companyName · $location',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: AppSpacing.sm),
                // Tags row
                Wrap(
                  spacing: AppSpacing.xs,
                  runSpacing: AppSpacing.xs,
                  children: [
                    if (remoteType != null && remoteType != 'onsite')
                      _tagChip(context, _remoteLabel(remoteType!)),
                    if (jobType != null)
                      _tagChip(context, _jobTypeLabel(jobType!)),
                    if (salaryMin != null || salaryMax != null)
                      _tagChip(context, _salaryLabel()),
                    EmailTrustBadge(trust: emailTrust),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _statusBadge() {
    if (_isApplied) {
      return const AppBadge(
        label: 'Applied',
        variant: AppBadgeVariant.success,
      );
    }
    if (_isClosed) {
      return const AppBadge(
        label: 'Closed',
        variant: AppBadgeVariant.neutral,
      );
    }
    return const SizedBox.shrink();
  }

  Widget _tagChip(BuildContext context, String label) {
    final colorScheme = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
            ),
      ),
    );
  }

  String _remoteLabel(String type) {
    switch (type) {
      case 'remote':
        return 'Remote';
      case 'hybrid':
        return 'Hybrid';
      default:
        return type;
    }
  }

  String _jobTypeLabel(String type) {
    switch (type) {
      case 'fulltime':
        return 'Full-time';
      case 'parttime':
        return 'Part-time';
      case 'contract':
        return 'Contract';
      case 'internship':
        return 'Internship';
      case 'freelance':
        return 'Freelance';
      default:
        return type;
    }
  }

  String _salaryLabel() {
    if (salaryMin != null && salaryMax != null) {
      return '₹${_fmt(salaryMin!)} – ₹${_fmt(salaryMax!)}';
    }
    if (salaryMin != null) return '₹${_fmt(salaryMin!)}+';
    if (salaryMax != null) return 'Up to ₹${_fmt(salaryMax!)}';
    return '';
  }

  String _fmt(int value) {
    if (value >= 100000) {
      return '${(value / 100000).toStringAsFixed(1)}L';
    }
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(0)}K';
    }
    return value.toString();
  }
}
