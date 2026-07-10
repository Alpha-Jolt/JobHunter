import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';

/// Displays an identified skill gap.
/// ALWAYS labelled as absent — never styled as a present skill.
/// Rule: gap chips must never carry a checkmark, green color, or
/// any neutral styling that could be mistaken for a confirmed skill.
class GapTagChip extends StatelessWidget {
  const GapTagChip({required this.gap, super.key});

  final String gap;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: AppColors.warningAmber.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppSpacing.xl),
        border: Border.all(
          color: AppColors.warningAmber.withValues(alpha: 0.35),
          style: BorderStyle.solid,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.add_circle_outline,
            size: 12,
            color: AppColors.warningAmber,
          ),
          const SizedBox(width: 4),
          Text(
            '$gap — not in your resume',
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
