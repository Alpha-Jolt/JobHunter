import 'package:freezed_annotation/freezed_annotation.dart';

part 'job_models.freezed.dart';
part 'job_models.g.dart';

@freezed
abstract class JobRecord with _$JobRecord {
  const factory JobRecord({
    @JsonKey(name: 'job_id') required String jobId,
    required String title,
    @JsonKey(name: 'company_name') required String companyName,
    required String location,
    @JsonKey(name: 'remote_type') String? remoteType,
    @JsonKey(name: 'salary_min') int? salaryMin,
    @JsonKey(name: 'salary_max') int? salaryMax,
    @JsonKey(name: 'experience_min') int? experienceMin,
    @JsonKey(name: 'experience_max') int? experienceMax,
    String? description,
    @JsonKey(name: 'skills_required') @Default([]) List<String> skillsRequired,
    @JsonKey(name: 'job_type') String? jobType,
    @JsonKey(name: 'apply_email') String? applyEmail,
    @JsonKey(name: 'email_trust') @Default('unknown') String emailTrust,
    @JsonKey(name: 'apply_url') String? applyUrl,
    @Default('raw') String status,
    String? source,
  }) = _JobRecord;

  factory JobRecord.fromJson(Map<String, dynamic> json) =>
      _$JobRecordFromJson(json);
}

@freezed
abstract class JobListResponse with _$JobListResponse {
  const factory JobListResponse({
    required List<JobRecord> jobs,
    required int total,
    required int page,
    @JsonKey(name: 'page_size') required int pageSize,
  }) = _JobListResponse;

  factory JobListResponse.fromJson(Map<String, dynamic> json) =>
      _$JobListResponseFromJson(json);
}

@freezed
abstract class JobCountsResponse with _$JobCountsResponse {
  const factory JobCountsResponse({
    required int total,
    @JsonKey(name: 'by_source') @Default({}) Map<String, int> bySource,
    @JsonKey(name: 'by_status') @Default({}) Map<String, int> byStatus,
    @JsonKey(name: 'by_email_trust') @Default({}) Map<String, int> byEmailTrust,
  }) = _JobCountsResponse;

  factory JobCountsResponse.fromJson(Map<String, dynamic> json) =>
      _$JobCountsResponseFromJson(json);
}

/// Active filter state for the job list.
class JobFilters {
  const JobFilters({
    this.remoteType,
    this.jobType,
    this.emailTrust,
    this.location,
    this.experienceMin,
    this.experienceMax,
    this.skills,
  });

  final String? remoteType;
  final String? jobType;
  final String? emailTrust;
  final String? location;
  final int? experienceMin;
  final int? experienceMax;
  final String? skills;

  bool get hasAnyFilter =>
      remoteType != null ||
      jobType != null ||
      emailTrust != null ||
      (location != null && location!.isNotEmpty) ||
      experienceMin != null ||
      experienceMax != null ||
      (skills != null && skills!.isNotEmpty);

  Map<String, dynamic> toQueryParams() {
    final params = <String, dynamic>{};
    if (remoteType != null) params['remote_type'] = remoteType;
    if (jobType != null) params['job_type'] = jobType;
    if (emailTrust != null) params['email_trust'] = emailTrust;
    if (location != null && location!.isNotEmpty) {
      params['location'] = location;
    }
    if (experienceMin != null) params['experience_min'] = experienceMin;
    if (experienceMax != null) params['experience_max'] = experienceMax;
    if (skills != null && skills!.isNotEmpty) params['skills'] = skills;
    return params;
  }

  JobFilters copyWith({
    String? remoteType,
    String? jobType,
    String? emailTrust,
    String? location,
    int? experienceMin,
    int? experienceMax,
    String? skills,
    bool clearRemoteType = false,
    bool clearJobType = false,
    bool clearEmailTrust = false,
    bool clearLocation = false,
    bool clearExperience = false,
    bool clearSkills = false,
  }) =>
      JobFilters(
        remoteType: clearRemoteType ? null : remoteType ?? this.remoteType,
        jobType: clearJobType ? null : jobType ?? this.jobType,
        emailTrust: clearEmailTrust ? null : emailTrust ?? this.emailTrust,
        location: clearLocation ? null : location ?? this.location,
        experienceMin:
            clearExperience ? null : experienceMin ?? this.experienceMin,
        experienceMax:
            clearExperience ? null : experienceMax ?? this.experienceMax,
        skills: clearSkills ? null : skills ?? this.skills,
      );

  static const empty = JobFilters();
}
