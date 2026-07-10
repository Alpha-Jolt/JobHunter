import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/utils/file_utils.dart';
import '../../../core/utils/secure_screen_mixin.dart';
import '../../../shared/components/app_button.dart';
import '../../../shared/components/error_banner.dart';
import '../../../shared/components/loading_overlay.dart';
import '../providers/resume_provider.dart';

class ResumeUploadScreen extends ConsumerStatefulWidget {
  const ResumeUploadScreen({super.key});

  @override
  ConsumerState<ResumeUploadScreen> createState() => _ResumeUploadScreenState();
}

class _ResumeUploadScreenState extends ConsumerState<ResumeUploadScreen>
    with SecureScreenMixin {
  PlatformFile? _pickedFile;
  String? _validationError;

  Future<void> _pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'docx'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;

    final file = result.files.first;
    final bytes = file.bytes;
    if (bytes == null || file.path == null) {
      setState(() => _validationError = 'Could not read the selected file.');
      return;
    }

    final error = FileUtils.validateResume(
      file.name,
      file.size,
      bytes,
    );

    setState(() {
      _validationError = error;
      if (error == null) {
        _pickedFile = file;
        ref.read(resumeUploadProvider.notifier).reset();
      }
    });
  }

  Future<void> _upload() async {
    final file = _pickedFile;
    if (file == null || file.path == null) return;

    await ref
        .read(resumeUploadProvider.notifier)
        .upload(file.path!, file.name);

    final state = ref.read(resumeUploadProvider);
    if (state.status == ResumeUploadStatus.success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Resume uploaded successfully.')),
      );
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final uploadState = ref.watch(resumeUploadProvider);
    final theme = Theme.of(context);

    return LoadingOverlay(
      isLoading: uploadState.isUploading,
      child: Scaffold(
        appBar: AppBar(title: const Text('Upload Resume')),
        body: Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Upload your master resume',
                style: theme.textTheme.titleLarge,
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                'PDF or DOCX · Maximum 10 MB\n'
                'This is your base resume. The AI will create tailored variants for each job.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: AppSpacing.xl3),

              // File picker area
              GestureDetector(
                onTap: uploadState.isUploading ? null : _pickFile,
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(AppSpacing.xl3),
                  decoration: BoxDecoration(
                    border: Border.all(
                      color: _pickedFile != null
                          ? AppColors.brandOrange
                          : theme.colorScheme.outlineVariant,
                      width: _pickedFile != null ? 2 : 1,
                      style: BorderStyle.solid,
                    ),
                    borderRadius: BorderRadius.circular(12),
                    color: _pickedFile != null
                        ? AppColors.brandOrange.withValues(alpha: 0.05)
                        : theme.colorScheme.surfaceContainerHighest
                            .withValues(alpha: 0.4),
                  ),
                  child: Column(
                    children: [
                      Icon(
                        _pickedFile != null
                            ? Icons.description_outlined
                            : Icons.upload_file_outlined,
                        size: 48,
                        color: _pickedFile != null
                            ? AppColors.brandOrange
                            : theme.colorScheme.onSurfaceVariant,
                      ),
                      const SizedBox(height: AppSpacing.md),
                      Text(
                        _pickedFile != null
                            ? _pickedFile!.name
                            : 'Tap to choose a file',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          fontWeight: _pickedFile != null
                              ? FontWeight.w600
                              : FontWeight.normal,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      if (_pickedFile != null) ...[
                        const SizedBox(height: AppSpacing.xs),
                        Text(
                          '${(_pickedFile!.size / 1024).toStringAsFixed(1)} KB',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              if (_validationError != null) ...[
                const SizedBox(height: AppSpacing.sm),
                ErrorBanner(message: _validationError!),
              ],

              if (uploadState.status == ResumeUploadStatus.error &&
                  uploadState.errorMessage != null) ...[
                const SizedBox(height: AppSpacing.sm),
                ErrorBanner(message: uploadState.errorMessage!),
              ],

              const Spacer(),

              AppButton(
                label: 'Upload Resume',
                onPressed: (_pickedFile == null || uploadState.isUploading)
                    ? null
                    : _upload,
                isLoading: uploadState.isUploading,
                icon: Icons.upload_outlined,
              ),
              const SizedBox(height: AppSpacing.sm),
              if (_pickedFile != null)
                AppButton(
                  label: 'Choose Different File',
                  onPressed:
                      uploadState.isUploading ? null : _pickFile,
                  variant: AppButtonVariant.text,
                ),
            ],
          ),
        ),
      ),
    );
  }
}
