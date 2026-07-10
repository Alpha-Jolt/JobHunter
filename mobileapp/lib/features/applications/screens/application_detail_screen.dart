import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/application_status_pill.dart';
import '../../../shared/components/error_banner.dart';
import '../data/application_models.dart';
import '../providers/applications_provider.dart';

/// Shows status and metadata for a single sent application.
/// Thread content is a TODO (Phase 2 backend item: reply tracking).
class ApplicationDetailScreen extends ConsumerWidget {
  const ApplicationDetailScreen({required this.applicationId, super.key});

  final String applicationId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusAsync = ref.watch(applicationStatusProvider(applicationId));
    final app = GoRouterState.of(context).extra as ApplicationRecord?;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(
          app?.jobTitle ?? 'Application',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: statusAsync.when(
          loading: () => const _DetailSkeleton(),
          error: (e, _) => ErrorBanner(
            message: e.toString(),
            onRetry: () =>
                ref.invalidate(applicationStatusProvider(applicationId)),
          ),
          data: (status) => Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (app?.companyName != null) ...[
                Text(app!.companyName!, style: theme.textTheme.titleMedium),
                const SizedBox(height: AppSpacing.sm),
              ],
              Row(
                children: [
                  ApplicationStatusPill(
                    status: parseApplicationStatus(status.status),
                  ),
                  if (status.replyCount > 0) ...[
                    const SizedBox(width: AppSpacing.sm),
                    Text(
                      '${status.replyCount} '
                      '${status.replyCount == 1 ? 'reply' : 'replies'}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: AppSpacing.lg),
              if (status.sentAt != null)
                _InfoRow(
                  label: 'Sent',
                  value: _formatDate(status.sentAt!),
                ),
              const SizedBox(height: AppSpacing.xl3),
              // Thread view — TODO(OQ-03): Phase 2 backend item
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(AppSpacing.lg),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(8),
                  border:
                      Border.all(color: theme.colorScheme.outlineVariant),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.mail_outline, size: 18),
                    const SizedBox(width: AppSpacing.sm),
                    Expanded(
                      child: Text(
                        'Email thread view coming in a future update.',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} '
        '${date.hour.toString().padLeft(2, '0')}:'
        '${date.minute.toString().padLeft(2, '0')} UTC';
  }
}

class _InfoRow extends StatelessWidget {
  const _InfoRow({required this.label, required this.value});
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(fontWeight: FontWeight.w600),
        ),
        Text(value, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _DetailSkeleton extends StatelessWidget {
  const _DetailSkeleton();

  @override
  Widget build(BuildContext context) {
    return const Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AppSkeleton(width: 200, height: 24),
        SizedBox(height: AppSpacing.md),
        AppSkeleton(width: 100, height: 28),
        SizedBox(height: AppSpacing.lg),
        AppSkeleton(height: 60),
      ],
    );
  }
}
