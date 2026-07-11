import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/app_chip.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../../shared/components/empty_state.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/job_card.dart';
import '../data/job_models.dart';
import '../../../core/network/connectivity_service.dart';
import '../../../shared/components/offline_banner.dart';
import '../providers/jobs_provider.dart';

class JobListScreen extends ConsumerWidget {
  const JobListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobState = ref.watch(jobListProvider);
    final connectivity = ref.watch(connectivityStreamProvider);
    final online = connectivity.whenOrNull(data: isOnline) ?? true;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Jobs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.swipe_outlined),
            tooltip: 'Swipe to select',
            onPressed: () => context.push('/jobs/swipe'),
          ),
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.filter_list_outlined),
                if (jobState.filters.hasAnyFilter)
                  Positioned(
                    right: 0,
                    top: 0,
                    child: Container(
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: AppColors.brandOrange,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
              ],
            ),
            tooltip: 'Filters',
            onPressed: () => _showFilterSheet(context, ref, jobState.filters),
          ),
        ],
      ),
      body: _buildBody(context, ref, jobState, online),
    );
  }

  Widget _buildBody(
    BuildContext context,
    WidgetRef ref,
    JobListState jobState,
    bool online,
  ) {
    if (jobState.isLoading && jobState.jobs.isEmpty) {
      return _JobListSkeleton();
    }

    if (jobState.hasError && jobState.jobs.isEmpty) {
      return Center(
        child: ErrorBanner(
          message: jobState.errorMessage!,
          onRetry: () => ref.read(jobListProvider.notifier).refresh(),
        ),
      );
    }

    if (!jobState.isLoading && jobState.jobs.isEmpty) {
      return EmptyState(
        title: jobState.filters.hasAnyFilter
            ? 'No jobs match your filters.'
            : 'No jobs available yet.',
        actionLabel: jobState.filters.hasAnyFilter ? 'Clear Filters' : null,
        onAction: jobState.filters.hasAnyFilter
            ? () => ref.read(jobListProvider.notifier).clearFilters()
            : null,
      );
    }

    return Column(
      children: [
        if (!online && jobState.jobs.isNotEmpty) const OfflineBanner(),
        Expanded(
          child: NotificationListener<ScrollNotification>(
            onNotification: (notification) {
              if (notification is ScrollEndNotification &&
                  notification.metrics.extentAfter < 200) {
                ref.read(jobListProvider.notifier).loadMore();
              }
              return false;
            },
            child: RefreshIndicator(
              onRefresh: () => ref.read(jobListProvider.notifier).refresh(),
              child: ListView.builder(
                itemCount: jobState.jobs.length +
                    (jobState.isLoadingMore ? 1 : 0) +
                    (jobState.hasError ? 1 : 0),
                itemBuilder: (context, index) {
                  if (index < jobState.jobs.length) {
                    final job = jobState.jobs[index];
                    return JobCard(
                      key: ValueKey(job.jobId),
                      jobId: job.jobId,
                      title: job.title,
                      companyName: job.companyName,
                      location: job.location,
                      status: job.status,
                      emailTrust: job.emailTrust,
                      remoteType: job.remoteType,
                      jobType: job.jobType,
                      salaryMin: job.salaryMin,
                      salaryMax: job.salaryMax,
                      onTap: () =>
                          context.push('/jobs/${job.jobId}', extra: job),
                    );
                  }
                  if (jobState.isLoadingMore) {
                    return const Padding(
                      padding: EdgeInsets.all(AppSpacing.lg),
                      child: Center(child: CircularProgressIndicator()),
                    );
                  }
                  if (jobState.hasError) {
                    return Padding(
                      padding: const EdgeInsets.all(AppSpacing.lg),
                      child: ErrorBanner(
                        message: jobState.errorMessage!,
                        onRetry: () =>
                            ref.read(jobListProvider.notifier).loadMore(),
                      ),
                    );
                  }
                  return null;
                },
              ),
            ),
          ),
        ),
      ],
    );
  }

  void _showFilterSheet(
    BuildContext context,
    WidgetRef ref,
    JobFilters currentFilters,
  ) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (_) => _FilterSheet(
        currentFilters: currentFilters,
        onApply: (filters) {
          Navigator.of(context).pop();
          ref
              .read(jobListProvider.notifier)
              .applyFilters(filters);
        },
        onClear: () {
          Navigator.of(context).pop();
          ref
              .read(jobListProvider.notifier)
              .clearFilters();
        },
      ),
    );
  }
}

// ── Filter bottom sheet ───────────────────────────────────────────────────────

class _FilterSheet extends StatefulWidget {
  const _FilterSheet({
    required this.currentFilters,
    required this.onApply,
    required this.onClear,
  });

  final JobFilters currentFilters;
  final void Function(JobFilters) onApply;
  final VoidCallback onClear;

