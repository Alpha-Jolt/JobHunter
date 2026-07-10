// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'application_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ApplicationRecord _$ApplicationRecordFromJson(Map<String, dynamic> json) =>
    _ApplicationRecord(
      applicationId: json['application_id'] as String,
      userId: json['user_id'] as String,
      jobId: json['job_id'] as String,
      resumeVariantId: json['resume_variant_id'] as String,
      status: json['status'] as String? ?? 'sent',
      sentAt: json['sent_at'] == null
          ? null
          : DateTime.parse(json['sent_at'] as String),
      replyCount: (json['reply_count'] as num?)?.toInt() ?? 0,
      threadId: json['thread_id'] as String?,
      jobTitle: json['job_title'] as String?,
      companyName: json['company_name'] as String?,
    );

Map<String, dynamic> _$ApplicationRecordToJson(_ApplicationRecord instance) =>
    <String, dynamic>{
      'application_id': instance.applicationId,
      'user_id': instance.userId,
      'job_id': instance.jobId,
      'resume_variant_id': instance.resumeVariantId,
      'status': instance.status,
      'sent_at': instance.sentAt?.toIso8601String(),
      'reply_count': instance.replyCount,
      'thread_id': instance.threadId,
      'job_title': instance.jobTitle,
      'company_name': instance.companyName,
    };

_SentTodayResponse _$SentTodayResponseFromJson(Map<String, dynamic> json) =>
    _SentTodayResponse(
      count: (json['count'] as num).toInt(),
      applications: (json['applications'] as List<dynamic>)
          .map((e) => ApplicationRecord.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$SentTodayResponseToJson(_SentTodayResponse instance) =>
    <String, dynamic>{
      'count': instance.count,
      'applications': instance.applications,
    };

_SendApplicationRequest _$SendApplicationRequestFromJson(
  Map<String, dynamic> json,
) => _SendApplicationRequest(
  userId: json['user_id'] as String,
  jobId: json['job_id'] as String,
  variantId: json['variant_id'] as String,
  userName: json['user_name'] as String,
  userEmail: json['user_email'] as String,
  userPhone: json['user_phone'] as String?,
  userSummary: json['user_summary'] as String?,
);

Map<String, dynamic> _$SendApplicationRequestToJson(
  _SendApplicationRequest instance,
) => <String, dynamic>{
  'user_id': instance.userId,
  'job_id': instance.jobId,
  'variant_id': instance.variantId,
  'user_name': instance.userName,
  'user_email': instance.userEmail,
  'user_phone': instance.userPhone,
  'user_summary': instance.userSummary,
};

_ApplicationStatus _$ApplicationStatusFromJson(Map<String, dynamic> json) =>
    _ApplicationStatus(
      status: json['status'] as String,
      sentAt: json['sent_at'] == null
          ? null
          : DateTime.parse(json['sent_at'] as String),
      replyCount: (json['reply_count'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$ApplicationStatusToJson(_ApplicationStatus instance) =>
    <String, dynamic>{
      'status': instance.status,
      'sent_at': instance.sentAt?.toIso8601String(),
      'reply_count': instance.replyCount,
    };
