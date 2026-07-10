import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';

/// Approval status indicator — first-class component expressing the
/// no-fabrication guarantee visually.
enum ApprovalStatus { pending, approved, rejected, expired }

class ApprovalStatusPill extends StatelessWidget {
  const ApprovalStatusPill({required this.status, super.key});

  final ApprovalStatus status;

  String get _label {
    switch (status) {
      case ApprovalStatus.pending:
        return 'Pending Review';
      case ApprovalStatus.approved:
        return 'Approved';
      case ApprovalStatus.rejected:
        return 'Rejected';
      case ApprovalStatus.expired:
        return 'Expired';
    }
  }

  Color get _color {
    switch (status) {
      case ApprovalStatus.pending:
        return AppColors.warningAmber;
      case ApprovalStatus.approved:
        return AppColors.successGreen;
      case ApprovalStatus.rejected:
        return Colors.grey;
      case ApprovalStatus.expired:
        return AppColors.warningAmber;
    }
  }

  IconData get _icon {
    switch (status) {
      case ApprovalStatus.pending:
        return Icons.hourglass_empty_outlined;
      case ApprovalStatus.approved:
        return Icons.check_circle_outline;
      case ApprovalStatus.rejected:
        return Icons.cancel_outlined;
      case ApprovalStatus.expired:
        return Icons.timer_off_outlined;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: _color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(AppSpacing.xl),
        border: Border.all(color: _color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_icon, size: 14, color: _color),
          const SizedBox(width: 4),
          Text(
            _label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: _color,
                  fontWeight: FontWeight.w600,
                ),
          ),
        ],
      ),
    );
  }
}

/// Parses a raw approval_status string from the API into [ApprovalStatus].
ApprovalStatus parseApprovalStatus(String? raw, {bool tokenExpired = false}) {
  if (tokenExpired) return ApprovalStatus.expired;
  switch (raw) {
    case 'approved':
      return ApprovalStatus.approved;
    case 'rejected':
      return ApprovalStatus.rejected;
    default:
      return ApprovalStatus.pending;
  }
}
