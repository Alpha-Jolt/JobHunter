// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'job_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_JobRecord _$JobRecordFromJson(Map<String, dynamic> json) => _JobRecord(
  jobId: json['job_id'] as String,
  title: json['title'] as String,
  companyName: json['company_name'] as String,
  location: json['location'] as String,
  remoteType: json['remote_type'] as String?,
  salaryMin: (json['salary_min'] as num?)?.toInt(),
  salaryMax: (json['salary_max'] as num?)?.toInt(),
  experienceMin: (json['experience_min'] as num?)?.toInt(),
  experienceMax: (json['experience_max'] as num?)?.toInt(),
  description: json['description'] as String?,
  skillsRequired:
      (json['skills_required'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList() ??
      const [],
  jobType: json['job_type'] as String?,
  applyEmail: json['apply_email'] as String?,
  emailTrust: json['email_trust'] as String? ?? 'unknown',
  applyUrl: json['apply_url'] as String?,
  status: json['status'] as String? ?? 'raw',
  source: json['source'] as String?,
);

Map<String, dynamic> _$JobRecordToJson(_JobRecord instance) =>
    <String, dynamic>{
      'job_id': instance.jobId,
      'title': instance.title,
      'company_name': instance.companyName,
      'location': instance.location,
      'remote_type': instance.remoteType,
      'salary_min': instance.salaryMin,
      'salary_max': instance.salaryMax,
      'experience_min': instance.experienceMin,
      'experience_max': instance.experienceMax,
      'description': instance.description,
      'skills_required': instance.skillsRequired,
      'job_type': instance.jobType,
      'apply_email': instance.applyEmail,
      'email_trust': instance.emailTrust,
      'apply_url': instance.applyUrl,
      'status': instance.status,
      'source': instance.source,
    };

_JobListResponse _$JobListResponseFromJson(Map<String, dynamic> json) =>
    _JobListResponse(
      jobs: (json['jobs'] as List<dynamic>)
          .map((e) => JobRecord.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: (json['total'] as num).toInt(),
      page: (json['page'] as num).toInt(),
      pageSize: (json['page_size'] as num).toInt(),
    );

Map<String, dynamic> _$JobListResponseToJson(_JobListResponse instance) =>
    <String, dynamic>{
      'jobs': instance.jobs,
      'total': instance.total,
      'page': instance.page,
      'page_size': instance.pageSize,
    };

_JobCountsResponse _$JobCountsResponseFromJson(Map<String, dynamic> json) =>
    _JobCountsResponse(
      total: (json['total'] as num).toInt(),
      bySource:
          (json['by_source'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, (e as num).toInt()),
          ) ??
          const {},
      byStatus:
          (json['by_status'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, (e as num).toInt()),
          ) ??
          const {},
      byEmailTrust:
          (json['by_email_trust'] as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, (e as num).toInt()),
          ) ??
          const {},
    );

Map<String, dynamic> _$JobCountsResponseToJson(_JobCountsResponse instance) =>
    <String, dynamic>{
      'total': instance.total,
      'by_source': instance.bySource,
      'by_status': instance.byStatus,
      'by_email_trust': instance.byEmailTrust,
    };
