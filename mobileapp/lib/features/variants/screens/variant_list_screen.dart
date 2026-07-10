import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/empty_state.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/variant_card.dart';
import '../../../core/network/connectivity_service.dart';
import '../../../shared/components/offline_banner.dart';
import '../providers/variants_provider.dart';

class VariantListScreen extends ConsumerWidget {
  const VariantListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final variantsAsync = ref.watch(variantListProvider);
    final connectivity = ref.watch(connectivityStreamProvider);
    final online = connectivity.whenOrNull(data: isOnline) ?? true;

    return Scaffold(
      appBar: AppBar(title: const Text('Variants')),
      body: variantsAsync.when(
        loading: () => _VariantListSkeleton(),
        error: (e, _) => Center(
          child: ErrorBanner(
            message: e.toString(),
            onRetry: () =>
                ref.read(variantListProvider.notifier).refresh(),
          ),
        ),
        data: (data) {
          if (data.variants.isEmpty) {
            return EmptyState(
              title: 'No variants yet.',
              subtitle:
                  'Browse jobs and generate a tailored resume variant for any role.',
              actionLabel: 'Browse Jobs',
              onAction: () => context.go('/jobs'),
            );
          }

          return Column(
            children: [
              if (!online) const OfflineBanner(),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: () =>
                      ref.read(variantListProvider.notifier).refresh(),
                  child: ListView.builder(
                    itemCount: data.variants.length,
                    itemBuilder: (context, index) {
                      final variant = data.variants[index];
                      final tokenExpiresAt = variant.createdAt?.add(const Duration(hours: 24));

                      return VariantCard(
                        key: ValueKey(variant.variantId),
                        variantId: variant.variantId,
                        jobTitle: variant.jobTitle ?? 'Job Variant',
                        companyName: variant.companyName ?? '',
                        approvalStatus: variant.approvalStatus,
                        tokenExpiresAt: tokenExpiresAt,
                        onTap: () =>
                            context.push('/variants/${variant.variantId}'),
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

class _VariantListSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: 4,
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      itemBuilder: (_, _) => Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.sm,
        ),
        child: const AppSkeleton(height: 100),
      ),
    );
  }
}
