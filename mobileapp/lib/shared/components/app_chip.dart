import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_spacing.dart';

/// Selectable chip for filters and skill tags.
/// States: default, selected, disabled.
class AppChip extends StatelessWidget {
  const AppChip({
    required this.label,
    this.isSelected = false,
    this.isDisabled = false,
    this.onTap,
    super.key,
  });

  final String label;
  final bool isSelected;
  final bool isDisabled;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final backgroundColor = isSelected
        ? AppColors.brandOrange
        : colorScheme.surfaceContainerHighest;
    final labelColor = isSelected
        ? AppColors.primaryForeground
        : isDisabled
            ? colorScheme.onSurface.withValues(alpha: 0.38)
            : colorScheme.onSurface;
    final borderColor =
        isSelected ? AppColors.brandOrange : colorScheme.outline;

    return GestureDetector(
      onTap: isDisabled ? null : onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md,
          vertical: AppSpacing.xs,
        ),
        decoration: BoxDecoration(
          color: isDisabled
              ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.5)
              : backgroundColor,
          borderRadius: BorderRadius.circular(AppRadius.full),
          border: Border.all(color: borderColor),
        ),
        child: Text(
          label,
          style: theme.textTheme.labelMedium?.copyWith(color: labelColor),
        ),
      ),
    );
  }
}
