import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/utils/secure_screen_mixin.dart';
import '../../../shared/components/app_badge.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/approval_status_pill.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/gap_tag_chip.dart';
import '../../applications/screens/application_send_sheet.dart';
import '../providers/variants_provider.dart';
import 'approval_confirm_sheet.dart';

/// Displays the curated resume variant in three clearly-labelled sections:
/// 1. Unchanged content (from your resume)
/// 2. Reordered / rephrased content
/// 3. Identified gaps (NEVER presented as present skills)
///
/// FLAG_SECURE is active on Android while this screen is visible —
/// prevents screenshots and recents-thumbnail leakage of resume content.
class VariantDetailScreen extends ConsumerStatefulWidget {
  const VariantDetailScreen({required this.variantId, super.key});

  final String variantId;

  @override
  ConsumerState<VariantDetailScreen> createState() =>
      _VariantDetailScreenState();
}

class _VariantDetailScreenState extends ConsumerState<VariantDetailScreen>
    with SecureScreenMixin {
  @override
  Widget build(BuildContext context) {
    final previewAsync = ref.watch(variantPreviewProvider(widget.variantId));

    return Scaffold(
      appBar: AppBar(title: const Text('Resume Variant')),
      body: previewAsync.when(
        loading: () => const _VariantDetailSkeleton(),
        error: (e, _) => Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () =>
                ref.invalidate(variantPreviewProvider(widget.variantId)),
          ),
        ),
        data: (preview) => ListView(
          padding: const EdgeInsets.all(AppSpacing.lg),
          children: [
            // Status + match score header
            Row(
              children: [
                ApprovalStatusPill(
                  status: parseApprovalStatus(preview.approvalStatus),
                ),
                if (preview.matchScore != null) ...[
                  const SizedBox(width: AppSpacing.sm),
                  AppBadge(
                    label: '${preview.matchScore}% match',
                    variant: preview.matchScore! >= 70
                        ? AppBadgeVariant.success
                        : preview.matchScore! >= 45
                            ? AppBadgeVariant.warning
                            : AppBadgeVariant.error,
                  ),
                ],
              ],
            ),
            const SizedBox(height: AppSpacing.xl2),

            // Section 1 — Unchanged content
            _SectionHeader(
              label: 'From your resume',
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
            ),
            const SizedBox(height: AppSpacing.sm),
            _CuratedContent(
              data: preview.curatedResume,
              section: 'unchanged',
            ),
            const SizedBox(height: AppSpacing.xl2),

            // Section 2 — Reordered / rephrased
            _SectionHeader(
              label: 'Reordered for this role',
              color: AppColors.infoBlue.withValues(alpha: 0.08),
            ),
            const SizedBox(height: AppSpacing.sm),
            _CuratedContent(
              data: preview.curatedResume,
              section: 'reordered',
            ),
            const SizedBox(height: AppSpacing.xl2),

            // Section 3 — Identified gaps (NEVER shown as present skills)
            if (preview.gapsIdentified.isNotEmpty) ...[
              _SectionHeader(
                label:
                    'Skills this role asks for — not in your resume',
                color: AppColors.warningAmber.withValues(alpha: 0.08),
                icon: Icons.info_outline,
                iconColor: AppColors.warningAmber,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                'These are gaps identified from the job description. '
                'They are NOT in your resume.',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.warningAmber,
                      fontStyle: FontStyle.italic,
                    ),
              ),
              const SizedBox(height: AppSpacing.sm),
              Wrap(
                spacing: AppSpacing.sm,
                runSpacing: AppSpacing.sm,
                children: preview.gapsIdentified
                    .map((gap) => GapTagChip(gap: gap))
                    .toList(),
              ),
              const SizedBox(height: AppSpacing.xl2),
            ],

            // Fabrication notice
            _FabricationNotice(),
          ],
        ),
      ),
      bottomNavigationBar: previewAsync.when(
        loading: () => const SizedBox.shrink(),
        error: (_, _) => const SizedBox.shrink(),
        data: (preview) => _VariantActions(
          variantId: widget.variantId,
          approvalStatus: preview.approvalStatus,
        ),
      ),
    );
  }
}

// ── Section header ────────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({
    required this.label,
    required this.color,
    this.icon,
    this.iconColor,
  });

  final String label;
  final Color color;
  final IconData? icon;
  final Color? iconColor;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          if (icon != null) ...[
            Icon(icon, size: 16, color: iconColor),
            const SizedBox(width: AppSpacing.sm),
          ],
          Text(
            label,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: iconColor ?? Theme.of(context).colorScheme.onSurface,
                ),
          ),
        ],
      ),
    );
  }
}

// ── Curated content renderer ──────────────────────────────────────────────────

class _CuratedContent extends StatelessWidget {
  const _CuratedContent({required this.data, required this.section});

  final Map<String, dynamic> data;
  final String section;

  @override
  Widget build(BuildContext context) {
    // The curated_resume JSON contains all sections. We display it as
    // human-readable key-value blocks. PDF rendering is a Phase 2 item.
    final relevant =
        data.entries.where((e) => e.value != null).toList();
    if (relevant.isEmpty) {
      return Text(
        'No content in this section.',
        style: Theme.of(context).textTheme.bodySmall,
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: relevant
          .map(
            (entry) => Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.sm),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _humanize(entry.key),
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _formatValue(entry.value),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
          )
          .toList(),
    );
  }

  String _humanize(String key) =>
      key.replaceAll('_', ' ').toUpperCase();

  String _formatValue(dynamic value) {
    if (value is List) return value.join(', ');
    return value.toString();
  }
}

// ── Fabrication notice ────────────────────────────────────────────────────────

