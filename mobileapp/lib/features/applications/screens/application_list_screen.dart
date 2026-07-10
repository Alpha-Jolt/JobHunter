import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/application_status_pill.dart';
import '../../../shared/components/empty_state.dart';
import '../../../shared/components/error_banner.dart';
import '../../../core/network/connectivity_service.dart';
import '../../../shared/components/offline_banner.dart';
import '../providers/applications_provider.dart';

class ApplicationListScreen extends ConsumerWidget {
  const ApplicationListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final appsAsync = ref.watch(applicationListProvider);
    final connectivity = ref.watch(connectivityStreamProvider);
    final online = connectivity.whenOrNull(data: isOnline) ?? true;

    return Scaffold(
      appBar: AppBar(title: const Text('Applications')),
      body: appsAsync.when(
        loading: () => _ApplicationListSkeleton(),
        error: (e, _) => Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () =>
                ref.read(applicationListProvider.notifier).refresh(),
          ),
        ),
        data: (data) {
          if (data.applications.isEmpty) {
            return EmptyState(
              title: 'No applications sent yet.',
              subtitle:
                  'Approve a resume variant, then send your first application.',
              actionLabel: 'View Variants',
              onAction: () => context.go('/variants'),
            );
          }

          return Column(
            children: [
              if (!online) const OfflineBanner(),
              // Today's count banner
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.lg,
                  vertical: AppSpacing.md,
                ),
                color: Theme.of(context)
                    .colorScheme
                    .surfaceContainerHighest,
                child: Text(
                  '${data.count} / 10 applications sent today',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: () => ref
                      .read(applicationListProvider.notifier)
                      .refresh(),
                  child: ListView.builder(
                    itemCount: data.applications.length,
                    itemBuilder: (context, index) {
                      final app = data.applications[index];
                      return ListTile(
                        key: ValueKey(app.applicationId),
                        title: Text(
                          app.jobTitle ?? 'Job Application',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        subtitle: app.companyName != null
                            ? Text(app.companyName!)
                            : null,
                        trailing: ApplicationStatusPill(
                          status: parseApplicationStatus(app.status),
                        ),
                        onTap: () => context.push(
                          '/applications/${app.applicationId}',
                          extra: app,
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _ApplicationListSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 5,
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      itemBuilder: (_, _) => Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.sm,
        ),
        child: const AppSkeleton(height: 64),
      ),
    );
  }
}
