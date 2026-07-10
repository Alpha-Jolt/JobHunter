import 'package:dio/dio.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/app_error.dart';
import '../../../core/network/dio_client.dart';
import 'profile_models.dart';

/// Repository for all profile and resume operations.
class ProfileRepository {
  const ProfileRepository({required DioClient dioClient})
      : _client = dioClient;

  final DioClient _client;

  // ── Own profile ─────────────────────────────────────────────────────────────

  Future<UserProfile> getMyProfile() async {
    try {
      final response = await _client.dio.get(ApiEndpoints.profileMe);
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<UserProfile> upsertProfile(ProfileUpsertRequest request) async {
    try {
      final response = await _client.dio.put(
        ApiEndpoints.profileMe,
        data: request.toJson()
          ..removeWhere((_, v) => v == null),
      );
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<String> uploadAvatar(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath),
      });
      final response = await _client.dio.post(
        ApiEndpoints.profileAvatar,
        data: formData,
      );
      return response.data['avatar_url'] as String;
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> deleteAvatar() async {
    try {
      await _client.dio.delete(ApiEndpoints.profileAvatar);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Public profile ──────────────────────────────────────────────────────────

  Future<UserProfile> getPublicProfile(String username) async {
    try {
      final response =
          await _client.dio.get(ApiEndpoints.publicProfile(username));
      return UserProfile.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Experience ──────────────────────────────────────────────────────────────

  Future<void> addExperience(UserExperience exp) async {
    try {
      await _client.dio.post(
        ApiEndpoints.profileExperience,
        data: exp.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> updateExperience(String id, UserExperience exp) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileExperienceById(id),
        data: exp.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> deleteExperience(String id) async {
    try {
      await _client.dio.delete(ApiEndpoints.profileExperienceById(id));
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Education ───────────────────────────────────────────────────────────────

  Future<void> addEducation(UserEducation edu) async {
    try {
      await _client.dio.post(
        ApiEndpoints.profileEducation,
        data: edu.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> updateEducation(String id, UserEducation edu) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileEducationById(id),
        data: edu.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> deleteEducation(String id) async {
    try {
      await _client.dio.delete(ApiEndpoints.profileEducationById(id));
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Projects ─────────────────────────────────────────────────────────────────

  Future<void> addProject(UserProject project) async {
    try {
      await _client.dio.post(
        ApiEndpoints.profileProjects,
        data: project.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> updateProject(String id, UserProject project) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileProjectById(id),
        data: project.toJson(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> deleteProject(String id) async {
    try {
      await _client.dio.delete(ApiEndpoints.profileProjectById(id));
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  // ── Bulk-replace sub-resources ───────────────────────────────────────────────

  Future<void> replaceSkills(List<UserSkill> skills) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileSkills,
        data: skills.map((s) => s.toJson()).toList(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> replaceCertifications(List<UserCertification> certs) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileCertifications,
        data: certs.map((c) => c.toJson()).toList(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> replaceLanguages(List<UserLanguage> languages) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileLanguages,
        data: languages.map((l) => l.toJson()).toList(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> replaceAchievements(List<UserAchievement> achievements) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileAchievements,
        data: achievements.map((a) => a.toJson()).toList(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }

  Future<void> replaceSocialLinks(List<UserSocialLink> links) async {
    try {
      await _client.dio.put(
        ApiEndpoints.profileSocialLinks,
        data: links.map((l) => l.toJson()).toList(),
      );
    } on DioException catch (e) {
      throw e.error is AppError ? e.error as AppError : extractAppError(e);
    }
  }
}
