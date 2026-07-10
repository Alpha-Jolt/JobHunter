import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../features/auth/providers/session_provider.dart';
import '../data/application_models.dart';
import '../data/application_repository.dart';

part 'applications_provider.g.dart';

// ── Infrastructure provider ───────────────────────────────────────────────────

@Riverpod(keepAlive: true)
ApplicationRepository applicationRepository(Ref ref) =>
    ApplicationRepository(dioClient: ref.watch(dioClientProvider));

// ── Applications sent today ───────────────────────────────────────────────────

@riverpod
class ApplicationListNotifier extends _$ApplicationListNotifier {
  @override
  Future<SentTodayResponse> build() async {
    final userId = ref.watch(sessionProvider).user?.userId;
    if (userId == null) {
      return const SentTodayResponse(count: 0, applications: []);
    }
    return ref
        .watch(applicationRepositoryProvider)
        .getSentToday(userId);
  }

  Future<void> refresh() async {
    ref.invalidateSelf();
    await future;
  }
}

// ── Single application status ─────────────────────────────────────────────────

@riverpod
Future<ApplicationStatus> applicationStatus(
  Ref ref,
  String applicationId,
) async {
  return ref
      .watch(applicationRepositoryProvider)
      .getStatus(applicationId);
}

// ── Send application flow ─────────────────────────────────────────────────────

enum SendStatus { idle, sending, success, error }

class SendApplicationState {
  const SendApplicationState({
    this.status = SendStatus.idle,
    this.result,
    this.errorMessage,
  });

  final SendStatus status;
  final ApplicationRecord? result;
  final String? errorMessage;

  bool get isSending => status == SendStatus.sending;

  SendApplicationState copyWith({
    SendStatus? status,
    ApplicationRecord? result,
    String? errorMessage,
  }) =>
      SendApplicationState(
        status: status ?? this.status,
        result: result ?? this.result,
        errorMessage: errorMessage,
      );
}

@riverpod
class SendApplicationNotifier extends _$SendApplicationNotifier {
  @override
  SendApplicationState build() => const SendApplicationState();

  Future<bool> send(SendApplicationRequest request) async {
    state = state.copyWith(status: SendStatus.sending);
    try {
      final result =
          await ref.read(applicationRepositoryProvider).send(request);
      state = SendApplicationState(
        status: SendStatus.success,
        result: result,
      );
      // Refresh the application list so today's count updates.
      ref.invalidate(applicationListProvider);
      return true;
    } catch (e) {
      state = SendApplicationState(
        status: SendStatus.error,
        errorMessage: e.toString(),
      );
      return false;
    }
  }

  void reset() => state = const SendApplicationState();
}
