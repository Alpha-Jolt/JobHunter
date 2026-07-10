// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'profile_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_UserExperience _$UserExperienceFromJson(Map<String, dynamic> json) =>
    _UserExperience(
      expId: json['exp_id'] as String?,
      jobTitle: json['job_title'] as String,
      company: json['company'] as String,
      location: json['location'] as String,
      startDate: json['start_date'] as String,
      endDate: json['end_date'] as String?,
      isCurrent: json['is_current'] as bool? ?? false,
      description: json['description'] as String?,
    );

Map<String, dynamic> _$UserExperienceToJson(_UserExperience instance) =>
    <String, dynamic>{
      'exp_id': instance.expId,
      'job_title': instance.jobTitle,
      'company': instance.company,
      'location': instance.location,
      'start_date': instance.startDate,
      'end_date': instance.endDate,
      'is_current': instance.isCurrent,
      'description': instance.description,
    };

_UserEducation _$UserEducationFromJson(Map<String, dynamic> json) =>
    _UserEducation(
      eduId: json['edu_id'] as String?,
      institution: json['institution'] as String,
      degree: json['degree'] as String,
      fieldOfStudy: json['field_of_study'] as String?,
      startYear: (json['start_year'] as num).toInt(),
      endYear: (json['end_year'] as num?)?.toInt(),
      isCurrent: json['is_current'] as bool? ?? false,
      gpa: (json['gpa'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$UserEducationToJson(_UserEducation instance) =>
    <String, dynamic>{
      'edu_id': instance.eduId,
      'institution': instance.institution,
      'degree': instance.degree,
      'field_of_study': instance.fieldOfStudy,
      'start_year': instance.startYear,
      'end_year': instance.endYear,
      'is_current': instance.isCurrent,
      'gpa': instance.gpa,
    };

_UserProject _$UserProjectFromJson(Map<String, dynamic> json) => _UserProject(
  projId: json['proj_id'] as String?,
  name: json['name'] as String,
  description: json['description'] as String?,
  techStack:
      (json['tech_stack'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
  projectUrl: json['project_url'] as String?,
  startDate: json['start_date'] as String?,
  endDate: json['end_date'] as String?,
);

Map<String, dynamic> _$UserProjectToJson(_UserProject instance) =>
    <String, dynamic>{
      'proj_id': instance.projId,
      'name': instance.name,
      'description': instance.description,
      'tech_stack': instance.techStack,
      'project_url': instance.projectUrl,
      'start_date': instance.startDate,
      'end_date': instance.endDate,
    };

_UserSkill _$UserSkillFromJson(Map<String, dynamic> json) =>
    _UserSkill(name: json['name'] as String, level: json['level'] as String?);

Map<String, dynamic> _$UserSkillToJson(_UserSkill instance) =>
    <String, dynamic>{'name': instance.name, 'level': instance.level};

_UserCertification _$UserCertificationFromJson(Map<String, dynamic> json) =>
    _UserCertification(
      name: json['name'] as String,
      issuer: json['issuer'] as String?,
      issuedDate: json['issued_date'] as String?,
      credentialUrl: json['credential_url'] as String?,
    );

Map<String, dynamic> _$UserCertificationToJson(_UserCertification instance) =>
    <String, dynamic>{
      'name': instance.name,
      'issuer': instance.issuer,
      'issued_date': instance.issuedDate,
      'credential_url': instance.credentialUrl,
    };

_UserLanguage _$UserLanguageFromJson(Map<String, dynamic> json) =>
    _UserLanguage(
      name: json['name'] as String,
      proficiency: json['proficiency'] as String?,
    );

Map<String, dynamic> _$UserLanguageToJson(_UserLanguage instance) =>
    <String, dynamic>{
      'name': instance.name,
      'proficiency': instance.proficiency,
    };

_UserAchievement _$UserAchievementFromJson(Map<String, dynamic> json) =>
    _UserAchievement(
      title: json['title'] as String,
      description: json['description'] as String?,
      date: json['date'] as String?,
    );

Map<String, dynamic> _$UserAchievementToJson(_UserAchievement instance) =>
    <String, dynamic>{
      'title': instance.title,
      'description': instance.description,
      'date': instance.date,
    };

_UserSocialLink _$UserSocialLinkFromJson(Map<String, dynamic> json) =>
    _UserSocialLink(
      platform: json['platform'] as String,
      url: json['url'] as String,
    );

Map<String, dynamic> _$UserSocialLinkToJson(_UserSocialLink instance) =>
    <String, dynamic>{'platform': instance.platform, 'url': instance.url};

_UserProfile _$UserProfileFromJson(Map<String, dynamic> json) => _UserProfile(
  userId: json['user_id'] as String,
  username: json['username'] as String?,
  headline: json['headline'] as String?,
  bio: json['bio'] as String?,
  location: json['location'] as String?,
  avatarKey: json['avatar_key'] as String?,
  avatarUrl: json['avatar_url'] as String?,
  isPublic: json['is_public'] as bool? ?? false,
  experiences:
      (json['experiences'] as List<dynamic>?)
          ?.map((e) => UserExperience.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  education:
      (json['education'] as List<dynamic>?)
          ?.map((e) => UserEducation.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  projects:
      (json['projects'] as List<dynamic>?)
          ?.map((e) => UserProject.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  skills:
      (json['skills'] as List<dynamic>?)
          ?.map((e) => UserSkill.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  certifications:
      (json['certifications'] as List<dynamic>?)
          ?.map((e) => UserCertification.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  languages:
      (json['languages'] as List<dynamic>?)
          ?.map((e) => UserLanguage.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  achievements:
      (json['achievements'] as List<dynamic>?)
          ?.map((e) => UserAchievement.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
  socialLinks:
      (json['social_links'] as List<dynamic>?)
          ?.map((e) => UserSocialLink.fromJson(e as Map<String, dynamic>))
          .toList() ??
      const [],
);

Map<String, dynamic> _$UserProfileToJson(_UserProfile instance) =>
    <String, dynamic>{
      'user_id': instance.userId,
      'username': instance.username,
      'headline': instance.headline,
      'bio': instance.bio,
      'location': instance.location,
      'avatar_key': instance.avatarKey,
      'avatar_url': instance.avatarUrl,
      'is_public': instance.isPublic,
      'experiences': instance.experiences,
      'education': instance.education,
      'projects': instance.projects,
      'skills': instance.skills,
      'certifications': instance.certifications,
      'languages': instance.languages,
      'achievements': instance.achievements,
      'social_links': instance.socialLinks,
    };

_ProfileUpsertRequest _$ProfileUpsertRequestFromJson(
  Map<String, dynamic> json,
) => _ProfileUpsertRequest(
  username: json['username'] as String?,
  headline: json['headline'] as String?,
  bio: json['bio'] as String?,
  location: json['location'] as String?,
  isPublic: json['is_public'] as bool?,
);

Map<String, dynamic> _$ProfileUpsertRequestToJson(
  _ProfileUpsertRequest instance,
) => <String, dynamic>{
  'username': instance.username,
  'headline': instance.headline,
  'bio': instance.bio,
  'location': instance.location,
  'is_public': instance.isPublic,
};

_MasterResume _$MasterResumeFromJson(Map<String, dynamic> json) =>
    _MasterResume(
      resumeId: json['resume_id'] as String,
      fileName: json['file_name'] as String,
      filePath: json['file_path'] as String,
    );

Map<String, dynamic> _$MasterResumeToJson(_MasterResume instance) =>
    <String, dynamic>{
      'resume_id': instance.resumeId,
      'file_name': instance.fileName,
      'file_path': instance.filePath,
    };
