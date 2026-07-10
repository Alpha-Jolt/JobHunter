import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../features/auth/providers/session_provider.dart';
import '../../profile/data/profile_models.dart';
import '../data/resume_repository.dart';

part 'resume_provider.g.dart';

// ── Infrastructure provider ───────────────────────────────────────────────────

@Riverpod(keepAlive: true)
ResumeRepository resumeRepository(Ref ref) =>
    ResumeRepository(dioClient: ref.watch(dioClientProvider));

// ── Last uploaded master resume (keepAlive — survives navigation) ─────────────

/// Holds the most recently uploaded [MasterResume] for the session.
/// VariantGenerationScreen reads `filePath` from this to populate
/// the `resume_file_path` field required by POST /api/ai/generate.
@Riverpod(keepAlive: true)
class MasterResumeNotifier extends _$MasterResumeNotifier {
  @override
  MasterResume? build() => null;

  void set(MasterResume resume) => state = resume;
  void clear() => state = null;
}

// ── Upload state ──────────────────────────────────────────────────────────────

enum ResumeUploadStatus { idle, uploading, success, error }

class ResumeUploadState {
  const ResumeUploadState({
    this.status = ResumeUploadStatus.idle,
    this.result,
    this.errorMessage,
  });

  final ResumeUploadStatus status;
  final MasterResume? result;
  final String? errorMessage;

  bool get isUploading => status == ResumeUploadStatus.uploading;

  ResumeUploadState copyWith({
    ResumeUploadStatus? status,
    MasterResume? result,
    String? errorMessage,
  }) =>
      ResumeUploadState(
        status: status ?? this.status,
        result: result ?? this.result,
        errorMessage: errorMessage,
      );
}

@riverpod
class ResumeUploadNotifier extends _$ResumeUploadNotifier {
  @override
  ResumeUploadState build() => const ResumeUploadState();

  Future<void> upload(String filePath, String fileName) async {
    state = state.copyWith(status: ResumeUploadStatus.uploading);
    try {
      final result = await ref
          .read(resumeRepositoryProvider)
          .upload(filePath, fileName);
      state = ResumeUploadState(
        status: ResumeUploadStatus.success,
        result: result,
      );
      // Persist the uploaded resume so VariantGenerationScreen can read it.
      ref.read(masterResumeProvider.notifier).set(result);
    } catch (e) {
      state = ResumeUploadState(
        status: ResumeUploadStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  void reset() => state = const ResumeUploadState();
}