  @override
  State<_FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<_FilterSheet> {
  late String? _remoteType;
  late String? _jobType;
  late String? _emailTrust;
  late TextEditingController _locationCtrl;
  late RangeValues _experienceRange;

  static const _remoteOptions = ['onsite', 'hybrid', 'remote'];
  static const _jobTypeOptions = [
    'fulltime',
    'parttime',
    'contract',
    'internship',
    'freelance',
  ];
  static const _trustOptions = ['verified', 'unknown', 'low'];

  @override
  void initState() {
    super.initState();
    _remoteType = widget.currentFilters.remoteType;
    _jobType = widget.currentFilters.jobType;
    _emailTrust = widget.currentFilters.emailTrust;
    _locationCtrl = TextEditingController(
      text: widget.currentFilters.location ?? '',
    );
    _experienceRange = RangeValues(
      (widget.currentFilters.experienceMin ?? 0).toDouble(),
      (widget.currentFilters.experienceMax ?? 15).toDouble(),
    );
  }

  @override
  void dispose() {
    _locationCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.7,
      maxChildSize: 0.9,
      builder: (context, controller) => ListView(
        controller: controller,
        padding: const EdgeInsets.all(AppSpacing.lg),
        children: [
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
          Text('Filters', style: theme.textTheme.headlineSmall),
          const SizedBox(height: AppSpacing.xl2),

          // Remote type
          Text('Remote Type', style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.sm,
            children: _remoteOptions
                .map(
                  (opt) => AppChip(
                    label: _remoteLabel(opt),
                    isSelected: _remoteType == opt,
                    onTap: () => setState(
                      () => _remoteType = _remoteType == opt ? null : opt,
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: AppSpacing.xl2),

          // Job type
          Text('Job Type', style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: _jobTypeOptions
                .map(
                  (opt) => AppChip(
                    label: _jobTypeLabel(opt),
                    isSelected: _jobType == opt,
                    onTap: () => setState(
                      () => _jobType = _jobType == opt ? null : opt,
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: AppSpacing.xl2),

          // Email trust
          Text('Email Trust', style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.sm,
            children: _trustOptions
                .map(
                  (opt) => AppChip(
                    label: _trustLabel(opt),
                    isSelected: _emailTrust == opt,
                    onTap: () => setState(
                      () =>
                          _emailTrust = _emailTrust == opt ? null : opt,
                    ),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: AppSpacing.xl2),

          // Location text filter
          Text('Location', style: theme.textTheme.titleSmall),
          const SizedBox(height: AppSpacing.sm),
          TextField(
            controller: _locationCtrl,
            decoration: InputDecoration(
              hintText: 'e.g. Bangalore',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.lg,
                vertical: AppSpacing.md,
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.xl2),

          // Experience range
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Experience', style: theme.textTheme.titleSmall),
              Text(
                '${_experienceRange.start.round()} – '
                '${_experienceRange.end.round() == 15 ? '15+' : _experienceRange.end.round()} yrs',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          RangeSlider(
            values: _experienceRange,
            min: 0,
            max: 15,
            divisions: 15,
            onChanged: (v) => setState(() => _experienceRange = v),
          ),
          const SizedBox(height: AppSpacing.xl3),

          // Actions
          AppButton(
            label: 'Apply Filters',
            onPressed: () => widget.onApply(
              JobFilters(
                remoteType: _remoteType,
                jobType: _jobType,
                emailTrust: _emailTrust,
                location: _locationCtrl.text.trim().isEmpty
                    ? null
                    : _locationCtrl.text.trim(),
                experienceMin: _experienceRange.start.round() == 0
                    ? null
                    : _experienceRange.start.round(),
                experienceMax: _experienceRange.end.round() == 15
                    ? null
                    : _experienceRange.end.round(),
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          AppButton(
            label: 'Clear All',
            onPressed: widget.onClear,
            variant: AppButtonVariant.text,
          ),
        ],
      ),
    );
  }

  String _remoteLabel(String opt) {
    switch (opt) {
      case 'onsite':
        return 'On-site';
      case 'hybrid':
        return 'Hybrid';
      case 'remote':
        return 'Remote';
      default:
        return opt;
    }
  }

  String _jobTypeLabel(String opt) {
    switch (opt) {
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
        return opt;
    }
  }

  String _trustLabel(String opt) {
    switch (opt) {
      case 'verified':
        return 'Verified';
      case 'unknown':
        return 'Unverified';
      case 'low':
        return 'Low Trust';
      default:
        return opt;
    }
  }
}

// ── Loading skeleton ──────────────────────────────────────────────────────────

class _JobListSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      itemCount: 6,
      itemBuilder: (_, _) => Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg,
          vertical: AppSpacing.sm,
        ),
        child: const AppSkeleton(height: 110),
      ),
    );
  }
}
