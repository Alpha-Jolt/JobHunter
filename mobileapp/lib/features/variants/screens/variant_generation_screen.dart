import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/error_banner.dart';
import '../../auth/providers/session_provider.dart';
import '../../jobs/data/job_models.dart';
import '../../resume/providers/resume_provider.dart';
import '../providers/variants_provider.dart';

/// Triggers AI variant generation for a given job.
/// Receives [JobRecord] as GoRouter extra.
///
/// Requires a master resume to have been uploaded. Reads `filePath` from
/// [MasterResumeNotifier] — the server-side path returned after upload.
/// If no resume is on file, blocks generation and shows an upload CTA.
class VariantGenerationScreen extends ConsumerStatefulWidget {
  const VariantGenerationScreen({required this.jobId, super.key});

  final String jobId;

  @override
  ConsumerState<VariantGenerationScreen> createState() =>
      _VariantGenerationScreenState();
}

class _VariantGenerationScreenState
    extends ConsumerState<VariantGenerationScreen> {
  bool _started = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _startGeneration());
  }

  Future<void> _startGeneration() async {
    if (_started) return;
    _started = true;

    final session = ref.read(sessionProvider);
    final userId = session.user?.userId;
    if (userId == null) return;

    // Read the server-side file path from the last uploaded master resume.
    // This is the path MinIO/S3 returned after POST /api/resume/upload.
    final masterResume = ref.read(masterResumeProvider);
    if (masterResume == null) {
      // No resume uploaded — generation blocked. UI shows upload CTA.
      return;
    }

    await ref
        .read(variantGenerationProvider.notifier)
        .generate(
          userId: userId,
          jobId: widget.jobId,
          resumeFilePath: masterResume.filePath,
        );
  }

  @override
  Widget build(BuildContext context) {
    final genState = ref.watch(variantGenerationProvider);
    final masterResume = ref.watch(masterResumeProvider);
    final job = GoRouterState.of(context).extra as JobRecord?;

    // No resume uploaded — block generation with upload CTA.
    if (masterResume == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Generate Variant')),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.xl2),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.upload_file_outlined, size: 56),
                const SizedBox(height: AppSpacing.xl2),
                Text(
                  'No resume uploaded yet',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: AppSpacing.sm),
                Text(
                  'Upload your master resume first so JobHunter can '
                  'tailor a variant for this role.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: AppSpacing.xl3),
                AppButton(
                  label: 'Upload Resume',
                  onPressed: () => context.push('/profile/resume'),
                  icon: Icons.upload_outlined,
                ),
                const SizedBox(height: AppSpacing.sm),
                AppButton(
                  label: 'Go Back',
                  onPressed: () => context.pop(),
                  variant: AppButtonVariant.text,
                ),
              ],
            ),
          ),
        ),
      );
    }

    // On success — navigate to the new variant detail screen.
    if (genState.status == GenerationStatus.success &&
        genState.result != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          ref.read(variantGenerationProvider.notifier).reset();
          context.pushReplacement(
            '/variants/${genState.result!.variantId}',
          );
        }
      });
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Generating Variant'),
        automaticallyImplyLeading:
            genState.status != GenerationStatus.generating,
      ),
      body: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl2),
        child: genState.status == GenerationStatus.error
            ? _ErrorView(
                jobTitle: job?.title ?? '',
                errorMessage: genState.errorMessage ?? 'Generation failed.',
                onRetry: () {
                  ref.read(variantGenerationProvider.notifier).reset();
                  setState(() => _started = false);
                  _startGeneration();
                },
              )
            : _GeneratingView(jobTitle: job?.title ?? ''),
      ),
    );
  }
}

// ── Generating state view ─────────────────────────────────────────────────────

class _GeneratingView extends StatelessWidget {
  const _GeneratingView({required this.jobTitle});
  final String jobTitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: AppSpacing.xl2),
          Text(
            'Analysing job description…',
            style: theme.textTheme.titleMedium,
          ),
          if (jobTitle.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.sm),
            Text(
              jobTitle,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
          ],
          const SizedBox(height: AppSpacing.xl2),
          Text(
            'Tailoring your resume to match the role.\n'
            'This usually takes 15–30 seconds.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// ── Error view ────────────────────────────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  const _ErrorView({
    required this.jobTitle,
    required this.errorMessage,
    required this.onRetry,
  });

  final String jobTitle;
  final String errorMessage;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ErrorBanner(message: errorMessage),
          const SizedBox(height: AppSpacing.xl2),
          AppButton(
            label: 'Retry',
            onPressed: onRetry,
            icon: Icons.refresh_outlined,
          ),
          const SizedBox(height: AppSpacing.sm),
          AppButton(
            label: 'Go Back',
            onPressed: () => Navigator.of(context).pop(),
            variant: AppButtonVariant.text,
          ),
        ],
      ),
    );
  }
}
