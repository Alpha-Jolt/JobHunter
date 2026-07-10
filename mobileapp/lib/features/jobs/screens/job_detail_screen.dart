import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_badge.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_chip.dart';
import '../../../shared/components/app_divider.dart';
import '../../../shared/components/email_trust_badge.dart';
import '../data/job_models.dart';

/// Displays full job details and surfaces the Generate Variant CTA.
/// Receives [JobRecord] as route extra to avoid an extra network call.
class JobDetailScreen extends ConsumerWidget {
  const JobDetailScreen({required this.jobId, super.key});

  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // JobRecord passed as GoRouter extra; fall back gracefully if absent.
    final job = GoRouterState.of(context).extra as JobRecord?;

    if (job == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Job not found.')),
      );
    }

    return Scaffold(
      appBar: AppBar(title: Text(job.title, maxLines: 1)),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: [
          // Company & location
          Text(job.companyName,
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: AppSpacing.xs),
          Text(
            '${job.location}'
            '${job.remoteType != null && job.remoteType != 'onsite' ? ' · ${_remoteLabel(job.remoteType!)}' : ''}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
          const SizedBox(height: AppSpacing.md),

          // Meta chips
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: [
              if (job.jobType != null)
                AppChip(label: _jobTypeLabel(job.jobType!)),
              if (job.salaryMin != null || job.salaryMax != null)
                AppChip(label: _salaryLabel(job)),
              if (job.experienceMin != null || job.experienceMax != null)
                AppChip(label: _expLabel(job)),
              EmailTrustBadge(trust: job.emailTrust),
              _statusBadge(job.status),
            ],
          ),

          // Low-trust warning
          if (job.emailTrust == 'low') ...[
            const SizedBox(height: AppSpacing.md),
            Container(
              padding: const EdgeInsets.all(AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.warningAmber.withValues(alpha: 0.10),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                    color: AppColors.warningAmber.withValues(alpha: 0.3)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_outlined,
                      size: 18, color: AppColors.warningAmber),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'HR email appears to be a free webmail address. '
                      'Proceed with awareness.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppColors.warningAmber,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: AppSpacing.xl2),
          const AppDivider(),
          const SizedBox(height: AppSpacing.xl2),

          // Description
          if (job.description != null) ...[
            Text('Description',
                style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: AppSpacing.sm),
            Text(job.description!,
                style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: AppSpacing.xl2),
          ],

          // Skills required
          if (job.skillsRequired.isNotEmpty) ...[
            Text('Skills Required',
                style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: AppSpacing.sm),
            Wrap(
              spacing: AppSpacing.sm,
              runSpacing: AppSpacing.sm,
              children: job.skillsRequired
                  .map((s) => AppChip(label: s))
                  .toList(),
            ),
            const SizedBox(height: AppSpacing.xl2),
          ],

          // Apply email
          if (job.applyEmail != null) ...[
            Text('Contact', style: Theme.of(context).textTheme.titleSmall),
            const SizedBox(height: AppSpacing.xs),
            Text(
              job.applyEmail!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: AppSpacing.xl3),
          ],
        ],
      ),

      // CTA footer
      bottomNavigationBar: _buildCta(context, job),
    );
  }

  Widget _buildCta(BuildContext context, JobRecord job) {
    final isClosed = job.status == 'closed';
    final isApplied = job.status == 'applied';

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: isClosed
            ? const AppButton(
                label: 'This job is closed',
                onPressed: null,
                variant: AppButtonVariant.outlined,
              )
            : isApplied
                ? AppButton(
                    label: 'Already Applied',
                    onPressed: () => context.push('/applications'),
                    variant: AppButtonVariant.outlined,
                    icon: Icons.send,
                  )
                : AppButton(
                    label: 'Generate Resume Variant',
                    onPressed: () => context.push(
                      '/jobs/$jobId/generate',
                      extra: job,
                    ),
                    icon: Icons.auto_awesome_outlined,
                  ),
      ),
    );
  }

  Widget _statusBadge(String status) {
    switch (status) {
      case 'applied':
        return const AppBadge(
            label: 'Applied', variant: AppBadgeVariant.success);
      case 'closed':
        return const AppBadge(
            label: 'Closed', variant: AppBadgeVariant.neutral);
      default:
        return const SizedBox.shrink();
    }
  }

  String _remoteLabel(String t) {
    switch (t) {
      case 'remote':
        return 'Remote';
      case 'hybrid':
        return 'Hybrid';
      default:
        return t;
    }
  }

  String _jobTypeLabel(String t) {
    switch (t) {
      case 'fulltime':
        return 'Full-time';
      case 'parttime':
        return 'Part-time';
      case 'contract':
        return 'Contract';
      case 'internship':
        return 'Internship';
      case 'freelance':
        return 'Freelance';
      default:
        return t;
    }
  }

  String _salaryLabel(JobRecord job) {
    if (job.salaryMin != null && job.salaryMax != null) {
      return '₹${_fmt(job.salaryMin!)} – ₹${_fmt(job.salaryMax!)}';
    }
    if (job.salaryMin != null) return '₹${_fmt(job.salaryMin!)}+';
    if (job.salaryMax != null) return 'Up to ₹${_fmt(job.salaryMax!)}';
    return '';
  }

  String _expLabel(JobRecord job) {
    if (job.experienceMin != null && job.experienceMax != null) {
      return '${job.experienceMin}–${job.experienceMax} yrs';
    }
    if (job.experienceMin != null) return '${job.experienceMin}+ yrs';
    if (job.experienceMax != null) return 'Up to ${job.experienceMax} yrs';
    return '';
  }

  String _fmt(int value) {
    if (value >= 100000) {
      return '${(value / 100000).toStringAsFixed(1)}L';
    }
    if (value >= 1000) {
      return '${(value / 1000).toStringAsFixed(0)}K';
    }
    return value.toString();
  }
}
