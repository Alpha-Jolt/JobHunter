import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/connectivity_service.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/offline_banner.dart';
import '../providers/variants_provider.dart';

/// Approval confirmation bottom sheet.
/// Only opens after a live approval token has been successfully fetched.
/// The token is held in [ApprovalFlowNotifier] — never passed through the UI.
/// Network-mandatory: blocked with explicit message when offline.
class ApprovalConfirmSheet extends ConsumerWidget {
  const ApprovalConfirmSheet({required this.variantId, super.key});

  final String variantId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final flowState = ref.watch(approvalFlowProvider);
    final connectivity = ref.watch(connectivityStreamProvider);
    final online = connectivity.whenOrNull(data: isOnline) ?? true;
    final theme = Theme.of(context);

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl2),
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
                  color: theme.colorScheme.outlineVariant,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xl2),
            Text('Approve Variant?', style: theme.textTheme.headlineSmall),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'By approving, you confirm that the content in this variant '
              'accurately represents your experience and qualifications. '
              'You will then be able to send applications using this variant.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.md),
            Container(
              padding: const EdgeInsets.all(AppSpacing.sm),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.info_outline, size: 16),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'Approval is valid for 24 hours.',
                      style: theme.textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            ),
            // Offline guard — approval is network-mandatory, always fail-closed
            if (!online) ...[
              const SizedBox(height: AppSpacing.md),
              const OfflineActionBanner(),
            ],
            if (flowState.errorMessage != null) ...[
              const SizedBox(height: AppSpacing.md),
              ErrorBanner(message: flowState.errorMessage!),
            ],
            const SizedBox(height: AppSpacing.xl2),
            AppButton(
              label: 'Approve',
              // Blocked when offline or busy — fail-closed per plan
              onPressed: (!online || flowState.isBusy)
                  ? null
                  : () async {
                      final success = await ref
                          .read(approvalFlowProvider.notifier)
                          .approve(variantId);
                      if (success && context.mounted) {
                        Navigator.of(context).pop();
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                              'Variant approved. You can now send an application.',
                            ),
                          ),
                        );
                      }
                    },
              isLoading: flowState.isBusy,
              icon: Icons.check_circle_outline,
            ),
            const SizedBox(height: AppSpacing.sm),
            AppButton(
              label: 'Cancel',
              onPressed: flowState.isBusy
                  ? null
                  : () {
                      ref.read(approvalFlowProvider.notifier).reset();
                      Navigator.of(context).pop();
                    },
              variant: AppButtonVariant.text,
            ),
          ],
        ),
      ),
    );
  }
}
