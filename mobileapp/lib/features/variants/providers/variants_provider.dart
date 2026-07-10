import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../features/auth/providers/session_provider.dart';
import '../data/variant_models.dart';
import '../data/variant_repository.dart';

part 'variants_provider.g.dart';

// ── Infrastructure provider ───────────────────────────────────────────────────

@Riverpod(keepAlive: true)
VariantRepository variantRepository(Ref ref) =>
    VariantRepository(dioClient: ref.watch(dioClientProvider));

// ── Pending variants list ─────────────────────────────────────────────────────

@riverpod
class VariantListNotifier extends _$VariantListNotifier {
  @override
  Future<PendingVariantsResponse> build() async {
    final userId = ref.watch(sessionProvider).user?.userId;
    if (userId == null) {
      return const PendingVariantsResponse(variants: [], total: 0);
    }
    return ref.watch(variantRepositoryProvider).getPendingVariants(userId);
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
    await future;
  }
}

// ── Variant preview ───────────────────────────────────────────────────────────

@riverpod
Future<VariantPreview> variantPreview(Ref ref, String variantId) async {
  return ref.watch(variantRepositoryProvider).getPreview(variantId);
}

// ── Variant generation ────────────────────────────────────────────────────────

enum GenerationStatus { idle, generating, success, error }

class GenerationState {
  const GenerationState({
    this.status = GenerationStatus.idle,
    this.result,
    this.errorMessage,
  });

  final GenerationStatus status;
  final VariantRecord? result;
  final String? errorMessage;

  bool get isGenerating => status == GenerationStatus.generating;

  GenerationState copyWith({
    GenerationStatus? status,
    VariantRecord? result,
    String? errorMessage,
  }) =>
      GenerationState(
        status: status ?? this.status,
        result: result ?? this.result,
        errorMessage: errorMessage,
      );
}

@riverpod
class VariantGenerationNotifier extends _$VariantGenerationNotifier {
  @override
  GenerationState build() => const GenerationState();

  Future<void> generate({
    required String userId,
    required String jobId,
    required String resumeFilePath,
  }) async {
    state = state.copyWith(status: GenerationStatus.generating);
    try {
      final result = await ref.read(variantRepositoryProvider).generate(
            GenerateVariantRequest(
              userId: userId,
              jobId: jobId,
              resumeFilePath: resumeFilePath,
            ),
          );
      state = GenerationState(
        status: GenerationStatus.success,
        result: result,
      );
      // Refresh the variant list to include this new variant.
      ref.invalidate(variantListProvider);
    } catch (e) {
      state = GenerationState(
        status: GenerationStatus.error,
        errorMessage: e.toString(),
      );
    }
  }

  void reset() => state = const GenerationState();
}

// ── Approval flow ─────────────────────────────────────────────────────────────

enum ApprovalFlowStatus { idle, fetchingToken, confirming, approving, success, error }

class ApprovalFlowState {
  const ApprovalFlowState({
    this.status = ApprovalFlowStatus.idle,
    this.errorMessage,
  });

  final ApprovalFlowStatus status;
  final String? errorMessage;

  bool get isBusy =>
      status == ApprovalFlowStatus.fetchingToken ||
      status == ApprovalFlowStatus.approving;

  ApprovalFlowState copyWith({
    ApprovalFlowStatus? status,
    String? errorMessage,
  }) =>
      ApprovalFlowState(
        status: status ?? this.status,
        errorMessage: errorMessage,
      );
}

@riverpod
class ApprovalFlowNotifier extends _$ApprovalFlowNotifier {
  String? _liveToken;

  @override
  ApprovalFlowState build() => const ApprovalFlowState();

  /// Step 1: Fetch a fresh approval token from the server.
  /// This MUST be called before opening ApprovalConfirmSheet.
  Future<String?> fetchToken(String variantId) async {
    state = state.copyWith(status: ApprovalFlowStatus.fetchingToken);
    try {
      final token = await ref
          .read(variantRepositoryProvider)
          .fetchApprovalToken(variantId);
      _liveToken = token;
      state = state.copyWith(status: ApprovalFlowStatus.confirming);
      return token;
    } catch (e) {
      _liveToken = null;
      state = ApprovalFlowState(
        status: ApprovalFlowStatus.error,
        errorMessage: e.toString(),
      );
      return null;
    }
  }

  /// Step 2: Approve using the live token fetched in step 1.
  /// Fails closed if no live token is present.
  Future<bool> approve(String variantId) async {
    final token = _liveToken;
    if (token == null) {
      state = const ApprovalFlowState(
        status: ApprovalFlowStatus.error,
        errorMessage: 'Approval token unavailable. Please try again.',
      );
      return false;
    }

    state = state.copyWith(status: ApprovalFlowStatus.approving);
    try {
      await ref
          .read(variantRepositoryProvider)
          .approve(variantId, token);
      _liveToken = null;
      state = state.copyWith(status: ApprovalFlowStatus.success);
      ref.invalidate(variantListProvider);
      ref.invalidate(variantPreviewProvider(variantId));
      return true;
    } catch (e) {
      _liveToken = null;
      state = ApprovalFlowState(
        status: ApprovalFlowStatus.error,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  /// Reject a variant with optional feedback.
  Future<bool> reject(String variantId, {String? feedback}) async {
    state = state.copyWith(status: ApprovalFlowStatus.approving);
    try {
      await ref
          .read(variantRepositoryProvider)
          .reject(variantId, userFeedback: feedback);
      state = state.copyWith(status: ApprovalFlowStatus.success);
      ref.invalidate(variantListProvider);
      ref.invalidate(variantPreviewProvider(variantId));
      return true;
    } catch (e) {
      state = ApprovalFlowState(
        status: ApprovalFlowStatus.error,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  void reset() {
    _liveToken = null;
    state = const ApprovalFlowState();
  }
}