class _FabricationNotice extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: Theme.of(context)
            .colorScheme
            .surfaceContainerHighest
            .withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.verified_outlined, size: 16),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Text(
              'This variant contains only content from your original resume, '
              'reordered and rephrased for relevance. '
              'No experience, skills, or credentials have been added.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Bottom action bar ─────────────────────────────────────────────────────────

class _VariantActions extends ConsumerWidget {
  const _VariantActions({
    required this.variantId,
    required this.approvalStatus,
  });

  final String variantId;
  final String approvalStatus;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final flowState = ref.watch(approvalFlowProvider);

    if (approvalStatus == 'approved') {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: AppButton(
            label: 'Send Application',
            onPressed: () => _openSendSheet(context, ref),
            icon: Icons.send_outlined,
          ),
        ),
      );
    }

    if (approvalStatus == 'rejected') {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: AppButton(
            label: 'Generate New Variant',
            onPressed: () => context.pop(),
            variant: AppButtonVariant.outlined,
            icon: Icons.refresh_outlined,
          ),
        ),
      );
    }

    // Pending — show approve/reject
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          AppSpacing.lg,
          AppSpacing.sm,
          AppSpacing.lg,
          AppSpacing.lg,
        ),
        child: Row(
          children: [
            Expanded(
              child: AppButton(
                label: 'Reject',
                onPressed: flowState.isBusy ? null : () => _openRejectSheet(context, ref),
                variant: AppButtonVariant.outlined,
              ),
            ),
            const SizedBox(width: AppSpacing.md),
            Expanded(
              child: AppButton(
                label: 'Approve',
                onPressed: flowState.isBusy
                    ? null
                    : () => _startApproval(context, ref),
                isLoading: flowState.isBusy,
                icon: Icons.check_outlined,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _startApproval(BuildContext context, WidgetRef ref) async {
    // Step 1: Fetch live token — fail closed if offline or error
    final token = await ref
        .read(approvalFlowProvider.notifier)
        .fetchToken(variantId);

    if (token == null || !context.mounted) return;

    // Step 2: Show confirmation sheet with live token in scope
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      isDismissible: false,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => ApprovalConfirmSheet(variantId: variantId),
    );
  }

  void _openRejectSheet(BuildContext context, WidgetRef ref) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => _RejectSheet(variantId: variantId),
    );
  }

  void _openSendSheet(BuildContext context, WidgetRef ref) {
    // Look up the cached VariantRecord to get jobId and job display metadata.
    final variantRecord = ref
        .read(variantListProvider)
        .whenOrNull(data: (d) => d.variants
            .where((v) => v.variantId == variantId)
            .firstOrNull);

    if (variantRecord == null) {
      // Variant not in cache — navigate to applications tab as fallback.
      context.go('/applications');
      return;
    }

    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      isDismissible: false,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => ApplicationSendSheet(
        jobId: variantRecord.jobId,
        variantId: variantId,
        jobTitle: variantRecord.jobTitle,
        companyName: variantRecord.companyName,
      ),
    );
  }
}

// ── Reject sheet ──────────────────────────────────────────────────────────────

class _RejectSheet extends ConsumerStatefulWidget {
  const _RejectSheet({required this.variantId});
  final String variantId;

  @override
  ConsumerState<_RejectSheet> createState() => _RejectSheetState();
}

class _RejectSheetState extends ConsumerState<_RejectSheet> {
  final _feedbackCtrl = TextEditingController();

  @override
  void dispose() {
    _feedbackCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final flowState = ref.watch(approvalFlowProvider);
    final theme = Theme.of(context);

    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xl2),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Reject Variant', style: theme.textTheme.headlineSmall),
              const SizedBox(height: AppSpacing.sm),
              Text(
                'Your feedback will trigger a new analysis. '
                'A fresh variant will be generated — this is not an in-place edit.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: AppSpacing.lg),
              TextField(
                controller: _feedbackCtrl,
                maxLines: 4,
                decoration: InputDecoration(
                  hintText: 'Optional: describe what to improve…',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
              if (flowState.errorMessage != null) ...[
                const SizedBox(height: AppSpacing.md),
                ErrorBanner(message: flowState.errorMessage!),
              ],
              const SizedBox(height: AppSpacing.xl2),
              AppButton(
                label: 'Reject and Request Re-analysis',
                onPressed: flowState.isBusy
                    ? null
                    : () async {
                        final success = await ref
                            .read(approvalFlowProvider.notifier)
                            .reject(
                              widget.variantId,
                              feedback: _feedbackCtrl.text.trim().isEmpty
                                  ? null
                                  : _feedbackCtrl.text.trim(),
                            );
                        if (success && context.mounted) {
                          Navigator.of(context).pop();
                          Navigator.of(context).pop();
                        }
                      },
                isLoading: flowState.isBusy,
                variant: AppButtonVariant.destructive,
              ),
              const SizedBox(height: AppSpacing.sm),
              AppButton(
                label: 'Cancel',
                onPressed:
                    flowState.isBusy ? null : () => Navigator.of(context).pop(),
                variant: AppButtonVariant.text,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Loading skeleton ──────────────────────────────────────────────────────────

class _VariantDetailSkeleton extends StatelessWidget {
  const _VariantDetailSkeleton();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(AppSpacing.lg),
      child: Column(
        children: [
          AppSkeleton(width: 120, height: 28),
          SizedBox(height: AppSpacing.xl2),
          AppSkeleton(height: 40),
          SizedBox(height: AppSpacing.lg),
          AppSkeleton(height: 120),
          SizedBox(height: AppSpacing.lg),
          AppSkeleton(height: 80),
          SizedBox(height: AppSpacing.lg),
          AppSkeleton(height: 60),
        ],
      ),
    );
  }
}
