import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../features/auth/providers/session_provider.dart';
import '../../resume/providers/resume_provider.dart';
import '../data/profile_models.dart';
import '../data/profile_repository.dart';

part 'profile_provider.g.dart';

// ── Infrastructure provider ───────────────────────────────────────────────────

@Riverpod(keepAlive: true)
ProfileRepository profileRepository(Ref ref) => ProfileRepository(
      dioClient: ref.watch(dioClientProvider),
    );

// ── Own profile ───────────────────────────────────────────────────────────────

@riverpod
class ProfileNotifier extends _$ProfileNotifier {
  @override
  Future<UserProfile> build() async {
    final profile = await ref.watch(profileRepositoryProvider).getMyProfile();
    // If the backend returns a master resume on this profile, seed
    // MasterResumeNotifier so VariantGenerationScreen can use it immediately
    // without requiring the user to re-upload in the same session.
    if (profile.masterResume != null) {
      ref.read(masterResumeProvider.notifier).set(profile.masterResume!);
    }
    return profile;
  }

  /// Re-fetch the profile from the server (e.g., after edit or avatar change).
  Future<void> refresh() async {
    ref.invalidateSelf();
    await future;
  }

  /// Upsert basic profile fields and refresh.
  Future<void> upsert(ProfileUpsertRequest request) async {
    final repo = ref.read(profileRepositoryProvider);
    final updated = await repo.upsertProfile(request);
    state = AsyncData(updated);
    // Also sync the display name on session user record.
    ref.read(sessionProvider.notifier).updateUser(
          ref.read(sessionProvider).user!,
        );
  }

  /// Upload a new avatar and refresh.
  Future<void> uploadAvatar(String filePath) async {
    await ref.read(profileRepositoryProvider).uploadAvatar(filePath);
    await refresh();
  }

  /// Delete the current avatar and refresh.
  Future<void> deleteAvatar() async {
    await ref.read(profileRepositoryProvider).deleteAvatar();
    await refresh();
  }
}

// ── Public profile ────────────────────────────────────────────────────────────

@riverpod
Future<UserProfile> publicProfile(Ref ref, String username) async {
  return ref.watch(profileRepositoryProvider).getPublicProfile(username);
}
