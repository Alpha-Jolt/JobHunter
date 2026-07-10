import 'package:freezed_annotation/freezed_annotation.dart';

part 'profile_models.freezed.dart';
part 'profile_models.g.dart';

// ── Sub-resource models ───────────────────────────────────────────────────────

@freezed
abstract class UserExperience with _$UserExperience {
  const factory UserExperience({
    @JsonKey(name: 'exp_id') String? expId,
    @JsonKey(name: 'job_title') required String jobTitle,
    required String company,
    required String location,
    @JsonKey(name: 'start_date') required String startDate,
    @JsonKey(name: 'end_date') String? endDate,
    @JsonKey(name: 'is_current') @Default(false) bool isCurrent,
    String? description,
  }) = _UserExperience;

  factory UserExperience.fromJson(Map<String, dynamic> json) =>
      _$UserExperienceFromJson(json);
}

@freezed
abstract class UserEducation with _$UserEducation {
  const factory UserEducation({
    @JsonKey(name: 'edu_id') String? eduId,
    required String institution,
    required String degree,
    @JsonKey(name: 'field_of_study') String? fieldOfStudy,
    @JsonKey(name: 'start_year') required int startYear,
    @JsonKey(name: 'end_year') int? endYear,
    @JsonKey(name: 'is_current') @Default(false) bool isCurrent,
    double? gpa,
  }) = _UserEducation;

  factory UserEducation.fromJson(Map<String, dynamic> json) =>
      _$UserEducationFromJson(json);
}

@freezed
abstract class UserProject with _$UserProject {
  const factory UserProject({
    @JsonKey(name: 'proj_id') String? projId,
    required String name,
    String? description,
    @JsonKey(name: 'tech_stack') @Default([]) List<String> techStack,
    @JsonKey(name: 'project_url') String? projectUrl,
    @JsonKey(name: 'start_date') String? startDate,
    @JsonKey(name: 'end_date') String? endDate,
  }) = _UserProject;

  factory UserProject.fromJson(Map<String, dynamic> json) =>
      _$UserProjectFromJson(json);
}

@freezed
abstract class UserSkill with _$UserSkill {
  const factory UserSkill({
    required String name,
    String? level,
  }) = _UserSkill;

  factory UserSkill.fromJson(Map<String, dynamic> json) =>
      _$UserSkillFromJson(json);
}

@freezed
abstract class UserCertification with _$UserCertification {
  const factory UserCertification({
    required String name,
    String? issuer,
    @JsonKey(name: 'issued_date') String? issuedDate,
    @JsonKey(name: 'credential_url') String? credentialUrl,
  }) = _UserCertification;

  factory UserCertification.fromJson(Map<String, dynamic> json) =>
      _$UserCertificationFromJson(json);
}

@freezed
abstract class UserLanguage with _$UserLanguage {
  const factory UserLanguage({
    required String name,
    String? proficiency,
  }) = _UserLanguage;

  factory UserLanguage.fromJson(Map<String, dynamic> json) =>
      _$UserLanguageFromJson(json);
}

@freezed
abstract class UserAchievement with _$UserAchievement {
  const factory UserAchievement({
    required String title,
    String? description,
    String? date,
  }) = _UserAchievement;

  factory UserAchievement.fromJson(Map<String, dynamic> json) =>
      _$UserAchievementFromJson(json);
}

@freezed
abstract class UserSocialLink with _$UserSocialLink {
  const factory UserSocialLink({
    required String platform,
    required String url,
  }) = _UserSocialLink;

  factory UserSocialLink.fromJson(Map<String, dynamic> json) =>
      _$UserSocialLinkFromJson(json);
}

// ── Full profile model ────────────────────────────────────────────────────────

@freezed
abstract class UserProfile with _$UserProfile {
  const factory UserProfile({
    @JsonKey(name: 'user_id') required String userId,
    String? username,
    String? headline,
    String? bio,
    String? location,
    @JsonKey(name: 'avatar_key') String? avatarKey,
    @JsonKey(name: 'avatar_url') String? avatarUrl,
    @JsonKey(name: 'is_public') @Default(false) bool isPublic,
    @Default([]) List<UserExperience> experiences,
    @Default([]) List<UserEducation> education,
    @Default([]) List<UserProject> projects,
    @Default([]) List<UserSkill> skills,
    @Default([]) List<UserCertification> certifications,
    @Default([]) List<UserLanguage> languages,
    @Default([]) List<UserAchievement> achievements,
    @JsonKey(name: 'social_links') @Default([]) List<UserSocialLink> socialLinks,
    // Master resume — populated when backend returns it on GET /api/profile/me.
    // Used by VariantGenerationScreen to obtain the server-side file path.
    @JsonKey(name: 'master_resume') MasterResume? masterResume,
  }) = _UserProfile;

  factory UserProfile.fromJson(Map<String, dynamic> json) =>
      _$UserProfileFromJson(json);
}

// ── Upsert request ────────────────────────────────────────────────────────────

@freezed
abstract class ProfileUpsertRequest with _$ProfileUpsertRequest {
  const factory ProfileUpsertRequest({
    String? username,
    String? headline,
    String? bio,
    String? location,
    @JsonKey(name: 'is_public') bool? isPublic,
  }) = _ProfileUpsertRequest;

  factory ProfileUpsertRequest.fromJson(Map<String, dynamic> json) =>
      _$ProfileUpsertRequestFromJson(json);
}

// ── Master resume metadata ────────────────────────────────────────────────────

@freezed
abstract class MasterResume with _$MasterResume {
  const factory MasterResume({
    @JsonKey(name: 'resume_id') required String resumeId,
    @JsonKey(name: 'file_name') required String fileName,
    @JsonKey(name: 'file_path') required String filePath,
  }) = _MasterResume;

  factory MasterResume.fromJson(Map<String, dynamic> json) =>
      _$MasterResumeFromJson(json);
}
