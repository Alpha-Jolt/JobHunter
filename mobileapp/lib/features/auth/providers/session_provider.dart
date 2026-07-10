import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/storage/secure_storage.dart';
import '../data/auth_models.dart';
import '../data/auth_repository.dart';

part 'session_provider.g.dart';

// ── Infrastructure providers ──────────────────────────────────────────────────

@Riverpod(keepAlive: true)
SecureStorage secureStorage(Ref ref) => SecureStorage();

@Riverpod(keepAlive: true)
DioClient dioClient(Ref ref) => DioClient.instance;

@Riverpod(keepAlive: true)
AuthRepository authRepository(Ref ref) => AuthRepository(
      dioClient: ref.watch(dioClientProvider),
      secureStorage: ref.watch(secureStorageProvider),
    );

// ── Session state ──────────────────────────────────────────────────────────────

enum SessionStatus { loading, authenticated, unauthenticated }

class SessionState {
  const SessionState({
    required this.status,
    this.user,
    this.error,
  });

  final SessionStatus status;
  final UserRecord? user;
  final String? error;

  bool get isAuthenticated => status == SessionStatus.authenticated;
  bool get isLoading => status == SessionStatus.loading;

  SessionState copyWith({
    SessionStatus? status,
    UserRecord? user,
    String? error,
  }) =>
      SessionState(
        status: status ?? this.status,
        user: user ?? this.user,
        error: error,
      );

  static const loading = SessionState(status: SessionStatus.loading);
  static const unauthenticated =
      SessionState(status: SessionStatus.unauthenticated);
}

@Riverpod(keepAlive: true)
class Session extends _$Session {
  @override
  SessionState build() {
    // Wire up session expiry callback
    DioClient.instance.onSessionExpired = () {
      state = SessionState.unauthenticated;
    };
    return SessionState.loading;
  }

  /// Called on app start — attempts silent token refresh.
  Future<void> initialize() async {
    state = SessionState.loading;
    final repo = ref.read(authRepositoryProvider);
    final refreshed = await repo.refreshToken();
    if (refreshed) {
      try {
        final user = await repo.getMe();
        state = SessionState(
          status: SessionStatus.authenticated,
          user: user,
        );
      } catch (_) {
        state = SessionState.unauthenticated;
      }
    } else {
      state = SessionState.unauthenticated;
    }
  }

  /// Login with email and password.
  Future<void> login(LoginRequest request) async {
    state = SessionState.loading;
    final repo = ref.read(authRepositoryProvider);
    try {
      final user = await repo.login(request);
      state = SessionState(
        status: SessionStatus.authenticated,
        user: user,
      );
    } catch (e) {
      state = SessionState(
        status: SessionStatus.unauthenticated,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Register a new account and auto-login.
  Future<void> register(RegisterRequest request) async {
    state = SessionState.loading;
    final repo = ref.read(authRepositoryProvider);
    try {
      await repo.register(request);
      await login(LoginRequest(
        email: request.email,
        password: request.password,
      ));
    } catch (e) {
      state = SessionState(
        status: SessionStatus.unauthenticated,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Logout and clear all session state.
  Future<void> logout() async {
    final repo = ref.read(authRepositoryProvider);
    await repo.logout();
    state = SessionState.unauthenticated;
  }

  /// Update the stored user record (e.g. after profile changes).
  void updateUser(UserRecord user) {
    state = state.copyWith(
      status: SessionStatus.authenticated,
      user: user,
    );
  }
}
