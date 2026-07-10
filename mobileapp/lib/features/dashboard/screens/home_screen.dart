import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/variant_card.dart';
import '../../applications/providers/applications_provider.dart';
import '../../auth/providers/session_provider.dart';
import '../../variants/providers/variants_provider.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    final variantsAsync = ref.watch(variantListProvider);
    final appsAsync = ref.watch(applicationListProvider);
    final theme = Theme.of(context);

    final displayName =
        session.user?.firstName?.isNotEmpty ?? false
            ? session.user!.firstName!
            : 'there';

    return Scaffold(
      appBar: AppBar(
        title: const Text('JobHunter'),
        centerTitle: false,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.wait<void>([
            ref.read(variantListProvider.notifier).refresh(),
            ref.read(applicationListProvider.notifier).refresh(),
          ]);
        },
        child: ListView(
          padding: const EdgeInsets.only(bottom: AppSpacing.xl4),
          children: [
            // Greeting header
            Padding(
              padding: const EdgeInsets.fromLTRB(
                AppSpacing.lg,
                AppSpacing.xl2,
                AppSpacing.lg,
                AppSpacing.lg,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Hi, $displayName 👋',
                    style: theme.textTheme.headlineMedium,
                  ),
                  const SizedBox(height: AppSpacing.xs),
                  Text(
                    'Here\'s your job hunt summary.',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),

            // Stats row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
              child: Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      label: 'Variants\nPending',
                      valueAsync: variantsAsync.when(
                        data: (d) => d.total,
                        loading: () => null,
                        error: (_, _) => 0,
                      ),
                      color: AppColors.warningAmber,
                      onTap: () => context.go('/variants'),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  Expanded(
                    child: _StatCard(
                      label: 'Sent\nToday',
                      valueAsync: appsAsync.when(
                        data: (d) => d.count,
                        loading: () => null,
                        error: (_, _) => 0,
                      ),
                      color: AppColors.infoBlue,
                      onTap: () => context.go('/applications'),
                    ),
                  ),
                  const SizedBox(width: AppSpacing.md),
                  // Application score — TODO (backend not implemented)
                  const Expanded(
                    child: _StatCardPlaceholder(
                      label: 'App\nScore',
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSpacing.xl2),

            // Quick actions
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
              child: Column(
                children: [
                  AppButton(
                    label: 'Browse Jobs',
                    onPressed: () => context.go('/jobs'),
                    icon: Icons.work_outline,
                  ),
                  const SizedBox(height: AppSpacing.sm),
                  AppButton(
                    label: 'Upload / Update Resume',
                    onPressed: () => context.push('/profile/resume'),
                    icon: Icons.upload_file_outlined,
                    variant: AppButtonVariant.outlined,
                  ),
                ],
              ),
            ),

            const SizedBox(height: AppSpacing.xl2),

            // Pending variants section
            variantsAsync.when(
              loading: () => const Padding(
                padding:
                    EdgeInsets.symmetric(horizontal: AppSpacing.lg),
                child: AppSkeleton(height: 120),
              ),
              error: (_, _) => const SizedBox.shrink(),
              data: (data) {
                if (data.variants.isEmpty) return const SizedBox.shrink();
                final pending = data.variants
                    .where((v) => v.approvalStatus == 'pending')
                    .take(3)
                    .toList();
                if (pending.isEmpty) return const SizedBox.shrink();

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.lg),
                      child: Row(
                        mainAxisAlignment:
                            MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Awaiting Approval',
                              style: theme.textTheme.titleMedium),
                          TextButton(
                            onPressed: () => context.go('/variants'),
                            child: const Text('See all'),
                          ),
                        ],
                      ),
                    ),
                    ...pending.map(
                      (v) => VariantCard(
                        key: ValueKey(v.variantId),
                        variantId: v.variantId,
                        jobTitle: v.jobTitle ?? 'Job Variant',
                        companyName: v.companyName ?? '',
                        approvalStatus: v.approvalStatus,
                        tokenExpiresAt: v.createdAt?.add(const Duration(hours: 24)),
                        onTap: () =>
                            context.push('/variants/${v.variantId}'),
                      ),
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

// ── Stat card ─────────────────────────────────────────────────────────────────

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.valueAsync,
    required this.color,
    required this.onTap,
  });

  final String label;
  final int? valueAsync;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            valueAsync == null
                ? const AppSkeleton(width: 32, height: 28)
                : Text(
                    valueAsync.toString(),
                    style: theme.textTheme.headlineMedium?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              label,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Placeholder stat card (backend not implemented) ───────────────────────────

class _StatCardPlaceholder extends StatelessWidget {
  const _StatCardPlaceholder({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '—',
            style: theme.textTheme.headlineMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            'Coming soon',
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant
                  .withValues(alpha: 0.6),
            ),
          ),
        ],
      ),
    );
  }
}
