import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/empty_state.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/app_skeleton.dart';
import '../../auth/providers/session_provider.dart';
import '../../resume/providers/resume_provider.dart';
import '../../variants/providers/variants_provider.dart';
import '../data/job_models.dart';
import '../providers/jobs_provider.dart';
import '../providers/swipe_queue.dart';

/// Tinder-style job swipe screen.
///
/// - Swipe RIGHT (or tap ✓) → accept job into queue
/// - Swipe LEFT  (or tap ✗) → skip job
/// - FAB "Generate Variants (n)" → triggers sequential generation for all
///   accepted jobs, then navigates to VariantListScreen (Option A)
///
/// Queue capped at 10 to respect variant budget.
class JobSwipeScreen extends ConsumerStatefulWidget {
  const JobSwipeScreen({super.key});

  @override
  ConsumerState<JobSwipeScreen> createState() => _JobSwipeScreenState();
}

class _JobSwipeScreenState extends ConsumerState<JobSwipeScreen>
    with SingleTickerProviderStateMixin {
  final SwipeQueueNotifier _queue = SwipeQueueNotifier();
  int _currentIndex = 0;
  bool _isSubmitting = false;
  String? _submitError;

  // Drag state
  double _dragX = 0;
  double _dragY = 0;
  bool _isDragging = false;
  static const double _swipeThreshold = 100.0;

  List<JobRecord> _jobs(JobListState state) => state.jobs;

  @override
  Widget build(BuildContext context) {
    final jobState = ref.watch(jobListProvider);
    final jobs = _jobs(jobState);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Swipe Jobs'),
        actions: [
          if (_queue.count > 0)
            Padding(
              padding: const EdgeInsets.only(right: AppSpacing.sm),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.sm,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.brandOrange,
                    borderRadius: BorderRadius.circular(AppRadius.full),
                  ),
                  child: Text(
                    '${_queue.count}/10',
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
      body: _buildBody(context, jobState, jobs),
      bottomNavigationBar: _queue.count > 0
          ? SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.lg),
                child: AppButton(
                  label: 'Generate Variants (${_queue.count})',
                  onPressed: _isSubmitting ? null : _submitQueue,
                  isLoading: _isSubmitting,
                  icon: Icons.auto_awesome_outlined,
                ),
              ),
            )
          : null,
    );
  }

  Widget _buildBody(
    BuildContext context,
    JobListState jobState,
    List<JobRecord> jobs,
  ) {
    if (jobState.isLoading && jobs.isEmpty) {
      return const Center(child: AppSkeleton(width: 320, height: 460));
    }

    if (jobState.hasError && jobs.isEmpty) {
      return Center(
        child: ErrorBanner(
          message: jobState.errorMessage!,
          isRetryable: true,
          onRetry: () => ref.read(jobListProvider.notifier).refresh(),
        ),
      );
    }

    if (_submitError != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(AppSpacing.xl2),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ErrorBanner(message: _submitError!),
              const SizedBox(height: AppSpacing.xl2),
              AppButton(
                label: 'Try Again',
                onPressed: _submitQueue,
                icon: Icons.refresh_outlined,
              ),
            ],
          ),
        ),
      );
    }

    if (jobs.isEmpty || _currentIndex >= jobs.length) {
      // All cards swiped or no jobs
      return EmptyState(
        title: _queue.count > 0
            ? 'All done! You\'ve selected ${_queue.count} job${_queue.count > 1 ? 's' : ''}.'
            : 'No more jobs to review.',
        subtitle: _queue.count > 0
            ? 'Tap Generate Variants below to continue.'
            : 'Come back later or pull to refresh.',
        actionLabel: _queue.count == 0 ? 'Refresh' : null,
        onAction: _queue.count == 0
            ? () {
                setState(() => _currentIndex = 0);
                ref.read(jobListProvider.notifier).refresh();
              }
            : null,
      );
    }

    final job = jobs[_currentIndex];
    final remaining = jobs.length - _currentIndex;

    return Column(
      children: [
        // Progress indicator
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg,
            vertical: AppSpacing.sm,
          ),
          child: Row(
            children: [
              Text(
                '$remaining job${remaining != 1 ? 's' : ''} remaining',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                    ),
              ),
              const Spacer(),
              if (_queue.isFull)
                Text(
                  'Queue full (10)',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppColors.warningAmber,
                        fontWeight: FontWeight.w600,
                      ),
                ),
            ],
          ),
        ),

        // Swipe card area
        Expanded(
          child: GestureDetector(
            onHorizontalDragStart: (_) =>
                setState(() => _isDragging = true),
            onHorizontalDragUpdate: (d) => setState(() {
              _dragX += d.delta.dx;
              _dragY += d.delta.dy * 0.3;
            }),
            onHorizontalDragEnd: (_) {
              if (_dragX > _swipeThreshold) {
                _swipeRight(job);
              } else if (_dragX < -_swipeThreshold) {
                _swipeLeft();
              } else {
                // Snap back
                setState(() {
                  _dragX = 0;
                  _dragY = 0;
                  _isDragging = false;
                });
              }
            },
            child: Center(
              child: AnimatedContainer(
                duration: _isDragging
                    ? Duration.zero
                    : const Duration(milliseconds: 200),
                curve: Curves.easeOut,
                transform: (Matrix4.identity()
                  ..leftTranslateByDouble(_dragX, _dragY, 0, 1)
                  ..rotateZ(_dragX * 0.001)),
                child: Stack(
                  children: [
                    // Card
                    _SwipeCard(job: job),

                    // Accept overlay (right swipe)
                    if (_dragX > 30)
                      Positioned.fill(
                        child: IgnorePointer(
                          child: Container(
                            decoration: BoxDecoration(
                              color: AppColors.successGreen
                                  .withValues(alpha: (_dragX / 150).clamp(0.0, 0.4)),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Center(
                              child: Opacity(
                                opacity: (_dragX / _swipeThreshold).clamp(0.0, 1.0),
                                child: Container(
                                  padding: const EdgeInsets.all(AppSpacing.md),
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: AppColors.successGreen,
                                      width: 3,
                                    ),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Text(
                                    'APPLY',
                                    style: TextStyle(
                                      color: AppColors.successGreen,
                                      fontSize: 28,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: 3,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),

                    // Reject overlay (left swipe)
                    if (_dragX < -30)
                      Positioned.fill(
                        child: IgnorePointer(
                          child: Container(
                            decoration: BoxDecoration(
                              color: AppColors.destructive.withValues(
                                  alpha: (-_dragX / 150).clamp(0.0, 0.4)),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Center(
                              child: Opacity(
                                opacity: (-_dragX / _swipeThreshold)
                                    .clamp(0.0, 1.0),
                                child: Container(
                                  padding: const EdgeInsets.all(AppSpacing.md),
                                  decoration: BoxDecoration(
                                    border: Border.all(
                                      color: AppColors.destructive,
                                      width: 3,
                                    ),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Text(
                                    'SKIP',
                                    style: TextStyle(
                                      color: AppColors.destructive,
                                      fontSize: 28,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: 3,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        ),

        // Button row
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.xl4,
            AppSpacing.lg,
            AppSpacing.xl4,
            AppSpacing.xl3,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Skip button
              _ActionButton(
                icon: Icons.close_rounded,
                color: AppColors.destructive,
                onTap: _swipeLeft,
                tooltip: 'Skip',
              ),

              // Tap to view detail
              _ActionButton(
                icon: Icons.info_outline_rounded,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
                onTap: () => context.push('/jobs/${job.jobId}', extra: job),
                tooltip: 'View details',
                small: true,
              ),

              // Accept button
              _ActionButton(
                icon: Icons.check_rounded,
                color: AppColors.successGreen,
                onTap: _queue.isFull ? null : () => _swipeRight(job),
                tooltip: 'Apply',
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _swipeRight(JobRecord job) {
    if (!_queue.isFull) _queue.accept(job);
    _nextCard();
  }

  void _swipeLeft() => _nextCard();

  void _nextCard() {
    setState(() {
      _currentIndex++;
      _dragX = 0;
      _dragY = 0;
      _isDragging = false;
    });
    // Pre-load next page when near end
    final jobState = ref.read(jobListProvider);
    if (_currentIndex >= jobState.jobs.length - 3) {
      ref.read(jobListProvider.notifier).loadMore();
    }
  }

  Future<void> _submitQueue() async {
    if (_queue.count == 0) return;
    setState(() {
      _isSubmitting = true;
      _submitError = null;
    });

    final session = ref.read(sessionProvider);
    final userId = session.user?.userId;
    final masterResume = ref.read(masterResumeProvider);

    if (userId == null || masterResume == null) {
      setState(() {
        _isSubmitting = false;
        _submitError = masterResume == null
            ? 'No resume uploaded. Please upload your resume first.'
            : 'Session error. Please log in again.';
      });
      return;
    }

    int successCount = 0;
    for (final job in _queue.accepted) {
      try {
        await ref.read(variantGenerationProvider.notifier).generate(
              userId: userId,
              jobId: job.jobId,
              resumeFilePath: masterResume.filePath,
            );
        successCount++;
      } catch (_) {
        // Continue with remaining jobs — partial success is acceptable
      }
    }

    if (!mounted) return;
    _queue.clear();
    ref.invalidate(variantListProvider);

    if (successCount > 0) {
      context.go('/variants');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            '$successCount variant${successCount > 1 ? 's' : ''} queued for review.',
          ),
        ),
      );
    } else {
      setState(() {
        _isSubmitting = false;
        _submitError = 'Failed to generate variants. Please try again.';
      });
    }
  }
}

// ── Swipe card ────────────────────────────────────────────────────────────────

class _SwipeCard extends StatelessWidget {
  const _SwipeCard({required this.job});
  final JobRecord job;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Container(
      width: MediaQuery.of(context).size.width - AppSpacing.xl3 * 2,
      constraints: const BoxConstraints(maxHeight: 460),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colorScheme.outlineVariant),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.08),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            // Company initial badge
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: AppColors.brandOrange.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Center(
                child: Text(
                  job.companyName.isNotEmpty
                      ? job.companyName[0].toUpperCase()
                      : '?',
                  style: theme.textTheme.headlineMedium?.copyWith(
                    color: AppColors.brandOrange,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),

            Text(
              job.title,
              style: theme.textTheme.titleLarge,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              job.companyName,
              style: theme.textTheme.titleMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                const Icon(Icons.location_on_outlined, size: 14),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    job.location +
                        (job.remoteType != null && job.remoteType != 'onsite'
                            ? ' · ${job.remoteType![0].toUpperCase()}${job.remoteType!.substring(1)}'
                            : ''),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            if (job.salaryMin != null || job.salaryMax != null) ...[
              const SizedBox(height: AppSpacing.xs),
              Row(
                children: [
                  const Icon(Icons.currency_rupee, size: 14),
                  const SizedBox(width: 4),
                  Text(
                    _salaryLabel(job),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: AppSpacing.lg),

            // Skills
            if (job.skillsRequired.isNotEmpty) ...[
              Wrap(
                spacing: AppSpacing.xs,
                runSpacing: AppSpacing.xs,
                children: job.skillsRequired
                    .take(5)
                    .map(
                      (s) => Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppSpacing.sm,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(AppRadius.full),
                        ),
                        child: Text(
                          s,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ),
              const SizedBox(height: AppSpacing.lg),
            ],

            // Description preview
            if (job.description != null)
              Text(
                job.description!,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
          ],
        ),
      ),
    );
  }

  String _salaryLabel(JobRecord job) {
    if (job.salaryMin != null && job.salaryMax != null) {
      return '₹${_fmt(job.salaryMin!)} – ₹${_fmt(job.salaryMax!)}';
    }
    if (job.salaryMin != null) return '₹${_fmt(job.salaryMin!)}+';
    return 'Up to ₹${_fmt(job.salaryMax!)}';
  }

  String _fmt(int v) {
    if (v >= 100000) return '${(v / 100000).toStringAsFixed(1)}L';
    if (v >= 1000) return '${(v / 1000).toStringAsFixed(0)}K';
    return v.toString();
  }
}

// ── Action button ─────────────────────────────────────────────────────────────

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.icon,
    required this.color,
    required this.onTap,
    required this.tooltip,
    this.small = false,
  });

  final IconData icon;
  final Color color;
  final VoidCallback? onTap;
  final String tooltip;
  final bool small;

  @override
  Widget build(BuildContext context) {
    final size = small ? 48.0 : 64.0;
    final iconSize = small ? 22.0 : 30.0;

    return Tooltip(
      message: tooltip,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: onTap == null
                ? Theme.of(context)
                    .colorScheme
                    .surfaceContainerHighest
                    .withValues(alpha: 0.5)
                : color.withValues(alpha: 0.10),
            border: Border.all(
              color: onTap == null
                  ? Theme.of(context).colorScheme.outlineVariant
                  : color.withValues(alpha: 0.4),
              width: 1.5,
            ),
          ),
          child: Icon(
            icon,
            color: onTap == null
                ? Theme.of(context)
                    .colorScheme
                    .onSurface
                    .withValues(alpha: 0.3)
                : color,
            size: iconSize,
          ),
        ),
      ),
    );
  }
}
