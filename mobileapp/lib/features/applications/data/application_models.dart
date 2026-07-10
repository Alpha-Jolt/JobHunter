import 'package:freezed_annotation/freezed_annotation.dart';

part 'application_models.freezed.dart';
part 'application_models.g.dart';

@freezed
abstract class ApplicationRecord with _$ApplicationRecord {
  const factory ApplicationRecord({
    @JsonKey(name: 'application_id') required String applicationId,
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'job_id') required String jobId,
    @JsonKey(name: 'resume_variant_id') required String resumeVariantId,

    /// Values: sent, replied, interview_scheduled, rejected, ghosted
    @Default('sent') String status,
    @JsonKey(name: 'sent_at') DateTime? sentAt,
    @JsonKey(name: 'reply_count') @Default(0) int replyCount,
    @JsonKey(name: 'thread_id') String? threadId,
    @JsonKey(name: 'job_title') String? jobTitle,
    @JsonKey(name: 'company_name') String? companyName,
  }) = _ApplicationRecord;

  factory ApplicationRecord.fromJson(Map<String, dynamic> json) =>
      _$ApplicationRecordFromJson(json);
}

@freezed
abstract class SentTodayResponse with _$SentTodayResponse {
  const factory SentTodayResponse({
    required int count,
    required List<ApplicationRecord> applications,
  }) = _SentTodayResponse;

  factory SentTodayResponse.fromJson(Map<String, dynamic> json) =>
      _$SentTodayResponseFromJson(json);
}

@freezed
abstract class SendApplicationRequest with _$SendApplicationRequest {
  const factory SendApplicationRequest({
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'job_id') required String jobId,
    @JsonKey(name: 'variant_id') required String variantId,
    @JsonKey(name: 'user_name') required String userName,
    @JsonKey(name: 'user_email') required String userEmail,
    @JsonKey(name: 'user_phone') String? userPhone,
    @JsonKey(name: 'user_summary') String? userSummary,
  }) = _SendApplicationRequest;

  factory SendApplicationRequest.fromJson(Map<String, dynamic> json) =>
      _$SendApplicationRequestFromJson(json);
}

@freezed
abstract class ApplicationStatus with _$ApplicationStatus {
  const factory ApplicationStatus({
    required String status,
    @JsonKey(name: 'sent_at') DateTime? sentAt,
    @JsonKey(name: 'reply_count') @Default(0) int replyCount,
  }) = _ApplicationStatus;

  factory ApplicationStatus.fromJson(Map<String, dynamic> json) =>
      _$ApplicationStatusFromJson(json);
}
