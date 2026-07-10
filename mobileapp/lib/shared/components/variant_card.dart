import 'package:flutter/material.dart';
import '../../core/theme/app_spacing.dart';
import 'approval_status_pill.dart';
import 'app_badge.dart';

/// Card representing a resume variant in the approval queue.
/// States: pending, approved, rejected, expired.
class VariantCard extends StatelessWidget {
  const VariantCard({
    required this.variantId,
    required this.jobTitle,
    required this.companyName,
    required this.approvalStatus,
    this.tokenExpiresAt,
    this.matchScore,
    this.onTap,
    super.key,
  });

  final String variantId;
  final String jobTitle;
  final String companyName;

  /// Raw string from API: pending | approved | rejected
  final String approvalStatus;

  /// UTC DateTime of token creation + 24h. Used for expiry check.
  final DateTime? tokenExpiresAt;

  /// Optional match score (0–100) from AI preview.
  final int? matchScore;

  final VoidCallback? onTap;

  bool get _isTokenExpired {
    if (tokenExpiresAt == null) return false;
    return DateTime.now().toUtc().isAfter(tokenExpiresAt!);
  }

  bool get _isTokenNearExpiry {
    if (tokenExpiresAt == null) return false;
    final remaining = tokenExpiresAt!.difference(DateTime.now().toUtc());
    return remaining.inHours <= 4 && remaining.inSeconds > 0;
  }

  ApprovalStatus get _parsedStatus =>
      parseApprovalStatus(approvalStatus, tokenExpired: _isTokenExpired);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Card(
      margin: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg,
        vertical: AppSpacing.sm,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Title + match score
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      jobTitle,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (matchScore != null) ...[
                    const SizedBox(width: AppSpacing.sm),
                    AppBadge(
                      label: '$matchScore%',
                      variant: matchScore! >= 70
                          ? AppBadgeVariant.success
                          : matchScore! >= 45
                              ? AppBadgeVariant.warning
                              : AppBadgeVariant.error,
                    ),
                  ],
                ],
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                companyName,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: AppSpacing.sm),
              Row(
                children: [
                  ApprovalStatusPill(status: _parsedStatus),
                  if (_isTokenNearExpiry) ...[
                    const SizedBox(width: AppSpacing.sm),
                    _expiryWarning(context),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _expiryWarning(BuildContext context) {
    final remaining =
        tokenExpiresAt!.difference(DateTime.now().toUtc());
    return Text(
      'Expires in ${remaining.inHours}h',
      style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.orange,
            fontWeight: FontWeight.w600,
          ),
    );
  }
}
